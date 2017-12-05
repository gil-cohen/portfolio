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
        'Cookie': 'adBlockerNewUserDomains=1512419337; __qca=P0-1205975076-1512419328308; PHPSESSID=f1ffr10h1vuf1punulotug1o67; geoC=IL; StickySession=id.35760618223.344www.investing.com; r_p_s=1; searchedResults=[{"pairId":10893,"link":"/equities/delek-automotive","symbol":"DLEA","name":"Delek%20Automotive%20Systems%20Ltd","type":"Equity%20-%20Tel%20Aviv","flag":"Israel"}]; gtmFired=OK; editionPostpone=1512419467810; SideBlockUser=a%3A2%3A%7Bs%3A10%3A%22stack_size%22%3Ba%3A1%3A%7Bs%3A11%3A%22last_quotes%22%3Bi%3A8%3B%7Ds%3A6%3A%22stacks%22%3Ba%3A1%3A%7Bs%3A11%3A%22last_quotes%22%3Ba%3A1%3A%7Bi%3A0%3Ba%3A3%3A%7Bs%3A7%3A%22pair_ID%22%3Bs%3A5%3A%2210893%22%3Bs%3A10%3A%22pair_title%22%3Bs%3A0%3A%22%22%3Bs%3A9%3A%22pair_link%22%3Bs%3A26%3A%22%2Fequities%2Fdelek-automotive%22%3B%7D%7D%7D%7D; _gat_allSitesTracker=1; _gat=1; optimizelySegments=%7B%224225444387%22%3A%22gc%22%2C%224226973206%22%3A%22search%22%2C%224232593061%22%3A%22false%22%2C%225010352657%22%3A%22none%22%7D; optimizelyBuckets=%7B%7D; optimizelyEndUserId=oeu1512419326378r0.6194372907748338; adbBLk=1; nyxDorf=OTtkPjF5NWg%2BYGhmM342PWA0M3Y%2FOWZnYmU%3D; billboardCounter_1=0; _ga=GA1.2.197294575.1512419328; _gid=GA1.2.76900588.1512419328',
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
