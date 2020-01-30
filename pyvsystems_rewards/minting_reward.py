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

        # Stage one of distribution.
        total_mab = sum([lease.get_mab(height) for lease in active_leases])
        self._lease_to_interest = {}
        stage_one_interest = 0
        for lease in active_leases:
            i = int(self.interest * (Decimal(lease.get_mab(height)) / Decimal(total_mab)))
            stage_one_interest += i
            self._lease_to_interest[lease] = i

        # Stage two of distribution.
        remaining_interest = self.interest - stage_one_interest
        ordered_leases = sorted(active_leases, key=lambda lease: lease.lease_id)
        ordered_leases = sorted(ordered_leases, key=lambda lease: lease.start_height)
        for lease in ordered_leases:
            if remaining_interest <= 0:
                break

            self._lease_to_interest[lease] += 1
            remaining_interest -= 1

    def interest_for_lease(self, lease):
        return self._lease_to_interest[lease]

    def interest_for_address(self, address):
        interest = 0
        for lease in self._lease_to_interest:
            if lease.address == address.address:
                interest += self.interest_for_lease(lease)

        return interest
