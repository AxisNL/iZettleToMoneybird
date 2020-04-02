import configparser
import datetime
import decimal
import os
import urllib
import requests
import json
import logging

# default verbosity, will be overwritten by main class
flagVerbose = False

config = configparser.ConfigParser()
config.read('etc/izettle2moneybird.conf')

tokenMoneyBird = config['Moneybird']['Token']
administratie_id = config['Moneybird']['administratie_id']
izettle_contact_id = config['Moneybird']['izettle_contact_id']
grootboekrekening_id_bankkosten = config['Moneybird']['grootboekrekening_id_bankkosten']
taxrate_id_inkoop_geen_btw = config['Moneybird']['taxrate_id_inkoop_geen_btw']
grootboekrekening_id_kruisposten = config['Moneybird']['grootboekrekening_id_kruisposten']
rekening_id_izettle = config['Moneybird']['rekening_id_izettle']

store_contacts = os.path.join("var", 'moneybird_contacts.json')
store_financial_accounts = os.path.join("var", 'moneybird_financial_accounts.json')
store_ledger_accounts = os.path.join("var", 'moneybird_ledger_accounts.json')
store_financial_mutations = os.path.join("var", 'moneybird_financial_mutations.json')
store_sales_invoices = os.path.join("var", 'moneybird_sales_invoices.json')
store_purchase_invoices = os.path.join("var", 'moneybird_purchase_invoices.json')
store_tax_rates = os.path.join("var", 'moneybird_tax_rates.json')


def LookupContactId(company_name):
    with open(store_contacts) as json_file:
        data = json.load(json_file)
    for contact in data:
        if contact['company_name'] == company_name:
            return contact['id']
    logging.error("Could not lookup contact with name '{0}' (watch out, case sensitive!)".format(company_name))
    exit(1)


def LookupLedgerAccountId(name):
    with open(store_ledger_accounts) as json_file:
        data = json.load(json_file)
    for ledger_account in data:
        if ledger_account['name'] == name:
            return ledger_account['id']
    logging.error("Could not lookup ledger account with name '{0}' (watch out, case sensitive!)".format(name))
    exit(1)


def LookupTaxrateIdPurchase(percentage):
    with open(store_tax_rates) as json_file:
        data = json.load(json_file)
    for tax_rate in data:
        if tax_rate["tax_rate_type"] == "purchase_invoice":
            if tax_rate['percentage'] == percentage:
                return tax_rate['id']
    logging.error("Could not lookup tax rate with percentage '{0}' (watch out, case sensitive!)".format(percentage))
    exit(1)

def LookupTaxrateIdSales(percentage):
    with open(store_tax_rates) as json_file:
        data = json.load(json_file)
    for tax_rate in data:
        if tax_rate["tax_rate_type"] == "sales_invoice":
            if tax_rate['percentage'] == percentage:
                return tax_rate['id']
    logging.error("Could not lookup tax rate with percentage '{0}' (watch out, case sensitive!)".format(percentage))
    exit(1)

def DownloadContacts():
    contacts = []
    per_page = 100
    count = 1
    continueloop = True
    while continueloop:
        url = "https://moneybird.com/api/v2/{0}/contacts.json?page={1}&per_page={2}".format(administratie_id, count,
                                                                                            per_page)
        o = MakeGetRequest(url)
        for contact in o:
            contacts.append(contact)
        if len(o) < per_page:
            continueloop = False
        count = count + 1

    with open(store_contacts, 'w') as outfile:
        json.dump(contacts, outfile, indent=4, sort_keys=True)
    logging.info('Downloaded Moneybird contacts ({0} items)'.format(len(contacts)))


def DownloadFinancialAccounts():
    url = "https://moneybird.com/api/v2/{0}/financial_accounts.json".format(administratie_id)
    o = MakeGetRequest(url)

    with open(store_financial_accounts, 'w') as outfile:
        json.dump(o, outfile, indent=4, sort_keys=True)
    logging.info('Downloaded Moneybird financial accounts ({0} items)'.format(len(o)))


