# -*- coding: utf-8 -*-

import codecs
from ofxparse import OfxParser

from .scrapers import get_symbol, get_symbol_last_price

class Portfolio:
    
    def __init__(self, ofx_path):
        with codecs.open(ofx_path) as fileobj:
            self.ofx = OfxParser.parse(fileobj)
            
        self.shares = []
        for t in self.ofx.account.statement.transactions:
            exchange, symbol = t.security.split(':')
            if exchange == 'TLV':
                continue

            share = self.get_share(symbol, exchange)
            if not share:
                share = Share(symbol, exchange)
                self.shares.append(share)
                
            share.add_transaction(
                str(t.tradeDate),
                float(t.units),
                float(t.unit_price),
                t.type,
                int(t.commission),
            )
            
    def get_share(self, symbol, exchange=None):
        for share in self.shares:
            if share.symbol == symbol:
                if exchange and share.exchange != exchange:
                    continue
                return share
                
    def calculate_total(self):
        sum = 0
        for share in self.shares:
            value = share.calculate_value()
            print(f'Holdings of share `{share.exchange}:{share.symbol}`: `{share.amount}` shares @ value is `{value}`)\n')
            sum += value
        return sum #return sum(share.calculate_value() for share in self.shares)
        
class Share:

    def __init__(self, symbol, exchange):
        self.symbol = symbol
        self.exchange = exchange
        self.transactions = []
        
    def add_transaction(self, date, amount, price, transaction_type, commission):
        print(self.symbol)
        print(self.exchange)
        print(date)
        print(amount)
        print(price)
        print(transaction_type)
        print(commission)
        print()
        self.transactions.append(dict(
            date=date,
            amount=amount,
            price=price,
            transaction_type=transaction_type,
            commission=commission,
        ))
    
    @property
    def amount(self):
        return sum(transaction['amount'] for transaction in self.transactions)
        
    def calculate_value(self):
        return self.amount * get_symbol_last_price(self.symbol, self.exchange)
        
    def calculate_profit(self):
        return sum(transaction['amount'] * transaction['price'] - transaction['commission'] for transaction in self.transactions)
        