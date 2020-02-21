# CryptoWatch - Multi Cryptocurrency watch-only wallet


CryptoWatch is a command line tool which provides a solution for keeping track on balances of multiple cryptocurrencies.
It provides watch feature only, which makes it lightweight and invulnerable to coins theft.
CryptoWatch displays all different coins tracked by the wallet, along with their amount and total value in USD and BTC.
It allows to track specific addresses, or manually add amount for a coin (This is useful for coins that don't
have a transparent blockchain, such as Monero).

CryptoWatch is especially useful for tracking multiple cold storages.


## Usage

To start CryptoWatch simply run the main module 'cryptowatch':
```
./cryptowatch.py
OR
python3 cryptowatch.py
```
By default, the wallet data is saved to a file named `wallet` in a directory
`.cryptowatch` in the user's home directory.
