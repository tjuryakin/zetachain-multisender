# Minimum pause time between successful withdrawals
DELAY_MIN = 420

# Maximum pause time between successful withdrawals
DELAY_MAX = 840

# List of exchanges you will work with (Visit https://docs.ccxt.com/, there are tables with exchange IDs)
# Currently 4 exchanges are supported: okx, bybit, bitget, htx
# REMINDER: you need to add addresses to the whitelist on each exchange (address book)
LIST_AVAILABLE_EXCHANGE = ['okx', 'bybit', 'bitget']

# Zeta RPC
RPC_URL = 'https://zetachain-evm.blockpi.network/v1/rpc/public'

# The amount in the wallet, more than which you do not need to top it up
MINIMUM_BALANCE_ZETA = 1.7

# Check the current balance of the outgoing wallet, if the amount on it is greater than MINIMUM_BALANCE_ZETA - skip withdrawal to this wallet
CHECK_CURRENT_WALLET_BALANCE = True
