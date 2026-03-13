class MultiPaxos:
    """Multi-Paxos strategy: supports multiple sequential consensus decisions."""

    def __init__(self, node):
        self.node = node
        self.log = {}       # slot -> chosen value
        self.next_slot = 1  # next available slot

    async def propose(self, value: str, slot: int = None) -> bool:
        """Propose a value for the next available slot."""
        if slot is None:
            slot = self.next_slot
            self.next_slot += 1

        # delegate to node's Paxos coordinator
        ok = await self.node.coordinate(value, slot=slot)

        if ok:
            self.log[slot] = value
        return ok

    def get_log(self) -> dict:
        """Return the current replicated log."""
        return dict(self.log)

    def is_consensus_reached(self, slot: int | None = None) -> bool:
        """
        Returns True if consensus has been reached for the given slot,
        or for all known slots if no slot is specified.
        """
        # Check in-memory log first
        if slot is not None:
            # Check if this slot is decided in memory
            if slot in self.log:
                return True

            # Check persistent storage
            if hasattr(self.node, "storage") and self.node.storage is not None:
                decided = self.node.storage.get_decision(slot)
                return decided is not None

            return False

        # If slot not specified — check if all prior slots are decided
        last_slot = self.next_slot - 1
        if last_slot <= 0:
            return False  # nothing proposed yet

        # Check all slots up to current next_slot
        for s in range(1, last_slot + 1):
            if s not in self.log:
                if hasattr(self.node, "storage") and self.node.storage is not None:
                    decided = self.node.storage.get_decision(s)
                    if not decided:
                        return False
                else:
                    return False

        return True
