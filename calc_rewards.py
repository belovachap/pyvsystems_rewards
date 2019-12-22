import requests
import functools
from collections import defaultdict

distribution_percent = 0.82 # 100 - 18% fee
endpoint = "http://wallet.v.systems/api"
strattime = 1575964672001715000 # nanosecond timestamp
endtime = 1576741985294000000  # nanosecond timestamp


def rewards(startts, endts):
    total = (endts-startts)/1e9/60*3600000000*distribution_percent

    def getAge(start, end):
        return max(0, min(endts, end) - max(startts, start))

    leaseAgeDict = {k: v['amount'] * getAge(v['start'], v['end']) for k, v in leaseDict.items()}
    totalLeaseAge = sum(leaseAgeDict.values())

    return {k: {
        'address': leaseDict[k]['address'],
        'amount': int(v * total / totalLeaseAge),
        'remark': leaseDict[k]['amount']} for k, v in leaseAgeDict.items()}


### need to get further transactions in future
a = requests.get(endpoint + '/transactions/list?address=AR6Gt6GXq7yPnXoFek83sQ6sCekQWbBj7YK&txType=3&limit=10000&offset=0')
leases = a.json()['transactions']
b = requests.get(endpoint + '/transactions/list?address=AR6Gt6GXq7yPnXoFek83sQ6sCekQWbBj7YK&txType=4&limit=10000&offset=0')
cancels = b.json()['transactions']

cancelDict = defaultdict(int, { x['leaseId']:x['timestamp'] for x in cancels })
leaseDict = { x['id']: {
    'start': x['timestamp'],
    'end': cancelDict[x['id']] or 1999999999999000000,
    'amount': x['amount'],
    'address': x['proofs'][0]['address']
} for x in leases }

rewdic = rewards(strattime, endtime)
distributionDic = functools.reduce(
    lambda x, y: x.update({ y['address']: (x[y['address']] + y['amount']/1e8) }) or x,
    rewdic.values(), defaultdict(int))

res = {x: y for x, y in distributionDic.items() if y > 0.1}
