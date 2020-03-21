from decimal import Decimal


class MintingReward:
    def __init__(
        self,
        minting_reward_id,
        timestamp,
        amount,
        height,
        active_leases,
        operation_fee_percent
    ):
        self.minting_reward_id = minting_reward_id
        self.timestamp = timestamp
        self.amount = amount
        self.height = height
        self.operation_fee = int(amount * operation_fee_percent)
        self.interest = amount - self.operation_fee
        self.leases = active_leases

        # Stage one of distribution.
        total_lease_amount =  Decimal(self.get_total_lease_amount())
        self._lease_to_interest = {}
        stage_one_interest = 0
        for lease in self.leases:
            i = int(self.interest * (Decimal(lease.amount) / total_lease_amount))
            stage_one_interest += i
            self._lease_to_interest[lease] = i

        # Stage two of distribution.
        remaining_interest = self.interest - stage_one_interest
        ordered_leases = sorted(self.leases, key=lambda lease: lease.lease_id)
        ordered_leases = sorted(ordered_leases, key=lambda lease: lease.start_height)
        for lease in ordered_leases:
            if remaining_interest <= 0:
                break

            self._lease_to_interest[lease] += 1
            remaining_interest -= 1

    def get_total_lease_amount(self):
        return sum([lease.amount for lease in self.leases])

    def interest_for_lease(self, lease):
        return self._lease_to_interest[lease]

    def interest_for_address(self, address):
        interest = 0
        for lease in self._lease_to_interest:
            if lease.address == address.address:
                interest += self.interest_for_lease(lease)

        return interest
