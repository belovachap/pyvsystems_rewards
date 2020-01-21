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
        self.operation_fee_percent = operation_fee_percent
        self._lease_to_interest = {}
        self._lease_to_operation_fee = {}

        total_mab = sum([lease.get_mab(height) for lease in active_leases])
        for lease in active_leases:
            interest = self.amount * (lease.get_mab(height) / total_mab)
            operation_fee = interest * self.operation_fee_percent
            interest -= operation_fee
            self._lease_to_interest[lease] = interest
            self._lease_to_operation_fee[lease] = operation_fee

    def operation_fee_for_lease(self, lease):
        return self._lease_to_operation_fee[lease]

    def operation_fee_for_address(self, address):
        operation_fee = 0.0
        import pdb; pdb.set_trace()

        for lease in self._lease_to_operation_fee:
            if lease.address == address.address:
                operation_fee += self.operation_fee_for_lease(lease)

        return operation_fee

    def operation_fee(self):
        operation_fee = 0.0
        for lease_operation_fee in self._lease_to_operation_fee.values():
            operation_fee += lease_operation_fee

        return operation_fee

    def interest_for_lease(self, lease):
        return self._lease_to_interest[lease]

    def interest_for_address(self, address):
        interest = 0.0
        for lease in self._lease_to_interest:
            if lease.address == address.address:
                interest += self.interest_for_lease(lease)

        return interest

    def interest(self):
        interest = 0.0
        for lease_interst in self._lease_to_interst.values():
            interest += lease_interst

        return interest
