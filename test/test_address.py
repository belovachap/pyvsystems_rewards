from decimal import Decimal

from pyvsystems_rewards.address import Address
from pyvsystems_rewards.lease import Lease
from pyvsystems_rewards.minting_reward import MintingReward


def test_add_minting_reward():
    '''Check that adding a minting reward to an address increments totals.'''
    lease_one = Lease('lease_one_id', 'address_one', 3300000000, 1)
    lease_two = Lease('lease_two_id', 'address_one', 50000000000, 50)
    lease_three = Lease('lease_three_id', 'address_two', 50000000000, 125)
    active_leases = [lease_one, lease_two, lease_three]

    minting_reward = MintingReward(
        minting_reward_id='transaction_id',
        timestamp=1575966231000000000,
        amount=3600000000,
        height=3000,
        active_leases=active_leases,
        operation_fee_percent=Decimal('0.18')
    )

    address = Address('address_one')
    address.start_lease(lease_one)
    address.start_lease(lease_two)

    assert address.total_interest == 0
    address.add_minting_reward(minting_reward)
    assert address.total_interest == 94303970 + 1428848015
