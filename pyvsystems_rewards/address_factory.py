from collections import OrderedDict

import requests

from .address import Address
from .lease import Lease
from .minting_reward import MintingReward
from .pool_distribution import PoolDistribution


class AddressFactory:
    TRANSACTION_CODE = {
        'Genesis': 1,
        'Payment': 2,
        'Lease': 3,
        'LeaseCancel': 4,
        'MintingTransaction': 5,
        'ContendSlotsTransaction': 6,
        'ReleaseSlotsTransaction': 7,
        'RegisterContractTransaction': 8,
        'ExecuteContractFunctionTransaction': 9,
        'DbPutTransaction': 10,
    }

    def __init__(
            self,
            api_url,
            hot_wallet_address,
            cold_wallet_address,
            operation_fee_percent
    ):
        self.total_interest = 0
        self.total_operation_fee = 0
        self.total_pool_distribution = 0
        self._api_url = api_url
        self._hot_wallet_address = hot_wallet_address
        self._cold_wallet_address = cold_wallet_address
        self._operation_fee_percent = operation_fee_percent
        self._addresses = None

        self.get_addresses()

    def get_addresses(self):
        if self._addresses is not None:
            return self._addresses.values()

        self._addresses = {}
        hot_wallet_transactions = self._get_transactions(self._hot_wallet_address)
        cold_wallet_transactions = self._get_transactions(self._cold_wallet_address)
        self._add_leases(hot_wallet_transactions)
        self._add_minting_rewards(cold_wallet_transactions)
        self._add_pool_distributions(cold_wallet_transactions)

        return self._addresses.values()

    def get_active_addresses(self, height):
        addresses = self.get_addresses()
        return [address for address in addresses if address.is_active(height)]

    def get_inactive_addresses(self, height):
        addresses = self.get_addresses()
        return [address for address in addresses if not address.is_active(height)]

    def _get_transactions(self, address):
        '''Returns all of the transactions associated with an address in
        increasing block height order.'''
        descending_transactions = OrderedDict()
        offset = 0
        limit = 10000
        while True:
            transactions = requests.get(
                self._api_url + '/transactions/list',
                params={'address': address, 'limit': limit, 'offset': offset}
            ).json()

            if transactions['size'] == 0:
                break

            for transaction in transactions['transactions']:
                descending_transactions[transaction['id']] = transaction

            offset += limit

        ascending_transactions = []
        for transaction_id in reversed(descending_transactions):
            ascending_transactions.append(descending_transactions[transaction_id])

        return ascending_transactions

    def _add_leases(self, hot_wallet_transactions):
        for tx in hot_wallet_transactions:
            if tx['type'] == self.TRANSACTION_CODE['Lease']:
                address = tx['proofs'][0]['address']
                if address not in self._addresses:
                    self._addresses[address] = Address(address)

                address = self._addresses[address]
                address.start_lease(
                    Lease(tx['id'], address.address, tx['amount'], tx['height'])
                )

            elif tx['type'] == self.TRANSACTION_CODE['LeaseCancel']:
                address = tx['proofs'][0]['address']
                address = self._addresses[address]
                address.stop_lease(tx['leaseId'], tx['height'])

    def _get_active_leases(self, height):
        active_leases = []
        for address in self.get_addresses():
            active_leases.extend(address.active_leases(height))

        return active_leases

    def _add_minting_rewards(self, cold_wallet_transactions):
        for tx in cold_wallet_transactions:
            if tx['type'] == self.TRANSACTION_CODE['MintingTransaction']:
                minting_reward = MintingReward(
                    tx['id'],
                    tx['timestamp'],
                    tx['amount'],
                    tx['height'],
                    self._get_active_leases(tx['height']),
                    self._operation_fee_percent
                )
                self.total_interest += minting_reward.interest
                self.total_operation_fee += minting_reward.operation_fee

                for address in self.get_active_addresses(tx['height']):
                    address.add_minting_reward(minting_reward)

    def _add_pool_distributions(self, cold_wallet_transactions):
        for tx in cold_wallet_transactions:
            if (tx['type'] == self.TRANSACTION_CODE['Payment'] and
                    tx['proofs'][0]['address'] == self._cold_wallet_address):
                address = tx['recipient']
                if address not in self._addresses:
                    continue

                pool_distribution = PoolDistribution(
                    tx['id'],
                    address,
                    tx['amount'],
                    tx['fee'],
                    tx['height']
                )
                self.total_pool_distribution += pool_distribution.amount + pool_distribution.fee
                self._addresses[address].add_pool_distribution(pool_distribution)
