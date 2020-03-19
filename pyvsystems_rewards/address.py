class Address:
    def __init__(self, address):
        self.address = address
        self._leases = {}
        self._pool_distributions = {}
        self._minting_rewards = {}
        self.total_interest = 0
        self.total_pool_distribution = 0

    def leases(self):
        return self._leases.values()

    def start_lease(self, lease):
        self._leases[lease.lease_id] = lease

    def stop_lease(self, lease_id, height):
        lease = self._leases[lease_id]
        lease.stop_height = height

    def active_leases(self, height):
        return [l for l in self.leases() if l.is_active(height)]

    def inactive_leases(self, height):
        return [l for l in self.leases() if not l.is_active(height)]

    def is_active(self, height):
        return bool(self.active_leases(height))

    def add_minting_reward(self, minting_reward):
        self._minting_rewards[minting_reward.minting_reward_id] = minting_reward
        self.total_interest += minting_reward.interest_for_address(self)
        for lease in self.active_leases(minting_reward.height):
            lease.add_minting_reward(minting_reward)

    def minting_rewards(self):
        return self._minting_rewards.values()

    def pool_distributions(self):
        return self._pool_distributions.values()

    def add_pool_distribution(self, pool_distribution):
        self._pool_distributions[pool_distribution.pool_distribution_id] = pool_distribution
        self.total_pool_distribution += pool_distribution.amount + pool_distribution.fee

    def total_interest_owed(self):
        return self.total_interest - self.total_pool_distribution
