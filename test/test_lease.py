from pyvsystems_rewards import Lease

def test_lease_active():
	lease = Lease()
	assert lease.is_active(1000)
