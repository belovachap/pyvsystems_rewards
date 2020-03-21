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

    minting_reward = MintingReward(
        minting_reward_id='transaction_id',
        timestamp=1575966231000000000,
        amount=3600000000,
        height=3000,
        active_leases=active_leases,
        operation_fee_percent=Decimal('0.18')
    )

    assert minting_reward.operation_fee == 648000000


def test_interest():
    lease_one = Lease('lease_one_id', 'address_one', 3300000000, 1)
    lease_two = Lease('lease_two_id', 'address_one', 50000000000, 50)
    lease_three = Lease('lease_three_id', 'address_one', 50000000000, 125)
    active_leases = [lease_one, lease_two, lease_three]
    
    minting_reward = MintingReward(
        minting_reward_id='transaction_id',
        timestamp=1575966231000000000,
        amount=3600000000,
        height=3000,
        active_leases=active_leases,
        operation_fee_percent=Decimal('0.18')
    )

    assert minting_reward.interest == 2952000000


def test_interest_for_lease():
    lease_one = Lease('lease_one_id', 'address_one', 3300000000, 1)
    lease_two = Lease('lease_two_id', 'address_one', 50000000000, 50)
    lease_three = Lease('lease_three_id', 'address_one', 50000000000, 125)
    active_leases = [lease_one, lease_two, lease_three]
    
    minting_reward = MintingReward(
        minting_reward_id='transaction_id',
        timestamp=1575966231000000000,
        amount=3600000000,
        height=3000,
        active_leases=active_leases,
        operation_fee_percent=Decimal('0.18')
    )

    assert minting_reward.interest_for_lease(lease_one) == 94303970
    assert minting_reward.interest_for_lease(lease_two) == 1428848015
    assert minting_reward.interest_for_lease(lease_three) == 1428848015


def test_interest_for_address():
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

    assert minting_reward.interest_for_address(address) == 94303970 + 1428848015


