import random
import time
import ccxt

from web3 import Web3
from loguru import logger
from typing import Union

from config.sender_config import (DELAY_MIN, DELAY_MAX, LIST_AVAILABLE_EXCHANGE, RPC_URL, MINIMUM_BALANCE_ZETA,
                                  CHECK_CURRENT_WALLET_BALANCE)
from config.api_config import (OKX_API_KEY, OKX_API_SECRET, OKX_PASSPHRASE, BYBIT_API_KEY, BYBIT_API_SECRET,
                               HTX_API_KEY, HTX_API_SECRET, BITGET_API_KEY, BITGET_API_SECRET,
                               BITGET_PASSPHRASE)

from ccxt.base.errors import InvalidAddress, InsufficientFunds, ExchangeError, PermissionDenied

def get_withdrawal_fee(token, exchange, network_id) -> float:
    currencies = exchange.fetch_currencies()

    for currency_code in currencies:
        if currency_code == token:
            for network in currencies[currency_code]['networks']:
                if currencies[currency_code]['networks'][network]['id'] == network_id:
                    return float(currencies[currency_code]['networks'][network]['fee'])

    raise ValueError(f'Fee not found, check token ({token}) and network ({network_id})')


def withdraw(token: str, amount: Union[int, float], to_address: str, params: dict, exchange) -> bool:
    try:
        exchange.withdraw(token, amount, to_address, params=params)
        return True
    except InvalidAddress:
        logger.warning(f'Invalid address (not in whitelist) {to_address}')
    except InsufficientFunds:
        logger.warning(f'Insufficient balance {token}')
    except ExchangeError:
        logger.warning(f'The withdrawal amount is less than the minimum')
    except PermissionDenied:
        logger.warning(f'Address not allowed in whitelist')
    except Exception as e:
        logger.error(f'Critical error: {e}')

    return False


def okx_withdraw(to_address: str, amount: Union[int, float], token: str, network_id: str) -> bool:
    exchange = ccxt.okx({
        'apiKey': OKX_API_KEY,
        'secret': OKX_API_SECRET,
        'password': OKX_PASSPHRASE,
    })

    result = withdraw(token, amount, to_address, params={
        'toAddr': to_address, 'chainName': network_id, 'fee': get_withdrawal_fee(token, exchange, network_id),
        'dest': 4, 'pwd': '-'
    }, exchange=exchange)

    return result


def bybit_withdraw(to_address: str, amount: Union[int, float], token: str, network_id: str) -> bool:
    result = withdraw(token, amount, to_address, params={'chain': network_id}, exchange=ccxt.bybit({
        'apiKey': BYBIT_API_KEY,
        'secret': BYBIT_API_SECRET
    }))

    return result


# if new whitelist - it's very hard... 1 wallet - sms, 2fa.. stupid
def htx_withdraw(to_address: str, amount: Union[int, float], token: str, network_id: str) -> bool:
    exchange = ccxt.htx({
        'apiKey': HTX_API_KEY,
        'secret': HTX_API_SECRET
    })

    result = withdraw(token, amount, to_address, params={
        'fee': get_withdrawal_fee(token, exchange, network_id),
        'chain': network_id
    }, exchange=exchange)

    return result


def bitget_withdraw(to_address: str, amount: Union[int, float], token: str, network_id: str) -> bool:
    result = withdraw(token, amount, to_address, params={'network': network_id}, exchange=ccxt.bitget({
        'apiKey': BITGET_API_KEY,
        'secret': BITGET_API_SECRET,
        'password': BITGET_PASSPHRASE,
        'enableRateLimit': True,
        'options': {
            'defaultType': 'spot'
        }
    }))

    return result


def get_all_exchanges():
    return {
        'okx': okx_withdraw,
        'bybit': bybit_withdraw,
        'bitget': bitget_withdraw,
        'htx': htx_withdraw
    }


if __name__ == '__main__':
    logger.add('withdraw.log')

    # Token settings
    withdraw_token = 'ZETA'

    web3 = Web3(Web3.HTTPProvider(RPC_URL))

    withdraw_network = {
        'okx': 'ZETA-ZetaChain',
        'bybit': 'ZETAEVM',
        'bitget': 'ZetaChain',
        'htx': 'zeta'
    }

    amount_min = 2.01
    amount_max = 3.31
    # End token settings

    with open('addresses.txt') as f:
        addresses = f.read().splitlines()

    for address in addresses:
        if CHECK_CURRENT_WALLET_BALANCE:
            zeta_balance = web3.from_wei(web3.eth.get_balance(web3.to_checksum_address(address)), 'ether')

            if zeta_balance > MINIMUM_BALANCE_ZETA:
                logger.warning(f'Skip {address} because amount balance {zeta_balance} ZETA')
                continue

        amount = float(random.randint(int(amount_min * 1000), int(amount_max * 1000)) / 1000)
        current_exchange = random.choice(LIST_AVAILABLE_EXCHANGE)

        logger.info(f'current address: {address}')
        logger.info(f'current exchange id: {current_exchange}')
        logger.info(f'amount: {amount}')

        map_exchanges = get_all_exchanges()

        if current_exchange not in list(map_exchanges.keys()):
            listmp = ', '.join(map_exchanges.keys())
            raise ValueError(f'current_exchange must be {listmp}')

        if current_exchange not in list(withdraw_network.keys()):
            listwn = ', '.join(withdraw_network.keys())
            raise ValueError(f'current_exchange must be {listwn}')

        result = map_exchanges[current_exchange](address, amount,
                                                 withdraw_token, withdraw_network[current_exchange])

        if result:
            sleep_time = random.randint(DELAY_MIN, DELAY_MAX)
            logger.info(f'ZETA has been transfered to {address} - {amount} ZETA. Wait {sleep_time} seconds.')
            time.sleep(sleep_time)
        else:
            logger.warning(f'ZETA has not been transfered to {address}')