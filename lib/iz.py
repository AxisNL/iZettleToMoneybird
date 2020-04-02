import configparser
import logging

import requests
import json
from datetime import datetime
#from lib import log

# default verbosity, will be overwritten by main class
flagVerbose = False

config = configparser.ConfigParser()
config.read('etc/izettle2moneybird.conf')
iZettleClientId = config['iZettle']['clientid']
iZettleClientSecret = config['iZettle']['clientsecret']
iZettleUserName = config['iZettle']['username']
iZettlePassword = config['iZettle']['password']

purchasesfile = "var/izettle_purchases.json"
transactionsfile = "var/izettle_transactions.json"

apitoken = {
    "token": "",
    "timestamp": datetime.min
}

#logger = log.logger(flagVerbose)


def GetToken():
    global apitoken
    global iZettleClientId
    global iZettleClientSecret
    global iZettleUserName
    global iZettlePassword

    flagTokenValid = True
    if len(apitoken['token']) == 0:
        flagTokenValid = False

    datetimeNow = datetime.today()
    tokenage_seconds = (datetimeNow - apitoken['timestamp']).total_seconds()
    if tokenage_seconds > 7200:
        flagTokenValid = False

    if not flagTokenValid:
        # the token is invalid and must be refreshed

        token_url = 'https://oauth.izettle.com/token'

        header = {
            'grant_type': 'password',
            'client_id': iZettleClientId,
            'client_secret': iZettleClientSecret,
            'username': iZettleUserName,
            'password': iZettlePassword,
            'Content-Type': 'application/json',
        }
        r = requests.post(token_url, data=header)
        data = json.loads(r.content)
        apitoken['token'] = data['access_token']
        apitoken['timestamp'] = datetimeNow

    # return the token
    return apitoken['token']


def DownloadPurchasesPurchases(datestart, dateend):
    global iZettleClientId
    global iZettleClientSecret
    global iZettleUserName
    global iZettlePassword

    izettleDate1 = datestart.strftime("%Y-%m-%d")
    izettleDate2 = dateend.strftime("%Y-%m-%d")

    url = "https://purchase.izettle.com/purchases/v2?startDate={0}&endDate={1}".format(izettleDate1, izettleDate2)

    header = {
        'Authorization': "Bearer {0}".format(GetToken())
    }

    purchases = requests.get(url, headers=header).json()
    purchases = purchases['purchases']
    with open(purchasesfile, 'w') as outfile:
        json.dump(purchases, outfile, indent=4, sort_keys=True)
    logging.info('Downloaded iZettle purchases ({0} items)'.format(len(purchases)))

    # print(json.dumps(purchases, sort_keys=True, indent=2))
    # exit(1)
    # for purchase in purchases['purchases']:
    #     print("------------------------------------------------")
    #     print(purchase['amount'])
    #     price = round(purchase['amount'], 2)
    #     price = (price / 100)
    #     print(price)
    #     print(purchase['timestamp'])
    #     Irate = ((price / 100) * izettleRate)
    #     print(Irate)
    #     print(price - Irate)
    #
    #     # time_object = datetime.strptime(purchase['timestamp'], '%y-%m-%dT%H:%M:%S.%f+0000').date()
    #     # print(time_object)
    #
    # print("------------------------------------------------")


def GetPurchases():
    with open(purchasesfile) as json_file:
        data = json.load(json_file)
    return data


def GetMyInfo():
    url = "https://oauth.izettle.com/users/me"
    header = {
        'Authorization': "Bearer {0}".format(GetToken())
    }

    myinfo = requests.get(url, headers=header).json()
    return myinfo


def DownloadTransactions(datestart, dateend):

    izettleDate1 = datestart.strftime("%Y-%m-%d")
    izettleDate2 = dateend.strftime("%Y-%m-%d")

    url = "https://finance.izettle.com/organizations/self/accounts/LIQUID/transactions?start={0}&end={1}" \
        .format(izettleDate1, izettleDate2)

    header = {
        'Authorization': "Bearer {0}".format(GetToken())
    }

    transactions = requests.get(url, headers=header).json()
    transactions = transactions['data']
    with open(transactionsfile, 'w') as outfile:
        json.dump(transactions, outfile, indent=4, sort_keys=True)
    logging.info('Downloaded iZettle transactions ({0} items)'.format(len(transactions)))

def GetTransactions():
    with open(transactionsfile) as json_file:
        data = json.load(json_file)
    return data


def LookupSalesPaymentUuid(izSalesNumber):
    sales = GetPurchases()
    for sale in sales:
        if numericEqual(sale['globalPurchaseNumber'], izSalesNumber):
            payments = sale['payments']
            if len(payments) != 1:
                logging.error("The iZettle purchase/sale with number {0} has != 1 payment!".format(izSalesNumber))
            return payments[0]['uuid']
    return None


def numericEqual(x, y, epsilon=1 * 10 ** (-8)):
    """Return True if two values are close in numeric value
        By default close is withing 1*10^-8 of each other
        i.e. 0.00000001
    """
    return abs(x - y) <= epsilon

# this code will only be run if this script is run directly
if __name__ == '__main__':
    print(json.dumps(GetMyInfo(), indent=2, sort_keys=True))