def DownloadLedgerAccounts():
    url = "https://moneybird.com/api/v2/{0}/ledger_accounts.json".format(administratie_id)
    o = MakeGetRequest(url)

    with open(store_ledger_accounts, 'w') as outfile:
        json.dump(o, outfile, indent=4, sort_keys=True)
    logging.info('Downloaded Moneybird ledger accounts ({0} items)'.format(len(o)))


def DownloadTaxRates():
    url = "https://moneybird.com/api/v2/{0}/tax_rates.json".format(administratie_id)
    o = MakeGetRequest(url)

    with open(store_tax_rates, 'w') as outfile:
        json.dump(o, outfile, indent=4, sort_keys=True)
    logging.info('Downloaded Moneybird tax rates ({0} items)'.format(len(o)))


def DownloadFinanancialMutations(startdate, enddate):
    startdatestring = startdate.strftime("%Y%m%d")
    enddatestring = enddate.strftime("%Y%m%d")
    fms = []
    per_page = 100
    count = 1
    continueloop = True
    while continueloop:
        url = "https://moneybird.com/api/v2/{0}/financial_mutations.json?filter=period%3A{1}..{2}&page={3}&per_page={4}".format(
            administratie_id, startdatestring, enddatestring, count, per_page)
        o = MakeGetRequest(url)
        for fm in o:
            fms.append(fm)
        if len(o) < per_page:
            continueloop = False
        count = count + 1

    with open(store_financial_mutations, 'w') as outfile:
        json.dump(fms, outfile, indent=4, sort_keys=True)
    logging.info('Downloaded Moneybird financial mutations ({0} items)'.format(len(fms)))


def DownloadSalesInvoices(startdate, enddate):
    startdatestring = startdate.strftime("%Y%m%d")
    enddatestring = enddate.strftime("%Y%m%d")
    salesinvoices = []
    per_page = 100
    count = 1
    continueloop = True
    while continueloop:
        url = "https://moneybird.com/api/v2/{0}/sales_invoices.json?filter=period%3A{1}..{2}&page={3}&per_page={4}".format(
            administratie_id, startdatestring, enddatestring, count, per_page)
        o = MakeGetRequest(url)
        for salesinvoice in o:
            salesinvoices.append(salesinvoice)
        if len(o) < per_page:
            continueloop = False
        count = count + 1

    with open(store_sales_invoices, 'w') as outfile:
        json.dump(salesinvoices, outfile, indent=4, sort_keys=True)
    logging.info('Downloaded Moneybird sales invoices ({0} items)'.format(len(salesinvoices)))


def GetSalesInvoices():
    with open(store_sales_invoices) as json_file:
        data = json.load(json_file)
    return data


def DownloadPurchaseInvoices(startdate, enddate):
    startdatestring = startdate.strftime("%Y%m%d")
    enddatestring = enddate.strftime("%Y%m%d")
    purchaseinvoices = []
    per_page = 100
    count = 1
    continueloop = True
    while continueloop:
        url = "https://moneybird.com/api/v2/{0}/documents/purchase_invoices.json?filter=period%3A{1}..{2}&page={3}&per_page={4}".format(
            administratie_id, startdatestring, enddatestring, count, per_page)
        o = MakeGetRequest(url)
        for purchaseinvoice in o:
            purchaseinvoices.append(purchaseinvoice)
        if len(o) < per_page:
            continueloop = False
        count = count + 1

    with open(store_purchase_invoices, 'w') as outfile:
        json.dump(purchaseinvoices, outfile, indent=4, sort_keys=True)
    logging.info('Downloaded Moneybird purchase invoices ({0} items)'.format(len(purchaseinvoices)))


