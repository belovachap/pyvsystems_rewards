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
