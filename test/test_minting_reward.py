from pyvsystems_rewards.address import Address
from pyvsystems_rewards.lease import Lease
from pyvsystems_rewards.minting_reward import MintingReward


def test_interest_for_lease():
    lease_one = Lease('lease_one_id', 'address_one', 3300000000, 1)
    lease_two = Lease('lease_two_id', 'address_one', 50000000000, 50)
    lease_three = Lease('lease_three_id', 'address_one', 50000000000, 125)
    active_leases = [lease_one, lease_two, lease_three]
    
    minting_reward = MintingReward('transaction_id', 3600000000, 1000, active_leases, 0.18)

    # TODO: Show calculations for this in a comment here... I don't think we've
    # completely nailed this down yet.
    
    assert minting_reward.interest_for_lease(lease_one) == 102931761.76429215
    assert minting_reward.interest_for_lease(lease_two) == 1483076617.163793
    assert minting_reward.interest_for_lease(lease_three) == 1365991621.0719147


def test_interest_for_address():
    lease_one = Lease('lease_one_id', 'address_one', 3300000000, 1)
    lease_two = Lease('lease_two_id', 'address_one', 50000000000, 50)
    lease_three = Lease('lease_three_id', 'address_two', 50000000000, 125)
    active_leases = [lease_one, lease_two, lease_three]

    minting_reward = MintingReward('transaction_id', 3600000000, 1000, active_leases, 0.18)

    address = Address('address_one')
    address.start_lease(lease_one)
    address.start_lease(lease_two)

    # TODO: Show calculations for this in a comment here... I don't think we've
    # completely nailed this down yet. Although, if you believe the math in the
    # previous test the explaination here is just that we add the lease interest
    # together.

    assert minting_reward.interest_for_address(address) == 1586008378.9280853
