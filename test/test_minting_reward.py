'''Unit tests for the MintingReward class. See unit_test_lease_calculations.ods
for a sense of where these numbers are coming from.
'''

from decimal import Decimal

from pyvsystems_rewards.address import Address
from pyvsystems_rewards.lease import Lease
from pyvsystems_rewards.minting_reward import MintingReward


def test_operation_fee():
    lease_one = Lease('lease_one_id', 'address_one', 3300000000, 1)
    lease_two = Lease('lease_two_id', 'address_one', 50000000000, 50)
    lease_three = Lease('lease_three_id', 'address_one', 50000000000, 125)
    active_leases = [lease_one, lease_two, lease_three]

    minting_reward = MintingReward('transaction_id', 3600000000, 3000, active_leases, Decimal('0.18'))

    assert minting_reward.operation_fee == 648000000


def test_interest():
    lease_one = Lease('lease_one_id', 'address_one', 3300000000, 1)
    lease_two = Lease('lease_two_id', 'address_one', 50000000000, 50)
    lease_three = Lease('lease_three_id', 'address_one', 50000000000, 125)
    active_leases = [lease_one, lease_two, lease_three]
    
    minting_reward = MintingReward('transaction_id', 3600000000, 3000, active_leases, Decimal('0.18'))

    assert minting_reward.interest == 2952000000


def test_interest_for_lease():
    lease_one = Lease('lease_one_id', 'address_one', 3300000000, 1)
    lease_two = Lease('lease_two_id', 'address_one', 50000000000, 50)
    lease_three = Lease('lease_three_id', 'address_one', 50000000000, 125)
    active_leases = [lease_one, lease_two, lease_three]
    
    minting_reward = MintingReward('transaction_id', 3600000000, 3000, active_leases, Decimal('0.18'))

    assert minting_reward.interest_for_lease(lease_one) == 97012713
    assert minting_reward.interest_for_lease(lease_two) == 1445873390
    assert minting_reward.interest_for_lease(lease_three) == 1409113897


def test_interest_for_address():
    lease_one = Lease('lease_one_id', 'address_one', 3300000000, 1)
    lease_two = Lease('lease_two_id', 'address_one', 50000000000, 50)
    lease_three = Lease('lease_three_id', 'address_two', 50000000000, 125)
    active_leases = [lease_one, lease_two, lease_three]

    minting_reward = MintingReward('transaction_id', 3600000000, 3000, active_leases, Decimal('0.18'))

    address = Address('address_one')
    address.start_lease(lease_one)
    address.start_lease(lease_two)

    assert minting_reward.interest_for_address(address) == 97012713 + 1445873390
