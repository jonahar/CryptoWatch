from typing import List, Optional, Tuple

import requests

from utils import logger

"""
This module is responsible for retrieving data from external sources, such as
addresses balance and coins value
"""

NOT_FOUND = -1


def lookup_btc_addresses(addresses: List[str]) -> Optional[List[float]]:
    all_addresses = "|".join(addresses)
    query = f"https://blockchain.info/balance?active={all_addresses}"
    
    response = requests.get(query)
    if not response.ok:
        # TODO: if at least one of the addresses is invalid the call will fail. try extracting them
        #  one by one
        return None
    
    response_json = response.json()
    
    return [
        response_json[addr]['final_balance'] / 1e8  # amount is returned in satoshis
        for addr in addresses
    ]


def lookup_eth_addresses(addresses: List[str]) -> Optional[List[float]]:
    all_addresses = ",".join(addresses)
    query = f"https://api.etherscan.io/api?module=account&action=balancemulti&address={all_addresses}"
    
    response = requests.get(query)
    if not response.ok:
        return None
    response_json: List[dict] = response.json()['result']
    
    # check that the addresses in the response are in the same order
    if not all(map(
        lambda t: t[0] == t[1]["account"],
        zip(addresses, response_json)
    )):
        logger.error("ETH addresses lookup response have unexpected order")
        return None
    
    return [
        float(response_dict["balance"]) / 1e18  # amount is returned in atomic units
        if "balance" in response_dict and response_dict["balance"] != ""
        else NOT_FOUND
        for response_dict in response_json
    ]


def lookup_addresses(coin: str, addresses: List[str]) -> Optional[List[float]]:
    """
    return the balance of given addresses of some coin

    :param coin the currency code (e.g. 'BTC' for bitcoin, 'ETH' for Ethereum, etc)
    :param addresses: a list of strings. each string is an address to look
    :return: a list of floats which correspond to the balances of the input addresses.
             If an address' balance could not be found or the address is invalid, the
             returned balance for this address is -1.
             In case of failure None is returned
    """
    
    if coin == 'BTC':
        return lookup_btc_addresses(addresses)
    
    if coin.upper() == 'ETH':
        return lookup_eth_addresses(addresses)
    
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
