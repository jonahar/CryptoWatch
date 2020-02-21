import os
import pickle
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Set

from data_retriever import lookup_addresses, lookup_value
from utils import CRYPTO_WATCH_DIR

WALLET_FILENAME = "wallet.pickle"
WALLET_FULLPATH = os.path.join(CRYPTO_WATCH_DIR, WALLET_FILENAME)


@dataclass
class TrackedCoin:
    addresses: Set[str] = field(default_factory=set)
    manual_balance: float = 0
    
    @staticmethod
    def get_empty_tracked_coin() -> "TrackedCoin":
        return TrackedCoin()


class Wallet:
    def __init__(self):
        os.makedirs(CRYPTO_WATCH_DIR, exist_ok=True)
        
        # if wallet file exists, load it
        if os.path.isfile(WALLET_FULLPATH):
            with open(WALLET_FULLPATH, 'rb') as f:
                self.wallet: Dict[str, TrackedCoin] = pickle.load(f)
        else:
            # keys are coin symbols
            # we can't use a lambda for the defaultdict so it will be picklable
            self.wallet: Dict[str, TrackedCoin] = defaultdict(
                TrackedCoin.get_empty_tracked_coin
            )
    
    def dump(self):
        with open(WALLET_FULLPATH, 'wb') as f:
            pickle.dump(self.wallet, f)
    
    def add_addresses(self, coin_symbol: str, addresses: Iterable[str]):
        """
        :param coin_symbol: coin code (e.g. BTC for Bitcoin)
        :param addresses: an iterable of addresses to watch of the given coin
        """
        self.wallet[coin_symbol].addresses.update(addresses)
        self.dump()
    
    def add_manual_balance(self, coin_symbol: str, balance: float):
        """
        adds balance for some coin manually. If a manual balance already exists for this coin,
        adds the given balance to the current balance
        """
        self.wallet[coin_symbol].manual_balance += balance
        self.dump()
    
    def remove_watch_address(self, coin_symbol: str, addresses: Iterable[str]):
        """
        removes addresses of a coin from the watch list. If a given address is
        not on the watch list it is ignored.
        """
        self.wallet[coin_symbol].addresses.difference_update(addresses)
        self.dump()
    
    def remove_manual_balance(self, coin_symbol: str):
        """
        removes the manual balance of the given coin
        """
        self.wallet[coin_symbol].manual_balance = 0
        self.dump()
    
    def remove_coin(self, coin_symbol: str):
        """
        completely remove the coin from the wallet
        """
        self.wallet.pop(coin_symbol, default=None)
        self.dump()
    
    def get_coins_ids(self) -> List[str]:
        """
        return a list of all the coins in this wallet
        """
        return list(self.wallet.keys())
    
    def get_coin_info(self, coin_symbol: str) -> TrackedCoin:
        return self.wallet[coin_symbol]
    
    def get_balances(self):
        """
        :return: List of lists. each inner list has the following elements:
                      [coin_code, amount, value_in_usd, value_in_btc]
                 coins for which finding the value was failed, the values will be 'N/A'
        """
        res = []
        coin_symbols_list = list(self.wallet.keys())
        coins_values = lookup_value(coin_symbols_list)
        for coin_idx, coin_code in enumerate(coin_symbols_list):
            addresses_amounts = lookup_addresses(coin_code, list(self.wallet[coin_code].addresses))
            total_coin_amount = 0
            if addresses_amounts is not None:
                # addresses whose balance was failed to retrieve is -1. sum everything except
                # failures
                for addr_amount in addresses_amounts:
                    if addr_amount > 0:
                        total_coin_amount += addr_amount
            
            total_coin_amount += self.wallet[coin_code].manual_balance
            total_coin_amount = round(total_coin_amount, 8)  # truncate to maximum 8 digits after decimal point
            
            if coins_values[coin_idx] is None:
                value_usd = 'N/A'
                value_btc = 'N/A'
            else:
                value_usd = round((total_coin_amount * coins_values[coin_idx][0]), 3)
                value_btc = round((total_coin_amount * coins_values[coin_idx][1]), 8)
            
            res.append([coin_code, total_coin_amount, value_usd, value_btc])
        
        return res
    
    def delete(self):
        """
        Delete all data from this wallet and delete the file from the disk.
        If later, funds are added to this wallet, it will be created again on the disk
        """
        if os.path.isfile(WALLET_FULLPATH):
            os.remove(WALLET_FULLPATH)
        self.wallet.clear()
