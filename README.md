# iZettleToMoneybird
This module contains a python program to sync iZettle data to Moneybird

The rest of the documentation is in Dutch, because 99% of the clients using this script will be Dutch.

Dit script wordt geleverd as-is, en is bedoeld voor de hobby-programmeur die data van zijn iZettle account (pinsysteem) 
naar Moneybird (boekhoudpakket) wil krijgen. Enige technische kennis is vereist.

Dit script verbindt naar de API's van iZettle en Moneybird, en download eerst alle relevante informatie (naar de /var
folder). Vervolgens wordt de data geanalyseerd en de benodigde boekingen in Moneybird toegepast.

### Installatie
Kloon de repo, that's it. Zorg dat je Python 3 hebt en installeer de requirements. Je kunt ook een GUI gebruiken 
zoals PyCharm om makkelijker packages te installeren.

### Configuratie

Kopieer of hernoem in de /etc folder izettle2moneybird.conf.dist naar izettle2moneybird.conf en vul je eigen gegevens 
in. Je moneybird administratieid kun je uit de url-balk halen als je in je administratie zit. Contactname en rekeningnamen
zul je op moeten zoeken.

### Proces

We downloaden eerst bij iZettle alle purchases en transactions. Iedere purchase is een verkoopfactuur, van de winkel 
naar de klant, in Moneybird een sale/verkoop genoemd. Iedere purchase bevat een of meerdere producten met elk een 
eigen BTW-tarief. Iedere purchase heeft ook een betaling met unieke id. Op dit moment ondersteunt het script enkel
purchases met 1 betaling.

In de iZettle transactions vinden we drie soorten transacties:
* CARD_PAYMENT: een betaling van de bovengenoemde verkoop (geld gaat van klant naar iZettle);
* CARD_PAYMENT_FEE: kosten die door iZettle in rekening wordt gebracht (geld gaat van winkel naar iZettle)
* PAYOUT: een overboeking van je iZettle account naar je bankrekening.
Er zijn er nog veel meer mogelijkheden (zie de iZettle documentatie), maar die worden op dit moment nog niet ondersteund.

In Moneybird zullen we een aantal zaken moeten hebben, die je zelf zult moeten aanmaken:

* Een aparte 'bankrekening' waarop de iZettle transacties plaatsvinden.
* Een contactpersoon voor de pinklanten, bijvoorbeeld 'Passant'. Mocht het nodig zijn zou je achteraf nog contactpersonen
aan kunnen passen. 
* Een contactpersoon voor de leverancier iZettle, waar de administratiekosten aan betaald worden.
* Een rekening waarop de iZettle-kosten worden geboekt (kan bestaande categorie 'Bankkosten' zijn)
* Een rekening waarop de omzet geboekt wordt (kan bestaande categorie 'omzet' zijn)

Vervolgens dient het script voor iedere purchase in iZettle een verkoopfactuur aan te maken gemaakt (klant koopt iets 
bij de winkel). Bij iedere verkoop brengt iZettle administratiekosten in rekening. Hiervoor maken we een inkoopfactuur 
aan (winkel koopt iets bij iZettle). Deze transacties vinden allemaal plaats op de bankrekening 'iZettle', en deze 
betalingen moeten natuurlijk ook gekoppeld worden aan de in- en verkoopfacturen.

Daarnaast wordt er ook nog eens in de zoveel tijd geld overgeboekt van de iZettle rekening naar de bankrekening. Moneybird
ondersteunt geen directe overboekingen tussen rekeningen, hiervoor is als tussenrekening bijvoorbeeld de bestaande 
rekening kruisposten te gebruiken. 

Dit script boekt automatisch de afschrijvingen van je iZettle account naar kruisposten, maar je moet dan nog zelf zorgen
dat je binnenkomende bedragen op je echte bankrekening ook op de categorie kruisposten geboekt worden. Dit kun je
automatiseren in Moneybird. Als het goed is zou het saldo van de rekening kruisposten op 0 moeten blijven!


### Uitvoeren

Je kunt het script bijvoorbeeld uitvoeren met:

    python izettle2moneybird.py
    
Je kunt nog specifieker zijn. Met de optie -n bijvoorbeeld, zorg je dat het script alleen in read-only modus 
draait en dus eerst laat zien wat er zou gebeuren, maar het past verder niets aan. De optie -v laat meer zien 
op de command line. Je kunt ook een handmatige begin- en einddatum opgeven.


    usage: izettle2moneybird.py [-h] [-n] [-v] [--startdate STARTDATESTRING]
                    [--enddate ENDDATESTRING]
    
    Sync iZettle to your Moneybird account.
    
    optional arguments:
      -h, --help            show this help message and exit
      -n, --noop            Only read, do not really change anything
      -v, --verbose         Print extra output
      --startdate STARTDATESTRING
                            The date to start on, in the example format 31122019
                            for dec 31st, 2019. If not specified, it will be
                            yesterday.
      --enddate ENDDATESTRING
                            The date to start on, in the example format 31122019
                            for dec 31st, 2019. If not specified, it will be
                            tomorrow.
                            

Het idee is om het script iedere dag met een task scheduler te draaien. Het script haalt data voor meerdere dagen 
op, omdat soms data aan elkaar gelinkt dient te worden van verschillende dagen. De betaling en een boeking kunnen
bijvoorbeeld wat uit elkaar liggen. 

Het script kan onbeperkt worden uitgevoerd en zal alleen zaken wijzigen die daadwerkelijk gewijzigd dienen te worden. 
Je kunt dus bijvoorbeeld bij problemen data uit Moneybird verwijderen, en daarna het script opnieuw uitvoeren om de 
data opnieuw in Moneybird te zetten.

### Troubleshooting

Er wordt een logfile weggeschreven in /log

### Changelog

| datum    | aut | opmerking              |
|----------|-----|------------------------|
| 20200402 | AH  | Complete rewrite klaar |
| 20200401 | AH  | Begin met rewrite      |
| 201906XX | AH  | Eerste versie          |