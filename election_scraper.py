from bs4 import BeautifulSoup as bs
from requests import get
import csv
import sys

argument_1 = "https://www.volby.cz/pls/ps2017nss/ps3?xjazyk=CZ"  # URL na všechny obce okresu
odpoved = get(argument_1)
odpoved.encoding = 'utf-8'  # nastavení kódování odpovědi
pars_odpoved = bs(odpoved.text, features="html.parser")

zahlavi_0 = ["Kód obce", "Název obce", "Voliči v seznamu", "Vydané obálky", "Platné hlasy"]


def ziskej_kody_obci(pars_html):
    all_td = pars_html.find_all("td", {"class": "cislo"})
    kody_obci = [cislo_obce.get_text() for cislo_obce in all_td]
    print("Získány kódy obcí")
    return kody_obci


def ziskej_nazvy_obci(pars_html):
    all_td = pars_html.find_all("td", {"class": "overflow_name"})
    nazvy_obci = [nazev_obce.get_text() for nazev_obce in all_td]
    print("Získány názvy obcí")
    return nazvy_obci


def ziskej_url_obci(pars_html):
    """
    Funkce vrací list URL odkazů na všechny obce
    :param pars_html: parsované HTML z 1. argumentu
    :return: list URL odkazů
    """
    urls = []
    for td in pars_html.find_all('td', class_='cislo'):
        link = td.find('a', href=True)
        if link and link['href'].startswith("ps311"):
            urls.append(f"https://www.volby.cz/pls/ps2017nss/{link['href']}")
    print("získány url odkazy na výsledky v jednotlivých městech")
    return urls


def vytvor_zahlavi_csv(url):
    """
    Funkce slouží k vytvoření záhlaví výsledného .csv souboru.
    :param url: string, URL adresa webu, kde jsou výsledky voleb
    :return: Sloučený list předdefinovaného záklaví_0 a scrapnutých názvů stran
    """
    odpoved_url = get(url)
    odpoved_url.encoding = 'utf-8'
    pars_odpoved_url = bs(odpoved_url.text, features="html.parser")
    vsechny_td_headers = pars_odpoved_url.find_all("td", headers=["t1sa1 t1sb2", "t2sa1 t2sb2"])
    nazvy_stran = []
    for data in vsechny_td_headers:
        text = data.get_text()
        if text == "-":
            continue
        nazvy_stran.append(text)
    print("Záhlaví vytvořeno")
    return zahlavi_0 + nazvy_stran


def ziskej_radek(url, kod_obce, nazev_obce):
    odpoved_radek = get(url)
    odpoved_radek.encoding = 'utf-8'
    pars_odpoved_radek = bs(odpoved_radek.text, features="html.parser")
    vsechny_td_headers = pars_odpoved_radek.find_all("td", headers=["sa2", "sa3", "sa6", "t1sa2 t1sb3", "t2sa2 t2sb3"])
    jeden_radek = []
    for data in vsechny_td_headers:
        text = data.get_text()
        if text == "-":
            continue
        jeden_radek.append(text)
    return [kod_obce, nazev_obce] + jeden_radek


def ziskej_vsechny_radky(url_obci, kody_obci, nazvy_obci):
    radky = []
    for i in range(len(url_obci)):
        radky.append(ziskej_radek(url_obci[i], kody_obci[i], nazvy_obci[i]))
    print("Získány všechny řádky")
    return radky


def zapis_csv(zahlavi, radky, soubor):
    print(f"Zapisuji data do {soubor}")
    with open(soubor, mode="w", newline="", encoding="utf-8") as soubor_open:
        zapisovac = csv.writer(soubor_open)
        zapisovac.writerow(zahlavi)
        zapisovac.writerows(radky)


def main():
    kody_obci = ziskej_kody_obci(pars_odpoved)
    nazvy_obci = ziskej_nazvy_obci(pars_odpoved)
    url_obci = ziskej_url_obci(pars_odpoved)
    if url_obci:
        zahlavi = vytvor_zahlavi_csv(url_obci[0])
        data_radky = ziskej_vsechny_radky(url_obci, kody_obci, nazvy_obci)
        zapis_csv(zahlavi, data_radky, "vysledky_voleb.csv")
    else:
        print("Žádné URL nebyly nalezeny.")


if __name__ == "__main__":
    main()
    print(f"Data byla úspěšně zapsána do 'vysledky_voleb.csv'")