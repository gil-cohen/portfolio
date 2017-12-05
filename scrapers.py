# -*- coding: utf-8 -*-
import json
import requests
import urllib.request
import pprint
import re

def get_symbol(symbol, exchange=None):
    link = f'https://finance.google.com/finance?q={symbol}&output=json'
    if exchange:
        link = f'https://finance.google.com/finance?q={symbol}:{exchange}&output=json'
    
    print(f'Accessing `{link}`')
    response = requests.get(link)
    
    if response.status_code in (200,):
        raw_data = response.content[6:-2].decode('unicode_escape') 
        return json.loads(raw_data)
        
def get_symbol_last_price(symbol, exchange):
    symbol_data = get_symbol(symbol, exchange)
    # l - last price
    last_price = float(symbol_data['l'].replace(',', ''))
    print(f'symbol {exchange}:{symbol} last price is {last_price}')
    return last_price
    
def get_symbol_id(paper):
    url =  'https://www.investing.com/search/service/search'
    values = dict(
        search_text=paper,
        term=paper,
        country_id=0,
        tab_id='All'
    )
    
    headers = {
        'Host': 'www.investing.com',
        'Connection': 'keep-alive',
        'Content-Length': '50',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Origin': 'https://www.investing.com',
        'X-Requested-With': 'XMLHttpRequest', # important
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36', #important
        'Content-Type': 'application/x-www-form-urlencoded',
        'Referer': 'https://www.investing.com/',
        #'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9',
    }
    
    data = urllib.parse.urlencode(values)
    data = data.encode('ascii') # data should be bytes
    request = urllib.request.Request(url, data, headers)

    with urllib.request.urlopen(request) as response:
        data = json.loads(response.read())
        for symbol in data['All']:
            if symbol['symbol'] == paper:
                return symbol['pair_ID']

def get_israeli_dividends(symbol, amount=0):
    symbol_id = get_symbol_id(symbol)
    values = dict(
        pairID = symbol_id,
        last_timestamp = 2001436800, # really far into the future
    )
    
    headers = {
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36',
        'X-Requested-With':'XMLHttpRequest',
    }
    
    data = urllib.parse.urlencode(values)
    data = data.encode('ascii') # data should be bytes
    request = urllib.request.Request('https://www.investing.com/equities/MoreDividendsHistory', data, headers)
    with urllib.request.urlopen(request) as response:
        data = json.loads(response.read())
        data = data['historyRows'].replace('\r\n', '')

        print(data)
        res = re.findall('<tr event_timestamp="(.*?)">.*?<td>(\d+(\.\d+)?)<\/td>', data, re.DOTALL)
        return res
