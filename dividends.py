# -*- coding: utf8 -*-
import urllib.request as urllib2
#import BeautifulSoup
import datetime
import threading
import sys
import json
import string
import pprint
import time
from multiprocessing.pool import ThreadPool
import dateutil.parser


import json
import requests
    
strptime = datetime.datetime.strptime
time.sleep(0.1)
SYMBOLS = [

]

def getUsDividendsMap(symbol):
    sys.stdout.write('Reading url for symbol: {0}\n'.format(symbol))
    data = urllib2.urlopen('http://www.nasdaq.com/symbol/%s/dividend-history' % symbol).read()
    sys.stdout.write('Parsing data for symbol: {0}\n'.format(symbol))
    #data = BeautifulSoup.BeautifulSoup(data)
    sys.stdout.write('Parsed data for symbol: {0}\n'.format(symbol))
    print(data)
    table = data.find('table', id='quotes_content_left_dividendhistoryGrid')
    if data.find('div', id='qwidget_lastsale'):
        last_price = data.find('div', id='qwidget_lastsale').text
    else:
        last_price = '0'
    idx = []
    res = []
    if not table:
        return (res, float(last_price.strip('$')))
    rows = table.findAll('tr')
    for col in rows[0].findAll('th'):
        idx.append(col.text)
    for row in rows[1:]:
        rowAsDict = {}
        for i,col in enumerate(row.findAll('td')):
            rowAsDict[idx[i]] = col.text
        res.append(rowAsDict)
    return (res, float(last_price.strip('$')))

def getDividendsAmmount(symbol, date, amount, buy_price=None):
    dividends, last_price = getUsDividends(symbol, amount)
    date = dateutil.parser.parse(date)
    dividends = filter(lambda x: dateutil.parser.parse(x['Ex'], dayfirst=True) > date, dividends)
    total_before, total_after = 0,0
    for dividend in dividends:
        total_before += float(dividend.get('Total', 0))
        total_after += float(dividend.get('TotalAfterTax', 0))
    #pprint.pprint(dividends)
    #printForSymbol(dividends)
    currency = '$' if isUsSymbol(symbol) else u'₪'
    print('='*108)
    print(u'Symbol: {0:<19} From Date: {1}\tAmount: {2}\nTotal dividends: {6:<6}\t    Total:   {5}{3:<9}\t\tAfter tax:  {5}{4:<11}\t'.format(
            symbol, date.strftime('%d/%m/%Y'), amount, total_before, total_after, currency, len(dividends)))
    if buy_price:
        gain_loss = (last_price - buy_price) * amount
        gain_yield = (gain_loss + total_before) / (amount * buy_price) * 100
        print(u'Price:  {0:<19} Buy Price: {1}\t\tGain\Loss: {2}\nTotal including dividends:  {3}\t\t\tYield: {4}%'.format(
            last_price, buy_price, gain_loss, gain_loss + total_before, gain_yield))
    print('='*108)
    

def getUsDividends(symbol, amount=0):
    res = []
    sys.stdout.write('Started with {}\n'.format(symbol))
    dividends, last_price = getUsDividendsMap(symbol)
    for dividend in dividends:
        dic = {'tid' : threading.get_ident(), 'symbol':symbol, 'comment': '', 'PaymentUnknown': False }
        try:
            latestPaymentDate = strptime(dividend['Payment Date'], '%m/%d/%Y').date()
        except:
            dic['PaymentUnknown'] = True
            latestPaymentDate = (datetime.timedelta(days=1) + datetime.datetime.now()).date()
        try:
            latestExDate = strptime(dividend['Ex/Eff Date'], '%m/%d/%Y').date()
        except:
            latestExDate = datetime.datetime.fromtimestamp(0).date()
        dic['Ex'] = latestExDate.strftime('%d/%m/%Y')
        dic['Amount'] = dividend['Cash Amount']
        dic['Payment'] = latestPaymentDate.strftime('%d/%m/%Y')
        try:
            dic['Total'] = str(amount * float(dic['Amount']))
            dic['TotalAfterTax'] = str(amount * float(dic['Amount']) * 0.75)
        except:
            dic['Total'] = '0'
            dic['TotalAfterTax'] = '0'
        if latestPaymentDate <= datetime.datetime.now().date():
            dic['comment'] += 'Payment date passed! '
        elif latestExDate <= datetime.datetime.now().date():
            dic['comment'] += 'Ex date passed! '
        res += [dic]
    sys.stdout.write('Ended with {}\n'.format(symbol))
    return (res, last_price)

def getIsraeliPaperId(paper):
    paper = paper.replace(' ', '+')
    t = json.loads(urllib2.urlopen('http://www.bizportal.co.il/SearchEngine/SearchQuery?Type=2&QueryString={0}'.format(paper)).read())[0]
    paperId = t['PaperId']
    return paperId

