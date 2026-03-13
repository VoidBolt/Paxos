# strategies/single_decree.py

class SingleDecreePaxos:
    """Single-decree Paxos strategy for one consensus value."""
    def __init__(self, node):
        self.node = node
        self.chosen_value = None
        self.proposal_id = None

    async def propose(self, value: str) -> bool:
        """Propose a value; returns True if consensus reached."""
        if self.chosen_value is not None:
            return True  # already chosen

        # Delegate to node's coordinator logic
        ok = await self.node.coordinate(value)
        if ok:
            self.chosen_value = value
        return ok

    def is_consensus_reached(self) -> bool:
        """
        Returns True if a consensus value has been chosen (either locally or persisted).
        """
        if self.chosen_value is not None:
            return True

        # Check persistent storage for decided value
        if hasattr(self.node, "storage") and self.node.storage is not None:
            latest = self.node.storage.get_latest_decision()
            return latest is not None

        return False
