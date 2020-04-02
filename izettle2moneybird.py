import configparser
import decimal
import json
import os
import sys
import dateutil.parser
import datetime
import argparse
import logging
import logging.handlers
from lib import iz, mb, log

parser = argparse.ArgumentParser(description='Sync iZettle to your Moneybird account.')
parser.add_argument('-n', '--noop', dest='noop', action='store_true', help="Only read, do not really change anything")
parser.add_argument('-v', '--verbose', dest='verbose', action='store_true', help="Print extra output")
parser.add_argument('--startdate', dest='startdatestring', type=str, help="The date to start on, in the "
                                                                          "example format 31122019 for dec "
                                                                          "31st, 2019. If not specified, it "
                                                                          "will be yesterday.")
parser.add_argument('--enddate', dest='enddatestring', type=str, help="The date to start on, in the "
                                                                      "example format 31122019 for dec "
                                                                      "31st, 2019. If not specified, it "
                                                                      "will be tomorrow.")
args = parser.parse_args()
flagNoop = args.noop
flagVerbose = args.verbose

iz.flagVerbose = flagVerbose
mb.flagVerbose = flagVerbose

######################################
# CONFIGURE LOGGING
# ####################################
logger = log.logger(flagVerbose)

######################################
# CHECK REQUIREMENTS
# ####################################

if sys.version_info <= (3, 6, 0):
    logger.critical("You are running Python version {0}, but ony >= 3.6 is tested".format(sys.version_info))
    exit(1)

######################################
# PARSING INPUT
# ####################################

# SET THE DEFAULT START AND END DATES
date = datetime.datetime.today()
startDate = (date + datetime.timedelta(days=-1))
endDate = (date + datetime.timedelta(days=1))

if args.startdatestring is not None:
    try:
        startDate = datetime.datetime.strptime(args.startdatestring, "%d%m%Y").date()
    except ValueError as err:
        logger.error("Could not convert '{0}' to date: {1}".format(startDate, err))
        exit(1)

if flagVerbose:
    logger.info("Starting date: {0}".format(startDate))

if args.enddatestring is not None:
    try:
        endDate = datetime.datetime.strptime(args.enddatestring, "%d%m%Y").date()
    except ValueError as err:
        logger.error("Could not convert '{0}' to date: {1}".format(startDate, err))
        exit(1)

if flagVerbose:
    logger.info("Ending date: {0}".format(endDate))

######################################
# GET THE PARAMETERS FROM THE CONFIG FILE
# ####################################
config = configparser.ConfigParser()
config.read('etc/izettle2moneybird.conf')

######################################
# DOWNLOAD ALL REQUIRED DATA
# ####################################
iz.DownloadTransactions(startDate, endDate)
iz.DownloadPurchasesPurchases(startDate, endDate)
# mb.DownloadContacts()
# mb.DownloadFinancialAccounts()
# mb.DownloadLedgerAccounts()
# mb.DownloadTaxRates()
mb.DownloadFinanancialMutations(startDate, endDate)
mb.DownloadSalesInvoices(startDate, endDate)
mb.DownloadPurchaseInvoices(startDate, endDate)

######################################
# PROCESS
# ####################################

# Compare the iZettle purchases with the Moneybird purchases
logger.info("Processing the iZettle purchases")

for izPurchase in iz.GetPurchases():
    purchaseNumber = izPurchase['purchaseNumber']

    if len(izPurchase['payments']) == 0:
        logger.error("This purchase (purchaseNumber {0}) has no payments, not supported".format(purchaseNumber))
    if len(izPurchase['payments']) > 1:
        logger.error(
            "This purchase (purchaseNumber {0}) has more than one payment, not supported".format(purchaseNumber))

    reference = "Izettle purchase {0}".format(purchaseNumber)
    logger.info("Processing the iZettle purchase {0}".format(purchaseNumber))
    flagFound = False
    # vergelijk met de Moneybird facturen
    for mbFactuur in mb.GetSalesInvoices():
        if mbFactuur['reference'] == reference:
            flagFound = True

    if not flagFound:
        # Voeg de invoice toe
        if flagNoop:
            logger.info("Sales invoice with reference '{0}' should be added, but I won't.".format(reference))
        else:
            timestamp = dateutil.parser.parse(izPurchase['timestamp'])
            izProducts = izPurchase['products']
            details_attributes = []
            for izProduct in izProducts:
                totalproductcents = izProduct['unitPrice'] * izProducts['quantity']
                totalproductamount = decimal.Decimal(totalproductcents / 100.0)
                products = {"description": izProduct['description'],
                            "price": totalproductamount,
                            "tax_rate": izProduct['vatPercentage']
                            }
            mb.AddSalesInvoice(reference, timestamp, products)

