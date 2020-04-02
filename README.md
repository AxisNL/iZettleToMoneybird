# iZettleToMoneybird
This module contains a python program to sync iZettle data to Moneybird

The rest of the documentation is in Dutch, because 99% of the clients using this script will be Dutch.



### Installatie
Kloon de repo, that's it. Zorg dat je Python 3 hebt en installeer de requirements. Je kunt ook een GUI gebruiken 
zoals PyCharm om makkelijker packages te installeren.

### Configuratie

Kopieer of hernoem iz2mb.conf.dist naar iz2mb.conf en vul je eigen gegevens in. Je zult wellicht een boel ID's in 
Moneybird op moeten zoeken. Ga naar de betreffende rekening of contact in Moneybird, en kopieer het laatste id uit 
de URL-balk (een enkel lang getal).

### Proces

We downloaden eerst bij iZettle alle purchases en transactions. Iedere purchase is een verkoopfactuur, van de winkel 
naar de klant. Iedere purchase bevat een of meerdere producten met elk een eigen BTW-tarief. Iedere purchase heeft
ook een betaling met unieke id.

In transactions vinden we drie soorten transacties:
* CARD_PAYMENT: een betaling van de bovengenoemde purchase;
* CARD_PAYMENT_FEE: kosten die door iZettle in rekening wordt gebracht (hier maken we in Moneybird een inkoopfactuur voor aan);
* PAYOUT: een overboeking van je iZettle account naar je bankrekening.
Er zijn er nog veel meer mogelijk (zie de documentatie), maar die worden op dit moment nog niet ondersteund.

In Moneybird zullen we een aantal zaken moeten hebben, die je zelf zult moeten aanmaken:

* Een aparte 'bankrekening' waarop de iZettle transacties plaatsvinden.
* Een contactpersoon voor de pinklanten, bijvoorbeeld 'Passant'. De facturen zijn achteraf nog handmatig aan te passen naar de klant.
* Een contactpersoon voor de leverancier iZettle, waar de administratiekosten aan betaald worden.

Vervolgens dient er voor iedere purchase in iZettle een verkoopfactuur te worden aangemaakt (klant koopt iets bij de winkel).
Bij iedere verkoop brengt iZettle administratiekosten in rekening. Hiervoor maken we een inkoopfactuur aan (winkel koopt iets
bij iZettle). Deze transacties vinden allemaal plaats op de bankrekening 'iZettle', en de betalingen moeten natuurlijk ook
gekoppeld worden aan de in- en verkoopfacturen.

Daarnaast wordt er ook nog eens in de zoveel tijd geld overgeboekt van de iZettle rekening naar de bankrekening. Moneybird
ondersteunt geen directe overboekingen tussen rekeningen, hiervoor is als tussenrekening bijvoorbeeld de rekening kruisposten
te gebruiken. 

Dit script boekt automatisch de afschrijvingen van je iZettle account naar kruisposten, maar je moet dan nog zelf zorgen
dat je binnenkomende bedragen op je echte bankrekening ook vanaf de kruisposten komen. Als het goed is zou het saldo van
de rekening kruisposten op 0 moeten blijven!


### Uitvoeren

Je kunt het script bijvoorbeeld uitvoeren met:

    python izettle2moneybird.py
    
Je kunt nog specifieker zijn. Met de optie -n bijvoorbeeld, zorg je dat het script alleen in read-only modus draait en dus eerst laat zien wat er zou gebeuren, maar het past verder niets aan. Je kunt ook een handmatige begin- en einddatum opgeven.


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
                            

Het voorstel is om het script iedere dag met een task scheduler te draaien. Het script haalt data voor meerdere dagen op, omdat soms data in iZettle aan elkaar gekoppeld dient te worden welke wat dagen uit elkaar liggen.

Het script kan onbeperkt worden uitgevoerd en zal alleen zaken wijzigen die daadwerkelijk gewijzigd dienen te worden. Je kunt dus bijvoorbeeld bij problemen data uit Moneybird verwijderen, en daarna het script opnieuw uitvoeren om de data opnieuw in Moneybird te zetten.