# -*- coding: utf-8 -*-

import json
import sys
import pprint

from .portfolio import Portfolio, Share
from .scrapers import get_israeli_dividends

def portfolio_test():
    return Portfolio(sys.argv[1])
    print(portfolio.calculate_total())
    
def symbol_test():
    symbol_data = get_symbol('DLEA.TA')
    pprint.pprint(symbol_data)
       
def israeli_dividend_test():
    dividends = get_israeli_dividends('AAPL')
    print(dividends)
    print(sum(float(dividend[1]) for dividend in dividends))
    
def main():
    israeli_dividend_test()
    
if __name__ == '__main__':
    main()