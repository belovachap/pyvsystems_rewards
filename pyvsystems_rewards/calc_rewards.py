#!/usr/bin/python3

'''
Run ./calc_rewards.py to generate a report of your supernode's rewards and
responsibilities ;)

<3,
Peercoin
'''

from collections import defaultdict, OrderedDict
from datetime import datetime

import requests


API_URL = 'http://wallet.v.systems/api' # mainnet
COLD_WALLET_ADDRESS = 'ARMb6m8PLr45oGAooYzYnxb8cSC112B7KCp' # mainnet
HOT_WALLET_ADDRESS = 'AR6Gt6GXq7yPnXoFek83sQ6sCekQWbBj7YK' # mainnet
HTML_OUTPUT_DIRECTORY = 'html_output'
OPERATION_FEE_PERCENT = 0.18

HEIGHT = requests.get(API_URL + '/blocks/height').json()['height']
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
UTC_NOW = datetime.utcnow()


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
    def __init__(self, minting_reward_id, amount, height, address_to_leases):
        self.minting_reward_id = minting_reward_id
        self.amount = amount
        self.height = height
        self.lease_to_rewards = {}

        active_leases = get_active_leases(address_to_leases, height)
        total_mab = sum([lease.get_mab(height) for lease in active_leases])
        for lease in active_leases:
            interest = self.amount * (lease.get_mab(height) / total_mab)
            operation_fee = interest * OPERATION_FEE_PERCENT
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


