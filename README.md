# Election Scraper

Třetí projekt na Python Akademii od Engeta

## Popis projektu
Tento program scrapuje výsledky parlamentních voleb z roku 2017.
Na základě zadaného URL odkazu na výsledky ve vybraném okrese stahne výsledky ve všech obcích vybraného okresu a zapíše je do CSV souboru.




## Instalace knihoven
Potřebné knihovny jsou uloženy v souboru requirements.txt. Jejich instalaci doporučuji v novém virtuálním prostředí, například pomocí Vámi používaného IDE.



## Spuštění projektu
Spuštění programu election_scraper_final.py v rámci příkazového řádku vyžaduje dva povinné argumenty, takto:

`
python election_scraper_final.py <url-na-vybrany-okres> <nazev-vysledneho-souboru>
`

Následně se stahnou výsledky voleb ve vybraném okrese a uloží do Vámi pojmenovaného souboru CSV.



## Ukázka projektu
Výsledky hlasování pro okres Hodonín.

1. argument ` https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=11&xnumnuts=6205 `
2. argument ` vysledky_hodonin.csv `

#### Spuštění programu

```
python election_scraper_final.py "https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=11&xnumnuts=6205" "vysledky_hodonin.csv"
```

#### Průběh stahování
```
>Získány kódy obcí
>Získány názvy obcí
>Získány URL odkazy na výsledky v jednotlivých městech
>Záhlaví vytvořeno
>Stahuji data...
>>>Získána všechna data!
>Zapisuji data do vysledky_hodonin.csv
Data byla úspěšně zapsána do souboru: vysledky_hodonin.csv
```

#### Ukázka výstupu
```csv
Kód obce,Název obce,Voliči v seznamu,Vydané obálky,Platné hlasy,Občanská demokratická strana...
586030,Archlebov,752,416,415,25...
586048,Blatnice pod Svatým Antonínkem,1 733,1 066,1 055,101...
586056,Blatnička,356,239,238,16...

