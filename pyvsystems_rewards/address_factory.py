from collections import defaultdict, OrderedDict

import requests

from .address import Address


class AddressFactory:
    MAB_MATURES_AFTER_BLOCKS = 86400
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
        self.api_url = api_url
        self.hot_wallet_address = hot_wallet_address
        self.cold_wallet_address = cold_wallet_address
        self.operation_fee_percent = operation_fee_percent
        self._addresses = None

    def get_addresses(self):
        if self._addresses is not None:
            return self._addresses

        self._addresses = []

        return self._addresses

    def get_transactions(self, address):
        '''Returns all of the transactions associated with an address in
        increasing block height order.'''
        descending_transactions = OrderedDict()
        offset = 0
        LIMIT = 10000
        while True:
            transactions = requests.get(
                self.api_url + '/transactions/list',
                params={'address': address, 'limit': LIMIT, 'offset': offset}
            ).json();

            if transactions['size'] == 0:
                break

            for transaction in transactions['transactions']:
                descending_transactions[transaction['id']] = transaction

            offset += LIMIT

        ascending_transactions = []
        for transaction_id in reversed(descending_transactions):
            ascending_transactions.append(descending_transactions[transaction_id])

        return ascending_transactions


    def get_address_to_leases(self, hot_wallet_transactions):
        address_to_leases = defaultdict(list)
        for tx in hot_wallet_transactions:
            if tx['type'] == TRANSACTION_CODE['Lease']:
                address = tx['proofs'][0]['address']
                address_to_leases[address].append(
                    Lease(tx['id'], address, tx['amount'], tx['height'])
                )
            elif tx['type'] == TRANSACTION_CODE['LeaseCancel']:
                address = tx['proofs'][0]['address']
                for lease in address_to_leases[address]:
                    if lease.lease_id == tx['leaseId']:
                        lease.stop_height = tx['height']
                        break

        return address_to_leases


    def get_minting_rewards(
        cold_wallet_transactions,
        address_to_leases,
        operation_fee_percent
    ):
        minting_rewards = []
        for tx in cold_wallet_transactions:
            if tx['type'] == TRANSACTION_CODE['MintingTransaction']:
                minting_rewards.append(
                    MintingReward(
                        tx['id'],
                        tx['amount'],
                        tx['height'],
                        address_to_leases,
                        operation_fee_percent
                    )
                )

        return minting_rewards


    def get_address_to_pool_distributions(
        cold_wallet_transactions,
        address_to_leases,
        cold_wallet_address
    ):
        address_to_pool_distributions = defaultdict(list)
        lease_addresses = address_to_leases.keys()
        for tx in cold_wallet_transactions:
            if (tx['type'] == TRANSACTION_CODE['Payment'] and
                    tx['proofs'][0]['address'] == cold_wallet_address):
                address = tx['recipient']
                if address not in lease_addresses:
                    continue

                pool_distribution = PoolDistribution(tx['id'], tx['amount'], tx['fee'], tx['height'])
                address_to_pool_distributions[address].append(pool_distribution)

        return address_to_pool_distributions