def get_transactions(address):
    '''Returns all of the transactions associated with an address in increasing
    block height order.'''
    descending_transactions = OrderedDict()
    offset = 0
    LIMIT = 10000
    while True:
        transactions = requests.get(
            API_URL + '/transactions/list',
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


def get_minting_rewards(cold_wallet_transactions, address_to_leases):
    minting_rewards = []
    for tx in cold_wallet_transactions:
        if tx['type'] == TRANSACTION_CODE['MintingTransaction']:
            minting_rewards.append(
                MintingReward(
                    tx['id'],
                    tx['amount'],
                    tx['height'],
                    address_to_leases
                )
            )

    return minting_rewards


def format_as_vsys(amount):
    amount = int(amount)
    whole = int(amount / 100000000)
    fraction = amount % 100000000
    return f'{whole}.{str(fraction).ljust(8, "0")}'


def create_minting_reward_pages(minting_rewards):
    lease_to_total_rewards = {}
    for minting_reward in minting_rewards:
        with open(f'{HTML_OUTPUT_DIRECTORY}/{minting_reward.minting_reward_id}.html', "w") as f:
            f.write("<html>")
            f.write('''
                <style>
                    table {
                        border-collapse: collapse;
                    }

                    table, th, td {
                        border: 1px solid black;
                    }

                    td {
                        padding: 10px;
                    }

                    .monospace {
                        font-family: "Courier New", Courier, monospace;
                    }

                    td.monospace {
                        text-align: right;
                    }
                </style>
            ''')
            f.write("<body>")
            f.write("<p><em>THIS IS DEVELOPMENT LEVEL SOFTWARE FOR DEVELOPERS ONLY!</em></p>")
            f.write(f'<h1>Peercoin VPool Rewards</h1>')
            f.write(f'<h2>Minting Reward <span class="monospace">{minting_reward.minting_reward_id}</span></h2>')
            f.write(f'<p>Page Updated: <span class="monospace">{UTC_NOW}</span></p>')
            f.write(f'<p>Minted Block Height: <span class="monospace">{minting_reward.height}</span></p>')
            f.write(f'<p>Minting Reward Amount: <span class="monospace">{format_as_vsys(minting_reward.amount)}</span></p>')
            f.write(f'<p>Total Operation Fee: <span class="monospace">{format_as_vsys(minting_reward.get_total_operation_fee())}</span></p>')
            f.write(f'<p>Total Interest: <span class="monospace">{format_as_vsys(minting_reward.get_total_interest())}</span></p>')

            f.write(f'<h2>Leases</h2>')
            f.write("<table>")
            f.write("<tr><th>Address</th><th>Lease ID</th><th>Amount</th><th>MAB</th><th>Operation Fee</th><th>Interest</th></tr>")
            for lease, (operation_fee, interest) in minting_reward.lease_to_rewards.items():
                o, i = lease_to_total_rewards.get(lease, (0.0, 0.0))
                lease_to_total_rewards[lease] = (o + operation_fee, i + interest)

                f.write('''
                        <tr>
                            <td class="monospace">{}</td>
                            <td class="monospace">{}</td>
                            <td class="monospace">{}</td>
                            <td class="monospace">{}</td>
                            <td class="monospace">{}</td>
                            <td class="monospace">{}</td>
                        </tr>
                    '''.format(
                        f'<a href="{lease.address}.html">{lease.address}</a>',
                        lease.lease_id,
                        format_as_vsys(lease.amount),
                        format_as_vsys(lease.get_mab(minting_reward.height)),
                        format_as_vsys(operation_fee),
                        format_as_vsys(interest),
                    )
                )

            f.write("</table>")
            f.write("</body></html>")

    return lease_to_total_rewards


def get_address_to_pool_distributions(cold_wallet_transactions, address_to_leases):
    address_to_pool_distributions = defaultdict(list)
    lease_addresses = address_to_leases.keys()
    for tx in cold_wallet_transactions:
        if (tx['type'] == TRANSACTION_CODE['Payment'] and
                tx['proofs'][0]['address'] == COLD_WALLET_ADDRESS):
            address = tx['recipient']
            if address not in lease_addresses:
                continue

            pool_distribution = PoolDistribution(tx['id'], tx['amount'], tx['fee'], tx['height'])
            address_to_pool_distributions[address].append(pool_distribution)

    return address_to_pool_distributions


def create_address_pages(
    address_to_leases,
    lease_to_total_rewards,
    address_to_pool_distributions
):
    address_to_totals = {}
    for address in address_to_leases:
        pool_distributions = address_to_pool_distributions[address]
        address_total_pool_distribution = sum(
            map(lambda x: x.amount + x.fee, pool_distributions)
        )

        leases = address_to_leases[address]
        address_total_operation_fee = 0.0
        address_total_interest = 0.0
        for lease in leases:
            o, i = lease_to_total_rewards.get(lease, (0.0, 0.0))
            address_total_operation_fee += o
            address_total_interest += i

        interest_owed = address_total_interest - address_total_pool_distribution

        address_to_totals[address] = (
            address_total_operation_fee,
            address_total_interest,
            address_total_pool_distribution,
            interest_owed,
        )

        with open(f'{HTML_OUTPUT_DIRECTORY}/{address}.html', "w") as f:
            f.write("<html>")
            f.write('''
                <style>
                    table {
                        border-collapse: collapse;
                    }

                    table, th, td {
                        border: 1px solid black;
                    }

                    td {
                        padding: 10px;
                    }

                    .monospace {
                        font-family: "Courier New", Courier, monospace;
                    }

                    td.monospace {
                        text-align: right;
                    }
                </style>
            ''')
            f.write("<body>")
            f.write("<p><em>THIS IS DEVELOPMENT LEVEL SOFTWARE FOR DEVELOPERS ONLY!</em></p>")
            f.write(f'<h1>Peercoin VPool Rewards</h1>')
            f.write(f'<h2>Address <span class="monospace">{address}</span></h2>')
            f.write(f'<p>Page Updated: <span class="monospace">{UTC_NOW}</span></p>')
            f.write(f'<p>Current Block Height: <span class="monospace">{HEIGHT}</span></p>')
            f.write(f'<p>Total Operation Fee: <span class="monospace">{format_as_vsys(address_total_operation_fee)}</span></p>')
            f.write(f'<p>Total Interest: <span class="monospace">{format_as_vsys(address_total_interest)}</span></p>')
            f.write(f'<p>Total Pool Distribution: <span class="monospace">{format_as_vsys(address_total_pool_distribution)}</span></p>')
            f.write(f'<p>Interest Owed: <span class="monospace">{format_as_vsys(interest_owed)}</span></p>')

            f.write(f'<h2>Leases</h2>')
            f.write('<table>')
            f.write(
                '''
                    <tr>
                        <th>Active</th>
                        <th>Lease ID</th>
                        <th>Amount</th>
                        <th>Start Height</th>
                        <th>Stop Height</th>
                        <th>Total Operation Fee</th>
                        <th>Total Interest</th>
                    </tr>
                '''
            )
            for lease in leases:
                o, i = lease_to_total_rewards.get(lease, (0.0, 0.0))
                f.write('''
                        <tr>
                            <td>{}</td>
                            <td class="monospace">{}</td>
                            <td class="monospace">{}</td>
                            <td class="monospace">{}</td>
                            <td class="monospace">{}</td>
                            <td class="monospace">{}</td>
                            <td class="monospace">{}</td>
                        </tr>
                    '''.format(
                        lease.is_active(HEIGHT),
                        lease.lease_id,
                        format_as_vsys(lease.amount),
                        lease.start_height,
                        lease.stop_height,
                        format_as_vsys(o),
                        format_as_vsys(i),
                    )
                )

            f.write('</table>')

            f.write(f'<h2>Pool Distributions</h2>')
            f.write('<table>')
            f.write('<tr><th>Height</th><th>Pool Distribution ID</th><th>Amount</th><th>Fee</th></tr>')
            for pool_distribution in pool_distributions:
                f.write(
                    '''
                        <tr>
                            <td class="monospace">{}</td>
                            <td class="monospace">{}</td>
                            <td class="monospace">{}</td>
                            <td class="monospace">{}</td>
                        </tr>
                    '''.format(
                        pool_distribution.height,
                        pool_distribution.pool_distribution_id,
                        format_as_vsys(pool_distribution.amount),
                        format_as_vsys(pool_distribution.fee),
                    )
                )

            f.write('</table>')
            f.write('</body></html>')

    return address_to_totals


def create_index_page(
    address_to_leases,
    minting_rewards,
    address_to_totals
):
    total_minting_reward = sum([reward.amount for reward in minting_rewards])

    total_operation_fee = 0.0
    total_interest = 0.0
    total_pool_distribution = 0.0
    total_interest_owed = 0.0
    for (fee, interest, dist, owed) in address_to_totals.values():
        total_operation_fee += fee
        total_interest += interest
        total_pool_distribution += dist
        total_interest_owed += owed

    with open(f'{HTML_OUTPUT_DIRECTORY}/index.html', 'w') as f:
        f.write('<html>')
        f.write(
            '''
                <style>
                    table {
                        border-collapse: collapse;
                    }

                    table, th, td {
                        border: 1px solid black;
                    }

                    td {
                        padding: 10px;
                    }

                    .monospace {
                        font-family: "Courier New", Courier, monospace;
                    }

                    td.monospace {
                        text-align: right;
                    }
                </style>
            '''
        )
        f.write('<body>')
        f.write('<p><em>THIS IS DEVELOPMENT LEVEL SOFTWARE FOR DEVELOPERS ONLY!</em></p>')
        f.write(f'<h1>Peercoin VPool Rewards</h1>')
        f.write(f'<p>Page Updated: <span class="monospace">{UTC_NOW}</span></p>')
        f.write(f'<p>Current Block Height: <span class="monospace">{HEIGHT}</span></p>')
        f.write(f'<p>Total Minting Reward: <span class="monospace">{format_as_vsys(total_minting_reward)}</span></p>')
        f.write(f'<p>Total Operation Fee: <span class="monospace">{format_as_vsys(total_operation_fee)}</span></p>')
        f.write(f'<p>Total Interest: <span class="monospace">{format_as_vsys(total_interest)}</span></p>')
        f.write(f'<p>Total Pool Distribution: <span class="monospace">{format_as_vsys(total_pool_distribution)}</span></p>')
        f.write(f'<p>Interest Owed: <span class="monospace">{format_as_vsys(total_interest_owed)}</span></p>')

        f.write('<h2>Recent Minted Blocks</h2>')
        f.write('<table>')
        f.write('<tr><th>Height</th><th>Minting Reward Amount</th><th>Operation Fee</th><th>Interest</th></tr>')
        for minting_reward in minting_rewards[-10:]:
            f.write(
                '''
                    <tr>
                        <td class="monospace">{}</td>
                        <td class="monospace">{}</td>
                        <td class="monospace">{}</td>
                        <td class="monospace">{}</td>
                    </tr>
                '''.format(
                    f'<a href="{minting_reward.minting_reward_id}.html">{minting_reward.height}</a>',
                    format_as_vsys(minting_reward.amount),
                    format_as_vsys(minting_reward.get_total_operation_fee()),
                    format_as_vsys(minting_reward.get_total_interest()),
                )
            )

        f.write('</table>')

        f.write('<h2>Lease Addresses</h2>')
        f.write('<table>')
        f.write('<tr><th>Address</th><th>Operation Fee</th><th>Interest</th><th>Pool Distribution</th><th>Owed</th></tr>')
        for address, (fee, interest, dist, owed) in address_to_totals.items():
            f.write(
                '''
                    <tr>
                        <td class="monospace">{}</td>
                        <td class="monospace">{}</td>
                        <td class="monospace">{}</td>
                        <td class="monospace">{}</td>
                        <td class="monospace">{}</td>
                    </tr>
                '''.format(
                    f'<a href="{address}.html">{address}</a>',
                    format_as_vsys(fee),
                    format_as_vsys(interest),
                    format_as_vsys(dist),
                    format_as_vsys(owed),
                )
            )

        f.write('</table>')
        f.write("</body></html>")


if __name__ == '__main__':
    hot_wallet_transactions = get_transactions(HOT_WALLET_ADDRESS)
    address_to_leases = get_address_to_leases(hot_wallet_transactions)

    cold_wallet_transactions = get_transactions(COLD_WALLET_ADDRESS)
    minting_rewards = get_minting_rewards(
        cold_wallet_transactions,
        address_to_leases
    )

    lease_to_total_rewards = create_minting_reward_pages(minting_rewards)

    address_to_pool_distributions = get_address_to_pool_distributions(
        cold_wallet_transactions,
        address_to_leases
    )

    address_to_totals = create_address_pages(
        address_to_leases,
        lease_to_total_rewards,
        address_to_pool_distributions
    )

    create_index_page(
        address_to_leases,
        minting_rewards,
        address_to_totals
    )
