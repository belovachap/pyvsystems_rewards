from pyvsystems_rewards.lease import Lease


def test_ongoing_lease_is_active():
    lease = Lease('lease_id', 'address', 100000000, 10)
    assert lease.is_active(9) == False
    assert lease.is_active(10) == True
    assert lease.is_active(11) == True

def test_closed_lease_is_active():
    lease = Lease('lease_id', 'address', 100000000, 10, 20)
    assert lease.is_active(9) == False
    assert lease.is_active(10) == True
    assert lease.is_active(19) == True
    assert lease.is_active(20) == False
    assert lease.is_active(21) == False