def AddFinancialStatementAndMutation(reference, transactioncode, timestamp, amount_dec):
    if transactioncode == 'PAYOUT':
        amount_dec = 0 - amount_dec
    if transactioncode == 'CARD_PAYMENT_FEE':
        amount_dec = 0 - amount_dec

    # first, lets check if the mutation already exists:
    mutations = GetFinanancialMutationsForDate(timestamp)
    flagMutationFound = False
    for mutation in mutations:
        if mutation['message'] == reference:
            flagMutationFound = True

    if flagMutationFound:
        print("Financial statement/mutation already exists, not creating ({0})".format(reference))
        return None
    else:

        statement = {
            "financial_statement":
                {
                    "reference": reference,
                    "financial_account_id": rekening_id_izettle,
                    "financial_mutations_attributes":
                        {
                            "1": {
                                "date": timestamp.strftime('%Y-%m-%d'),
                                "message": reference,
                                "amount": "{0:f}".format(amount_dec)}
                        }
                }
        }

        url = "https://moneybird.com/api/v2/{0}/financial_statements.json".format(administratie_id)
        statementpost = MakePostRequest(url, statement)

        financial_mutation_id = statementpost['financial_mutations'][0]['id']

        print("Statement created. ({0})".format(reference))

        return financial_mutation_id


def LinkPayout(mutation_id, amount_dec):
    link = {
        "booking_type": "LedgerAccount",
        "booking_id": grootboekrekening_id_kruisposten,
        "price_base": "{0:f}".format(amount_dec)
    }
    url = "https://moneybird.com/api/v2/{0}/financial_mutations/{1}/link_booking.json".format(administratie_id,
                                                                                              mutation_id)
    MakePatchRequest(url, link)
    print("Linked payout to bank account")


def LinkSalesInvoice(mutation_id, timestamp, trans_orig_uuid, amount_dec):
    salesinvoices = GetSalesInvoicesForDate(timestamp)
    salesinvoice_id = -1

    for salesinvoice in salesinvoices:
        if trans_orig_uuid in salesinvoice['reference']:
            salesinvoice_id = salesinvoice['id']

    if salesinvoice_id == -1:
        print("Could not find a sales invoice to go with this transaction, not linking..")
    else:
        link = {
            "booking_type": "SalesInvoice",
            "booking_id": salesinvoice_id,
            "price_base": "{0:f}".format(amount_dec)
        }
        url = "https://moneybird.com/api/v2/{0}/financial_mutations/{1}/link_booking.json".format(administratie_id,
                                                                                                  mutation_id)
        MakePatchRequest(url, link)
        print("Linked transaction for sales invoice")


def MakeNegative(number):
    if number > 0:
        number = 0 - number
    return number


def LinkPurchaseInvoice(mutation_id, timestamp, trans_orig_uuid, amount_dec):
    purchaseinvoices = GetPurchaseInvoicesForDate(timestamp)
    purchaseinvoice_id = -1

    for purchaseinvoice in purchaseinvoices:
        if trans_orig_uuid in purchaseinvoice['reference']:
            purchaseinvoice_id = purchaseinvoice['id']

    if purchaseinvoice_id == -1:
        print("Could not find a purchase invoice to go with this transaction, not linking..")
    else:
        link = {
            "booking_type": "Document",
            "booking_id": purchaseinvoice_id,
            "price_base": "{0:f}".format(amount_dec)
        }
        url = "https://moneybird.com/api/v2/{0}/financial_mutations/{1}/link_booking.json".format(administratie_id,
                                                                                                  mutation_id)
        MakePatchRequest(url, link)
        print("Linked transaction for purchase invoice")


def AddSalesInvoice(reference, invoice_date, products):
    details_attributes = []
    for product in products:
        details_attribute = {
            "description": product['description'],
            "price": "{0:f}".format(product['price']),
            "tax_rate_id": LookupTaxrateId(product['tax_rate']),
            "ledger_account_id": LookupLedgerAccountId('Omzet')
        }
        details_attributes.append(details_attribute)

    postObject = {"sales_invoice":
                      {"reference": reference,
                       "invoice_date": invoice_date.isoformat(),
                       "contact_id": LookupContactId(config['Moneybird']['contact_passant']),
                       "details_attributes": details_attributes,
                       "prices_are_incl_tax": True
                       }
                  }
    url = "https://moneybird.com/api/v2/{0}/sales_invoices".format(administratie_id)
    invoicepost = MakePostRequest(url, postObject)
    invoiceid = invoicepost['id']
    print("Sales invoice '{0}' created".format(sales_reference))
    return invoiceid


