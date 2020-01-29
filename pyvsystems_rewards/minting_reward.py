from decimal import Decimal


class MintingReward:
    def __init__(
        self,
        minting_reward_id,
        amount,
        height,
        active_leases,
        operation_fee_percent
    ):
        self.minting_reward_id = minting_reward_id
        self.amount = amount
        self.height = height
        self.operation_fee = int(amount * operation_fee_percent)
        self.interest = amount - self.operation_fee

        total_mab = sum([lease.get_mab(height) for lease in active_leases])
        self._lease_to_interest = {}
        for lease in active_leases:
            i = int(self.interest * (Decimal(lease.get_mab(height)) / Decimal(total_mab)))
            self._lease_to_interest[lease] = i

    def interest_for_lease(self, lease):
        return self._lease_to_interest[lease]

    def interest_for_address(self, address):
        interest = 0
        for lease in self._lease_to_interest:
            if lease.address == address.address:
                interest += self.interest_for_lease(lease)

        return interest
