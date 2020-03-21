from decimal import Decimal

class Lease:

    def __init__(self, lease_id, address, amount, start_height, stop_height=None):
        self.lease_id = lease_id
        self.address = address
        self.amount = amount
        self.start_height = start_height
        self.stop_height = stop_height
        self.total_interest = 0

    def is_active(self, height):
        if height < self.start_height:
            return False

        return self.stop_height is None or height < self.stop_height

    def add_minting_reward(self, minting_reward):
        self.total_interest += minting_reward.interest_for_lease(self)

    # The following functions are required to use the Lease as a key in
    # dictionaries.
    def __hash__(self):
        return hash(self.lease_id)

    def __eq__(self, other):
        return self.lease_id == other.lease_id

    def __ne__(self, other):
        return not(self == other)