def SendInvoice(invoiceid):
    url = "https://moneybird.com/api/v2/{0}/sales_invoices/{1}/send_invoice.json".format(administratie_id, invoiceid)
    postObject = {"sales_invoice_sending":
                      {"delivery_method": "Manual"
                       }
                  }
    MakePatchRequest(url, postObject)
    print("Sales invoice marked as sent")


def AddPurchaseInvoice(purchase_id, invoice_date, prijs_incl_decimal):
    global passant_id
    global administratie_id

    flagPurchaseInvoiceExists = False
    existingPurchaseInvoices = GetPurchaseInvoicesForDate(invoice_date)
    purchase_reference = "Izettle inkoop {0}".format(purchase_id)
    for invoice in existingPurchaseInvoices:
        if invoice['reference'] == purchase_reference:
            flagPurchaseInvoiceExists = True

    if flagPurchaseInvoiceExists:
        print("Purchase invoice '{0}' already exists, not creating".format(purchase_reference))
    else:
        postObject = {"purchase_invoice":
                          {"reference": purchase_reference,
                           "date": invoice_date.isoformat(),
                           "contact_id": izettle_contact_id,
                           "details_attributes": [
                               {
                                   "description": "Administratiekosten bij pintransactie",
                                   "price": "{0:f}".format(prijs_incl_decimal),
                                   "ledger_account_id": grootboekrekening_id_bankkosten,
                                   "tax_rate_id": taxrate_id_inkoop_geen_btw
                               }
                           ],
                           "prices_are_incl_tax": True
                           }
                      }
        url = "https://moneybird.com/api/v2/{0}/documents/purchase_invoices.json".format(administratie_id)
        MakePostRequest(url, postObject)
        print("Purchase invoice '{0}' created".format(purchase_reference))


#
# def GetSalesInvoicesForDate(datetosearch):
#     datestring = datetosearch.strftime("%Y%m%d")
#     url = "https://moneybird.com/api/v2/{0}/sales_invoices.json?filter=period%3A{1}..{1}".format(
#         administratie_id, datestring)
#     o = MakeGetRequest(url)
#     return o

#
# def GetSalesInvoiceByRef(reference):
#     reference = "reference:{0}".format(reference)
#     reference_urlsafe = urllib.parse.quote(reference)
#     url = "https://moneybird.com/api/v2/{0}/sales_invoices.json?filter={1}".format(
#         administratie_id, reference_urlsafe)
#     print(url)
#     o = MakeGetRequest(url)
#     return o
#
#
# def GetPurchaseInvoicesForDate(datetosearch):
#     datestring = datetosearch.strftime("%Y%m%d")
#     url = "https://moneybird.com/api/v2/{0}/documents/purchase_invoices.json?filter=period%3A{1}..{1}".format(
#         administratie_id, datestring)
#     o = MakeGetRequest(url)
#     return o


def MakeGetRequest(url):
    # print("DEBUG: get {0}".format(url))
    global tokenMoneyBird

    headers = {
        "authorization": "Bearer {0}".format(tokenMoneyBird)
    }
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        return r.json()
    else:
        print("Error: {0} {1}".format(r.status_code, r.content))
        exit(1)


def MakePostRequest(url, postObj):
    # print("DEBUG: post {0}".format(url))
    global tokenMoneyBird

    headers = {
        "authorization": "Bearer {0}".format(tokenMoneyBird)
    }
    r = requests.post(url, json=postObj, headers=headers)
    if r.status_code == 200:
        return r.json()
    if r.status_code == 201:
        return r.json()
    if r.status_code > 299:
        print("Error: {0}".format(r.content))
        exit(1)


def MakePatchRequest(url, postObj):
    global tokenMoneyBird

    headers = {
        "authorization": "Bearer {0}".format(tokenMoneyBird)
    }
    r = requests.patch(url, json=postObj, headers=headers)
    result = r.json()
    return result

# this code will only be run if this script is run directly
# if __name__ == '__main__':
#     print(json.dumps(GetInvoices(), indent=2, sort_keys=True))
