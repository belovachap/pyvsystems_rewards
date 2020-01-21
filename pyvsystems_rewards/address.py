class Address:
    def __init__(self, address):
        self.address = address
        self.leases = []
        self.minting_rewards = []
        self.pool_distributions = []

    def active_leases(self, height):
        return [l for l in self.leases if l.is_active(height)]

    def inactive_leases(self, height):
        return [l for l in self.leases if not l.is_active(height)]
