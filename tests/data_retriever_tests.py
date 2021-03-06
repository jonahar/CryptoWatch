import unittest

from data_retriever import NOT_FOUND, lookup_addresses


class DataRetrieverTest(unittest.TestCase):
    
    def test_btc_lookup_single(self):
        addresses = [
            "1FDMwEo8qNa9icVcooBUoGvA6NriePtJJ3",  # balance 50
        ]
        expected_balances = [50]
        balances = lookup_addresses(coin="BTC", addresses=addresses)
        self.assertListEqual(balances, expected_balances)
    
    def test_btc_lookup_multiple(self):
        # both addresses were last used in 2009. probably wouldn't change.
        # worst case, test will fail and we'll figure it out
        addresses = [
            "15NUwyBYrZcnUgTagsm1A7M2yL2GntpuaZ",  # balance 0
            "1FDMwEo8qNa9icVcooBUoGvA6NriePtJJ3",  # balance 50
        ]
        expected_balances = [0, 50]
        balances = lookup_addresses(coin="BTC", addresses=addresses)
        self.assertListEqual(balances, expected_balances)
    
    def test_eth_lookup_single(self):
        addresses = [
            "0x2C3C1dF3c25FE3875cE559FC68c6E9068bD952ED",  # balance 0.000518161526620852
        ]
        expected_balances = [0.000518161526620852]
        balances = lookup_addresses(coin="ETH", addresses=addresses)
        self.assertListEqual(balances, expected_balances)
    
    def test_eth_lookup_multiple(self):
        addresses = [
            "0xDf190dC7190dfba737d7777a163445b7Fff16133",  # balance 0
            "0x2C3C1dF3c25FE3875cE559FC68c6E9068bD952ED",  # balance 0.000518161526620852
            "0xGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",  # invalid address format
        ]
        expected_balances = [0, 0.000518161526620852, NOT_FOUND]
        balances = lookup_addresses(coin="ETH", addresses=addresses)
        self.assertListEqual(balances, expected_balances)
    
    def test_bch_lookup_single(self):
        addresses = [
            "1FDMwEo8qNa9icVcooBUoGvA6NriePtJJ3",  # balance 50
        ]
        expected_balances = [50]
        balances = lookup_addresses(coin="BCH", addresses=addresses)
        self.assertListEqual(balances, expected_balances)
    
    def test_bch_lookup_multiple(self):
        addresses = [
            "15NUwyBYrZcnUgTagsm1A7M2yL2GntpuaZ",  # balance 0
            "1FDMwEo8qNa9icVcooBUoGvA6NriePtJJ3",  # balance 50
        ]
        expected_balances = [0, 50]
        balances = lookup_addresses(coin="BCH", addresses=addresses)
        self.assertListEqual(balances, expected_balances)
    
    def test_ltc_lookup_single(self):
        addresses = [
            "LgYj5bghguAf4kdSh8erb3bTnjpuZtYUti",  # balance 0.05587024
        ]
        expected_balances = [0.05587024]
        balances = lookup_addresses(coin="LTC", addresses=addresses)
        self.assertListEqual(balances, expected_balances)
    
    def test_ltc_lookup_multiple(self):
        addresses = [
            "LgYj5bghguAf4kdSh8erb3bTnjpuZtYUti",  # balance 0.05587024
            "LhKxXU6QtxoGNxeU9uUTrLjA1X5wPtbiep",  # balance 0.00000960
        ]
        expected_balances = [0.05587024, 0.00000960]
        balances = lookup_addresses(coin="LTC", addresses=addresses)
        self.assertListEqual(balances, expected_balances)


if __name__ == '__main__':
    unittest.main()