def getIsraeliDividends(paper, amount=0):
    res = []
    paperId = getIsraeliPaperId(paper)
    req1 = urllib2.Request('http://www.bizportal.co.il/Quote/Dividends/FutureEvents_AjaxBinding_Read/{0}?page=1&pageSize=100'.format(paperId))
    req1.add_header('Referer', 'http://www.bizportal.co.il/')
    future_dividends = json.loads(urllib2.urlopen(req1).read())['Data']
    req2 = urllib2.Request('http://www.bizportal.co.il/Quote/Dividends/HistoricalEvents_AjaxBinding_Read?stockID={0}&page=1&pageSize=100'.format(paperId))
    req2.add_header('Referer', 'http://www.bizportal.co.il/')
    past_dividends = json.loads(urllib2.urlopen(req2).read())['Data']
    dividends = (future_dividends if future_dividends else []) + (past_dividends if past_dividends else [])
    for i in dividends:
        dic = {'tid' : threading.get_ident(), 'symbol' : paper.decode('utf8'), 'comment' : '' }
        latestExDate = strptime(i['XDate'], '%d/%m/%y').date()
        latestPaymentDate = strptime(i['PaymentDate'], '%d/%m/%y').date()
        dic['Ex'] = latestExDate.strftime('%d/%m/%Y')
        dic['Amount'] = str(float(''.join([c for c in i['PaymentFull'] if c in string.digits + '.'])) / 100) if i['PaymentFull'] else '0'
        dic['Payment'] = latestPaymentDate.strftime('%d/%m/%Y')
        dic['Total'] = str(amount * float(dic['Amount']))
        dic['Tax'] = i['Tax']
        dic['TotalAfterTax'] = str(float(dic['Total']) * ((100-float(i['Tax'])) / 100) )
        if latestPaymentDate <= datetime.datetime.now().date():
            dic['comment'] += 'Payment date passed!'
        elif latestExDate <= datetime.datetime.now().date():
            dic['comment'] += 'Ex date passed!'
        res += [dic]
    return res

def isUsSymbol(symbol):
    if not symbol.strip(string.ascii_letters + string.punctuation):
        return True
    else:
        return False

def printForSymbol(dividendsSymbolDict):
    dividendsSymbolDict.sort(cmp=lambda x,y: int((strptime(x['Payment'], '%d/%m/%Y') - strptime(y['Payment'], '%d/%m/%Y')).total_seconds()))
    for i in dividendsSymbolDict:
        if ''.join([c for c in i['Amount'] if c in string.digits + '.']) == i['Amount'] and float(i['Amount']) < 0.00001:
            pass
            #continue
        currency = '$' if isUsSymbol(i['symbol']) else u'₪'
        print(u'Symbol: {1:<19} Ex Date: {2} \tPayment Date: {4}\tComments:\n{8}Amount: {9}{3:<10} Total:   {9}{5:<9}\t\tAfter tax:  {9}{6:<11}\t{7}'.format(
            i['tid'], i['symbol'], i['Ex'], i['Amount'], 'Unknown\t' if i.get('PaymentUnknown', False) else i['Payment'],
            i.get('Total', 0), i['TotalAfterTax'], i.get('comment', 'No comment.'), ' '*8, currency))
        print('-'*108)

def getDividends(symbol, amount):
    try:
        if isUsSymbol(symbol):
            return getUsDividends(symbol, amount)[0]
        else:
            return getIsraeliDividends(symbol, amount)
    except:
        import traceback
        traceback.print_exc()

def printComing(symbols, days_back=15):
    start = datetime.datetime.now()
    pool = ThreadPool(processes=4)
    res = pool.map(lambda s:getDividends(s[0], s[1]), symbols)
    res = reduce(lambda a,b: (a if a else []) + (b if b else []), res)
    pool.close()
    pool.join()
    end = datetime.datetime.now()
    delta = end-start
    res = filter(lambda i: strptime(i['Payment'], '%d/%m/%Y').date() >= datetime.datetime.now().date() - datetime.timedelta(days=days_back), res)
    res = filter(lambda i: not i.get('PaymentUnknown', False) or strptime(i['Ex'], '%d/%m/%Y').date() >= datetime.datetime.now().date() - datetime.timedelta(days=30), res)
    printForSymbol(res)
    print('Done for all, total time: ' + str(delta))

#printComing(SYMBOLS, 15)

def test_from_ofx():
    ofx_path = r'C:\Users\Lior\Downloads\My Portfolio.ofx'
    from ofxparse import OfxParser
    import codecs
    with codecs.open(ofx_path) as fileobj:
        ofx = OfxParser.parse(fileobj)
    txns = ofx.account.statement.transactions
    for t in txns:
        exchange, symbol = t.security.split(':')
        date = str(t.tradeDate)
        amount = float(t.units)
        buy_price = float(t.unit_price)
        if exchange == 'TLV':
            print('Skipping stock TLV:{0}'.format(symbol))
            continue
        getDividendsAmmount(symbol, date, amount, buy_price)

def get_symbol(symbol):
    link = 'https://finance.google.com/finance?q={0}&output=json'.format(symbol)
    print(f'Accessing `{link}`')
    rsp = requests.get(link)
    
    if rsp.status_code in (200,):
        data = rsp.content[6:-2].decode('unicode_escape') 
        return json.loads(data)

def main():
    symbol_data = get_symbol('DLEA.TA')
    print(symbol_data.keys())
    return

    # print out some quote data
    print('Opening Price: {}'.format(fin_data['op']))
    print('Price/Earnings Ratio: {}'.format(fin_data['pe']))
    print('52-week high: {}'.format(fin_data['hi52']))
    print('52-week low: {}'.format(fin_data['lo52']))
        
if __name__ == '__main__':
    main()