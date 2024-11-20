import requests
from bs4 import BeautifulSoup as bs, BeautifulSoup
from requests import get
import csv
import sys

#  kontrola počtu zadaných argumentů
if len(sys.argv) < 3:
    print("Pro správné použití programu zadej (včetně uvozovek): python election_scraper.py 'URL' 'název_souboru.csv'")
    sys.exit(1)

argument_1 = sys.argv[1]  # URL na všechny obce zvoleného okresu
argument_2 = sys.argv[2]  # název výsledného .csv souboru


def test_url_odkazu(url: str) -> BeautifulSoup:
    """
    Funkce vezme první zadaný argument, tedy url odkaz, a testuje jeho validitu
    :param url: url odkaz na webovou stránku
    :return: vrací parsovanou html stránku, pokud je URL validní; v případě erroru ukončuje program
    """
    try:  # Ověření, zda-li se jedná o validní URL odkaz
        odpoved = get(url)
        odpoved.encoding = 'utf-8'  # nastavení kódování odpovědi
        odpoved.raise_for_status()
    except requests.exceptions.MissingSchema:
        print(f">>>Neplatný URL odkaz '{url}'",
              "Ujisti se, že se skutečně jedná o odkaz na webovou stránku.",
              ">>>Ukončuji program.",
              sep="\n")
        sys.exit(1)
    except requests.exceptions.RequestException as error:
        print(f">>>Vyskytla se tato chyba: {error}",
              ">>>Je zadaný odkaz opravdu správný?",
              ">>>Ukončuji program.",
              sep="\n")
        sys.exit(1)
    pars_odpoved = bs(odpoved.text, features="html.parser")

    return pars_odpoved

#  Stálé záhlaví, které je vždy stejné
zahlavi_0 = ["Kód obce", "Název obce", "Voliči v seznamu", "Vydané obálky", "Platné hlasy"]


def ziskej_kody_obci(pars_html):
    """
    Funkce extrahuje ze zadaného URL kódy jednotlivých obcí
    :param pars_html: parsovaná html stránka s výsledkama voleb
    :return: list s kódama obcí
    """
    all_td_kody = pars_html.find_all("td", {"class": "cislo"})
    kody_obci = [cislo_obce.get_text() for cislo_obce in all_td_kody]
    if len(kody_obci) == 0: #  Kdyby selhalo extrahování a list kódů obcí byl prázdný, tak se ukončí program
        sys.exit("Nepodařilo se extrahovat kódy obcí. URL neodpovídá zadání.")
    print(">Získány kódy obcí")
    #  print(len(kody_obci))
    return kody_obci


def ziskej_nazvy_obci(pars_html):
    """
    Funkce extrahuje názvy obcí ze zadaného URL odkazu
    :param pars_html: parsovaná html stránka s výsledkama voleb
    :return: list s názvama obcí
    """
    #  Zahraničí má specifickou strukturu
    if argument_1 == "https://www.volby.cz/pls/ps2017nss/ps36?xjazyk=CZ":
        all_td_nazvy = pars_html.find_all("td", {"headers": "s3"})
        nazvy_obci = [nazev_obce.get_text() for nazev_obce in all_td_nazvy]
    #  Brno má specifickou strukturu
    elif argument_1 == "https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=11&xnumnuts=6202":
        all_td_nazvy = pars_html.find_all("td", {"headers": "t1sa1 t1sb2"})
        nazvy_obci = [nazev_obce.get_text() for nazev_obce in all_td_nazvy]
    #  Zbytek okresů funguje jednotně
    else:
        all_td_nazvy = pars_html.find_all("td", {"class": "overflow_name"})
        nazvy_obci = [nazev_obce.get_text() for nazev_obce in all_td_nazvy]
    if len(nazvy_obci) == 0: #  Kdyby selhalo extrahování a list názvů obcí byl prázdný, tak se ukončí program
        sys.exit("Nepodařilo se extrahovat názvy obcí. URL neodpovídá zadání")
    print(">Získány názvy obcí")
    #  print(len(nazvy_obci))
    return nazvy_obci


def ziskej_url_obci(pars_html):
    """
    Funkce vrací list URL odkazů na všechny obce daného okresu
    :param pars_html: parsované HTML z 1. argumentu
    :return: list URL odkazů
    """
    urls = []
    for td in pars_html.find_all('td', class_='cislo'):
        link = td.find('a', href=True)
        if link and link['href'].startswith("ps311"):
            urls.append(f"https://www.volby.cz/pls/ps2017nss/{link['href']}")
    if len(urls) == 0: # Kdyby generování URL odkazů selhalo, ukončí se program
        sys.exit("Nepodařilo se extrahovat URL na jednotlivá města ve vybraném okrese. Argument s URL odkazem neodpovídá zadání.")
    print(">Získány URL odkazy na výsledky v jednotlivých městech")
    #  print(len(urls))
    return urls


