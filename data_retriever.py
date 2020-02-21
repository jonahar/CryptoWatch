from typing import List, Optional, Tuple

import requests

"""
This module is responsible for retrieving data from external sources, such as
addresses balance and coins value
"""


def lookup_addresses(coin: str, addresses: List[str]):
    """
    return the balance of given addresses of some coin

    :param coin the currency code (e.g. 'BTC' for bitcoin, 'ETH' for Ethereum, etc)
    :param addresses: a list of strings. each string is an address to look
    :return: a list of floats which correspond to the balances of the input addresses.
             If an address' balance could not be found or the address is invalid, the
             returned balance for this address is -1.
             In case of failure None is returned
    """
    
    if coin.upper() == 'BTC':
        query = 'https://blockchain.info/balance?active='
        for addr in addresses:
            query += addr + '|'
        query = query[:-1]  # remove the last separator. the API doesn't allow this
        try:
            dict = requests.get(query).json()
        except:
            # TODO: if at least one of the addresses is invalid the call will fail. try extracting them
            #  one by one
            return None
        res = []
        for addr in dict.keys():
            amount_satoshi = float(dict[addr]['final_balance'])
            res.append(amount_satoshi / 1e8)
        return res
    
    if coin.upper() == 'ETH':
        query = 'https://api.etherscan.io/api?module=account&action=balancemulti&address='
        for addr in addresses:
            query += addr + ','
        coins_info = requests.get(query).json()['result']  # list of dictionaries
        res = []
        for coin_info in coins_info:
            try:
                res.append(float(coin_info['balance']) / 1e18)  # amount is returned in atomic units
            except:
                res.append(-1)
        return res
    
    # TODO add special lookup for BCH
    
    return None


def lookup_value(coins: List[str]) -> List[Optional[Tuple[float, float]]]:
    """
    return the value of the given coins in USD and BTC

    :param coins: a collection of coin codes.
    :return: list of tuples - each tuple is (coin_value_USD, coin_value_BTC).
             if a coin is not found, None is placed in its corresponding index in the list
    """
    res = []
    try:
        all_coins = requests.get('https://api.coinmarketcap.com/v1/ticker/').json()
        for coin in coins:
            coin = coin.upper()
            found = False
            for coin_info in all_coins:
                if coin_info['symbol'] == coin:
                    # this is the coin
                    found = True
                    res.append((float(coin_info['price_usd']), float(coin_info['price_btc'])))
                    break
            if not found:
                res.append(('N/A', 'N/A'))
        return res
    
    except Exception:
        return [None] * len(coins)
