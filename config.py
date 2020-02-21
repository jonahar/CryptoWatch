import os

CRYPTO_WATCH_DIR = os.path.join(os.path.expandvars("$HOME"), ".cryptowatch")
WALLET_FILENAME = "wallet"
WALLET_FULLPATH = os.path.join(CRYPTO_WATCH_DIR, WALLET_FILENAME)
LOGFILE = os.path.join(CRYPTO_WATCH_DIR, "cryptowatch.log")
