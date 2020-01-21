class MintingReward:
    def __init__(
        self,
        minting_reward_id,
        amount,
        height,
        address_to_leases,
        operation_fee_percent
    ):
        self.minting_reward_id = minting_reward_id
        self.amount = amount
        self.height = height
        self.operation_fee_percent = operation_fee_percent
        self.lease_to_rewards = {}

        active_leases = get_active_leases(address_to_leases, height)
        total_mab = sum([lease.get_mab(height) for lease in active_leases])
        for lease in active_leases:
            interest = self.amount * (lease.get_mab(height) / total_mab)
            operation_fee = interest * self.operation_fee_percent
            interest -= operation_fee
            self.lease_to_rewards[lease] = (operation_fee, interest)

    def get_total_operation_fee(self):
        total_operation_fee = 0.0
        for (operation_fee, _) in self.lease_to_rewards.values():
            total_operation_fee += operation_fee

        return total_operation_fee

    def get_total_interest(self):
        total_interest = 0.0
        for (_, interest) in self.lease_to_rewards.values():
            total_interest += interest

        return total_interest
