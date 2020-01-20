from collections import defaultdict, OrderedDict

import requests


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


class Lease:
    def __init__(self, lease_id, address, amount, start_height, stop_height=None):
        self.lease_id = lease_id
        self.address = address
        self.amount = amount
        self.start_height = start_height
        self.stop_height = stop_height

    def is_active(self, height):
        if height < self.start_height:
            return False

        return self.stop_height is None or height < self.stop_height

    def get_mab(self, height):
        if not self.is_active(height):
            return None

        mab_modifier = (height - self.start_height) / float(MAB_MATURES_AFTER_BLOCKS)
        mab_modifier = min(1.0, mab_modifier)
        return mab_modifier * self.amount

    # The following functions are required to use the Lease as a key in
    # dictionaries.
    def __hash__(self):
        return hash(self.lease_id)

    def __eq__(self, other):
        return self.lease_id == other.lease_id

    def __ne__(self, other):
        return not(self == other)


def get_active_leases(address_to_leases, height):
    active_leases = []
    for leases in address_to_leases.values():
        for lease in leases:
            if lease.is_active(height):
                active_leases.append(lease)

    return active_leases


class MintingReward:
    def __init__(
        self,
        minting_reward_id,
        amount,
        height,
        address_to_leases,
        operation_fee_percent
    ):
        self.minting_reward_id = minting_reward_id
        self.amount = amount
        self.height = height
        self.operation_fee_percent = operation_fee_percent
        self.lease_to_rewards = {}

        active_leases = get_active_leases(address_to_leases, height)
        total_mab = sum([lease.get_mab(height) for lease in active_leases])
        for lease in active_leases:
            interest = self.amount * (lease.get_mab(height) / total_mab)
            operation_fee = interest * self.operation_fee_percent
            interest -= operation_fee
            self.lease_to_rewards[lease] = (operation_fee, interest)

    def get_total_operation_fee(self):
        total_operation_fee = 0.0
        for (operation_fee, _) in self.lease_to_rewards.values():
            total_operation_fee += operation_fee

        return total_operation_fee

    def get_total_interest(self):
        total_interest = 0.0
        for (_, interest) in self.lease_to_rewards.values():
            total_interest += interest

        return total_interest


class PoolDistribution:
    def __init__(self, pool_distribution_id, amount, fee, height):
        self.pool_distribution_id = pool_distribution_id
        self.amount = amount
        self.fee = fee
        self.height = height


def get_transactions(api_url, address):
    '''Returns all of the transactions associated with an address in increasing
    block height order.'''
    descending_transactions = OrderedDict()
    offset = 0
    LIMIT = 10000
    while True:
        transactions = requests.get(
            api_url + '/transactions/list',
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


def get_address_to_leases(hot_wallet_transactions):
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
