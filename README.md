# CryptoWatch - Multi Cryptocurrency watch-only wallet


CryptoWatch is a command line tool which provides a solution for keeping track on balances of multiple cryptocurrencies.
It provides watch feature only, which makes it lightweight and invulnerable to coins theft.
CryptoWatch displays all different coins tracked by the wallet, along with their amount and total value in USD and BTC.
It allows to track specific addresses, or manually add amount for a coin (This is useful for coins that don't
have a transparent blockchain, such as Monero).

CryptoWatch is especially useful for tracking multiple cold storages.


## Usage

To start CryptoWatch simply run the 'cryptowatch' Python script:
```
python cryptowatch.py
```
or
```
python3 cryptowatch.py
```

Note that you should be consistent with the version of python you use to run the program: 
It uses serialization using pickle, which differs between the two versions of python.

By default the wallet saves its data to a file named `.cryptowatch.wallet` in a directory
`.cryptowatch` in the user's home directory. These can be changed at the start of the file `wallet.py`.


## Tip Jar
Donations are greatly appreciated  
Bitcoin: `1LUEGXTsXFi7JEVmR9iwGzUiLxx18NH63p`  
Monero: `4D4HpbmA9VJPjJHutYjZtsb7zBhJQc4CodAd5ujsxxVPjHtQ8ELKTgwJig64wEzFry9NWnm47t4jcWMH4cM2FjLZNd8t7a29ECZ1MF3ucA`