def test_block_8089127():
    "A unit test built around Peercoin VPool's MintingReward at block 8089127."
    height = 8089127

    # (Lease ID, Address, Amount, Start Height, Stop Height)
    lease_data = [
        ('C9SMdjen9DxLTqQnu8htLFSzgH1u5EfNgdHPXXzdF58h', 'ARA3fc8tMNpGmutPFLh7iGNvB7meyJMVMRR', 540000000000, 7707545, None),
        ('4KNcUe8LfaURRQTyV4cE2z4d6rjHZdJBCU6HYbbgwyXx', 'ARQFQ3sfbihE9xP9mfNXVUQsLRrr9DyLova', 624998900000000, 7309618, None),
        ('6fheVZGzP2nGAgEFHYiW6qnYBALfaLa6tBqcbRwmDp3M', 'ARBB2JYAVM3eE26UiQpF3DLp9uDQCKDR7Gm', 400000000000000, 7309749, None),
        ('HBKvnv1SNhaYCdHyeGCBjZVwBw9ewzHYbSaLm3kMpMsJ', 'AR5n6YUbxeeWgwWwsKxQzyCegWy7rB4sXBM', 360000000000000, 7309757, None),
        ('CdDmWvWGyCFnjXVNNpdBSsM17K6nhm4B79xsR64Mu7Ga', 'AREhFuLAfJ3LupEMTcRAWLwkFP5VKWCr7Uw', 1520000000000000, 7309787, None),
        ('8KkvFZQCzTePPKp9gtfbeywXgRGQmzDQjF1Jjxw1TKJ8', 'ARBVoFeUJEYifbujKR6C9S6TGdCzjAAw47z', 1080000000000000, 7309814, None),
        ('6FhCYmRJrEQ7uoaGLsxi18mq32XAYg8xLjooM4QTUzM9', 'AR4hZNUwXQqHCWBsHpgGKJR5fLVDaxCxf1K', 339999600000000, 7456817, None),
        ('B7qpEA29f2iq4Ttm4951JieVUFzsHfrTFRRhoAGpYAuz', 'ARRMXakP4w56yVs1dywVyvA6vqgmRWxGCPC', 370000000000000, 7456904, None),
        ('5NfYLD3s69RaAHYD7p3BHCchJkXeNjg8eTRYZi2ox1SH', 'ARH91X1nyJLfq39Rz29kbq26YfpGbMwHE9o', 354999800000000, 7456914, None),
        ('EaPJW8NRtxzjPtXMZsbzr7W4ij1Qzpv4HEZE58yECWzf', 'ARDMJryY9ZVBqQq71bx7BErRMSZTutzpjTR', 1000000000000000, 7456926, None),
        ('FjVbs7dn4NKJ8WmY1dUGto1T72wBtDrFhXbqkckoERgL', 'ARDMJryY9ZVBqQq71bx7BErRMSZTutzpjTR', 800000000000000, 7782518, None),
        ('8fy6t576KouC97QyLwSUUd3dsFwQjeRtbjbszWGuC39N', 'ARDMJryY9ZVBqQq71bx7BErRMSZTutzpjTR', 600000000000000, 7782524, None),
        ('2YtFF4g11WHLqxNSksd8UZAsJUB35EsinnkERhx2XHYm', 'ARDMJryY9ZVBqQq71bx7BErRMSZTutzpjTR', 500000000000000, 7782541, None),
        ('7LSRKooU4JuEy6mDBshXtkGD29wnpdzA7758QDk7Kj5X', 'ARDYkoV7gT2YNro3KmX1skELNeBdaRwXoMM', 100000000000000, 7589163, None),
        ('6HJicNq7RxCjQg9e6C4C44D1MAKhwJDk7LvJd71qn9Hg', 'ARF58WawVMRFnDYLKx9qT3MXUR9ySXSKSad', 279999900000000, 7782469, None),
        ('8tmvDdnoANxhgC7EApeHX32RDN5jZw6zXbfwdHSPuYtw', 'AR3Ted9xt4wEYMFAxFez4xuo7QWKipCYPy4', 199999960000000, 7782479, None),
        ('3T12Fa4skf6m562rBYtQYHyMtvDyDBL9zKkELoKeMFjn', 'ARBWyE2Fab4h4hGvb8BbFNCMuAcEB7mnuyY', 198507400000000, 7782501, None),
        ('B6m6UkfE4QxBT4hweNGrWeAzfQg64TszLPFkVABiY4oo', 'ARDdLTCpKhaG6nhviFVtRmmZPhWVL5pekZC', 14500000000000, 7872337, None),
        ('ESR9cESaoeuXfEVJE6oGC5HL3khjnUUUS9HXENNWuEha', 'ARAcK1xHAeUq5Jge1AMpCvujGT8tFEYQhcV', 26100000000, 7912551, 8299241),
        ('9qgczgworw9sWg5gY6YU6a5crEWBZaC9x6EtYVQvAqFe', 'ARGvUpQVKd8c3SVCcKczESUoAEBfKm53ZoP', 16800000000, 7912554, 8325392),
        ('DnmmAfHHspr4sHFoYf4qwtXJNX7VJ29YBCJP3aZDduvB', 'ARAinSRNMM7MpB1neK7tBRbPyayA3FX7mSt', 15100000000, 7912557, 8126536),
        ('925YKL8oVYfPzovRvYXwpyLb7GmzAb75EUBe8u6BvA5B', 'AR7n6wGnavPJsLJr5s9NSZMKEBdJ812bTcz', 21100000000, 7912559, 8299333),
        ('A5Z79e3EUBPjxyd7JWKEfj6DvvvsfdHPGV2gFbpLTKx1', 'ARJEvXBbyBNmaPLkQ6D7tyQhess3JffzJk9', 120000000000000, 8088935, 9424076),
        ('5vcs7X5fWhDweBjWcpSRB9WRQEjEUxVLumgGonLh7nqJ', 'ARHLrAtZEn3idoCxbArmvxUpJDUWC7ydMjs', 1000000000000, 8088977, 8105964),
        ('Hiqa8Qpvik1czuY6Ka7ShjLk2ziWwYRRycervngkh3FV', 'ARALpfPRvZNwpeYWpe3zLivhq5Lsy1X7SAy', 9000000000000, 8088992, None),
        ('E731ukLpL9viTELRiYCpcgFuHPseotNzcKSh3fjGmdSA', 'ARHyBquEznSjSJWBEFPCsxrGPpih596TbVW', 20000000000000, 8089118, 8674511),
    ]

    address_ARHy = Address('ARHyBquEznSjSJWBEFPCsxrGPpih596TbVW')
    address_ARAL = Address('ARALpfPRvZNwpeYWpe3zLivhq5Lsy1X7SAy')

    leases = []
    for data in lease_data:
        lease = Lease(*data)
        assert lease.is_active(height)

        if lease.address == address_ARHy.address:
            address_ARHy.start_lease(lease)
        elif lease.address == address_ARAL.address:
            address_ARAL.start_lease(lease)

        leases.append(lease)

    minting_reward = MintingReward(
        minting_reward_id='EUhbqj5GytomcckGob5ZKNQCaEMcDUdcgJa8ziKDtACN',
        timestamp=1575966231999634871,
        amount=3600000000,
        height=height,
        active_leases=leases,
        operation_fee_percent=Decimal('0.18')
    )

    assert minting_reward.operation_fee == 648000000
    assert minting_reward.interest == 2952000000

    check_interest = 0
    for lease in leases:
        check_interest += minting_reward.interest_for_lease(lease)

    assert check_interest == minting_reward.interest

    interest_ARHy = minting_reward.interest_for_address(address_ARHy)
    interest_ARAL = minting_reward.interest_for_address(address_ARAL)

    assert interest_ARHy == 6638463
    assert interest_ARAL == 2987308