def vytvor_zahlavi_csv(url):
    """
    Funkce slouží k vytvoření kompletního záhlaví výsledného .csv souboru.
    :param url: jeden z URL na konkrétní obci, kde jsou výsledky voleb
    :return: Sloučený list předdefinovaného záklaví_0 a scrapnutých názvů stran
    """
    try:
        odpoved_url = get(url)
        odpoved_url.encoding = 'utf-8'
        pars_odpoved_url = bs(odpoved_url.text, features="html.parser")
    except requests.exceptions.RequestException as error:
        print(f"Chyba při tvorbě záhlaví: {error}",
              "Ukončuji program.",
              sep="\n")
        sys.exit(1)

    vsechny_td_headers = pars_odpoved_url.find_all("td", headers=["t1sa1 t1sb2", "t2sa1 t2sb2"])
    nazvy_stran = []
    for data in vsechny_td_headers:
        text = data.get_text()
        if text == "-":
            continue
        nazvy_stran.append(text)
    print(">Záhlaví vytvořeno")
    return zahlavi_0 + nazvy_stran


def ziskej_radek(url, kod_obce, nazev_obce):
    """
    Funkce, která z výsledků v jedné obci vytvoří řádek s daty
    :param url: jeden z URL na web obce, kde jsou výsledky voleb
    :param kod_obce: kód obce, který odpovídá <url> parametru
    :param nazev_obce: název obce, který odpovídá <url> parametru
    :return: vrací list, ve kterém jsou data jednoho řádku (výsledky v jedné obci)
    """
    try:
        odpoved_radek = get(url)
        odpoved_radek.encoding = 'utf-8'
        pars_odpoved_radek = bs(odpoved_radek.text, features="html.parser")
    except requests.exceptions.RequestException as error:
        print(f"Chyba při získávání dat: {error}",
              "Ukončuji program.",
              sep="\n")
        sys.exit(1)

    vsechny_td_headers = pars_odpoved_radek.find_all("td", headers=["sa2", "sa3", "sa6", "t1sa2 t1sb3", "t2sa2 t2sb3"])
    jeden_radek = []
    for data in vsechny_td_headers:
        text = data.get_text()
        if text == "-":
            continue
        jeden_radek.append(text)
    return [kod_obce, nazev_obce] + jeden_radek


def ziskej_vsechny_radky(url_obci, kody_obci, nazvy_obci):
    """
    Funkce, která přes vnořenou fci ziskej_radek vygeneruje všechny řádky
    :param url_obci: list vygenerovaných URL z fce ziskej_url_obci
    :param kody_obci: list kódů obcí z fce ziskej_kody_obci
    :param nazvy_obci: list kódů obcí z fce ziskej_nazvy_obci
    :return: list, jehož prvky jsou listy, jejichž data jsou kompletní výsledky voleb v jedné obci
    """
    radky = []
    for i in range(len(url_obci)):
        radky.append(ziskej_radek(url_obci[i], kody_obci[i], nazvy_obci[i]))
    print(">>>Získána všechna data!")
    return radky


def zapis_csv(zahlavi, radky, soubor):
    """
    Funkce, která zapisuje získaná data do CSV souboru
    :param zahlavi: list záhlaví, získaný z fce vytvor_zahlavi_csv
    :param radky: list řádků, získaný z fce ziskej_vsechny_radky
    :param soubor: druhý, uživatelem zadaný argument při spouštění programu
    :return: po úspěšném zápisu dat do CSV se vypíše hláška, která uživatele informuje o úspěšném zápisu dat
    """
    print(f">Zapisuji data do {soubor}")
    with open(soubor, mode="w", newline="", encoding="utf-8") as soubor_open:
        zapisovac = csv.writer(soubor_open)
        zapisovac.writerow(zahlavi)
        zapisovac.writerows(radky)
    return print(f"Data byla úspěšně zapsána do souboru: {argument_2}")


def main():
    pars_odpoved = test_url_odkazu(argument_1)
    kody_obci = ziskej_kody_obci(pars_odpoved)
    nazvy_obci = ziskej_nazvy_obci(pars_odpoved)
    url_obci = ziskej_url_obci(pars_odpoved)
    if url_obci:
        zahlavi = vytvor_zahlavi_csv(url_obci[0])
        print(">Stahuji data...")
        data_radky = ziskej_vsechny_radky(url_obci, kody_obci, nazvy_obci)
        zapis_csv(zahlavi, data_radky, argument_2)
    else:
        print("Žádné URL nebyly nalezeny.")


if __name__ == "__main__":
    main()