exit(1)

# WALK THROUGH ALL THE TRANSACTIONS AND CREATE BANK STATEMENTS FOR THE IZETTLE ACCOUNT

for transaction in transactions:
    print(json.dumps(transaction, indent=2))

    transactioncode = transaction['originatorTransactionType']
    trans_orig_uuid = transaction['originatingTransactionUuid']
    reference = "IZETTLE_{0}_{1}_{2}".format(transactioncode, transaction['timestamp'], trans_orig_uuid)
    amount_cents = int(transaction['amount'])
    # always get a positive number to work with
    if amount_cents < 0:
        amount_cents = 0 - amount_cents
    amount_dec = decimal.Decimal(amount_cents / 100.0)

    timestamp = dateutil.parser.parse(transaction['timestamp'])

    print("-------------------")
    print("Processing transaction {0}".format(reference))

    mutation_id = mb.AddFinancialStatementAndMutation(reference, transactioncode, timestamp, amount_dec)
    key = "{0}_{1}".format(transactioncode, trans_orig_uuid)
    object_ids_mutations[key] = mutation_id

    # LinkTransaction(financial_mutation_id, transactioncode, timestamp, amount_dec)
exit(1)
# WALK THROUGH ALL THE TRANSACTIONS AND CREATE SALES AND PURCHASE STATEMENTS

for transaction in transactions:
    if transactioncode not in ['CARD_PAYMENT', 'CARD_PAYMENT_FEE', 'PAYOUT']:
        print("Transaction code {0} not handled!".format(transactioncode))
        exit(1)

    transactioncode = transaction['originatorTransactionType']
    trans_orig_uuid = transaction['originatingTransactionUuid']
    reference = "IZETTLE_{0}_{1}_{2}".format(transactioncode, transaction['timestamp'], trans_orig_uuid)

    print('-------------------')

    amount_cents = transaction['amount']
    # always get a positive number to work with
    if amount_cents < 0:
        amount_cents = 0 - amount_cents

    amount_dec = decimal.Decimal(amount_cents / 100.0)
    timestamp = dateutil.parser.parse(transaction['timestamp'])

    if transactioncode == 'CARD_PAYMENT_FEE':
        print("Analyzing purchase with id {0}".format(trans_orig_uuid))
        print("  Date: {0}".format(timestamp))
        print("  Amount: {0} cents".format(amount_cents))

        mb.AddPurchaseInvoice(trans_orig_uuid, timestamp, amount_dec)
        key = "{0}_{1}".format(transactioncode, trans_orig_uuid)
        if key in object_ids_mutations:
            mut_id = object_ids_mutations[key]
            mb.LinkPurchaseInvoice(mut_id, timestamp, trans_orig_uuid, amount_dec)

    if transactioncode == 'CARD_PAYMENT':
        print("Analyzing sale with id {0}".format(trans_orig_uuid))
        print("  Date: {0}".format(timestamp))
        print("  Amount: {0} cents".format(amount_cents))

        new_id = mb.AddSalesInvoice(trans_orig_uuid, timestamp, amount_dec)
        if not new_id is None:
            mb.SendInvoice(new_id)

        key = "{0}_{1}".format(transactioncode, trans_orig_uuid)

        if key in object_ids_mutations:
            mut_id = object_ids_mutations[key]
            mb.LinkSalesInvoice(mut_id, timestamp, trans_orig_uuid, amount_dec)

    if transactioncode == 'PAYOUT':
        print("Analyzing payout with timestamp {0}".format(timestamp))
        print("  Date: {0}".format(timestamp))
        print("  Amount: {0} cents".format(amount_cents))

        key = "{0}_{1}".format(transactioncode, trans_orig_uuid)
        if key in object_ids_mutations:
            mut_id = object_ids_mutations[key]
            mb.LinkPayout(mut_id, amount_dec)
