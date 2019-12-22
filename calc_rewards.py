import requests
import functools
from collections import defaultdict, OrderedDict

distribution_percent = 0.82 # 100 - 18% fee
endpoint = "http://localhost:9922"
strattime = 1575964672001715000 # nanosecond timestamp
endtime = 1576741985294000000  # nanosecond timestamp

SUPERNODE_ADDRESS = "AU69hVSi1dgiVt8so8UiJbDA8xaHgZf5uqq"
REWARDS_ADDRESS = "AU4uSzCqHnq831RiK5HuYPTFYW2R27wbPAL"


def all_supernode_addresses():
    '''Returns the addresses in the supernode's wallet.'''
    return requests.get(endpoint + '/addresses').json()


def all_transactions_for_address(address):
    '''Returns all of the transactions associated with an address in increasing
    block height order.'''
    descending_trnasactions = OrderedDict()
    offset = 0
    LIMIT = 10000
    while True:
        transactions = requests.get(
            endpoint + '/transactions/list',
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


if __name__ == "__main__":
    print(f"SuperNode address {SUPERNODE_ADDRESS} has {len(all_transactions_for_address(SUPERNODE_ADDRESS))} txs.")
    print(f"Rewards address {REWARDS_ADDRESS} has {len(all_transactions_for_address(REWARDS_ADDRESS))} txs.")


# def rewards(startts, endts):
#     total = (endts-startts)/1e9/60*3600000000*distribution_percent

#     def getAge(start, end):
#         return max(0, min(endts, end) - max(startts, start))

#     leaseAgeDict = {k: v['amount'] * getAge(v['start'], v['end']) for k, v in leaseDict.items()}
#     totalLeaseAge = sum(leaseAgeDict.values())

#     return {k: {
#         'address': leaseDict[k]['address'],
#         'amount': int(v * total / totalLeaseAge),
#         'remark': leaseDict[k]['amount']} for k, v in leaseAgeDict.items()}

# ### need to get further transactions in future
# a = requests.get(endpoint + '/transactions/list?address=AR6Gt6GXq7yPnXoFek83sQ6sCekQWbBj7YK&txType=3&limit=10000&offset=0')
# leases = a.json()['transactions']
# b = requests.get(endpoint + '/transactions/list?address=AR6Gt6GXq7yPnXoFek83sQ6sCekQWbBj7YK&txType=4&limit=10000&offset=0')
# cancels = b.json()['transactions']

# cancelDict = defaultdict(int, { x['leaseId']:x['timestamp'] for x in cancels })
# leaseDict = { x['id']: {
#     'start': x['timestamp'],
#     'end': cancelDict[x['id']] or 1999999999999000000,
#     'amount': x['amount'],
#     'address': x['proofs'][0]['address']
# } for x in leases }

# rewdic = rewards(strattime, endtime)
# distributionDic = functools.reduce(
#     lambda x, y: x.update({ y['address']: (x[y['address']] + y['amount']/1e8) }) or x,
#     rewdic.values(), defaultdict(int))

# res = {x: y for x, y in distributionDic.items() if y > 0.1}

