from abc import ABC, abstractmethod

class PaxosNodeInterface(ABC):
    """
    Interface for a Paxos Node.
    Defines the required structure and methods for Paxos node implementations.
    """

    @abstractmethod
    def __init__(self, node_id, role, logger, node_count):
        """Initialize a Paxos node with ID, role, logger, and total node count."""
        pass

    @abstractmethod
    def set_consensus(self, value):
        """Set the consensus value for this node."""
        pass

    @abstractmethod
    def reset_consensus_reached(self):
        """Reset the consensus reached flag."""
        pass

    @abstractmethod
    def log_state_change(self):
        """Log the node's current state change."""
        pass

    @abstractmethod
    async def send_prepare(self, nodes, proposal):
        """Send a prepare request to other nodes."""
        pass

    @abstractmethod
    def receive_prepare(self, proposal):
        """Handle receiving a prepare request."""
        pass

    @abstractmethod
    async def send_promise(self, proposal):
        """Send a promise in response to a prepare request."""
        pass

    @abstractmethod
    def receive_promise(self, proposal):
        """Handle receiving a promise from another node."""
        pass

    @abstractmethod
    def decide_on_promises_received(self, proposal):
        """Decide on action after receiving promises."""
        pass

    @abstractmethod
    async def send_accept(self, nodes, proposal):
        """Send an accept request to other nodes."""
        pass

    @abstractmethod
    def receive_accept(self, proposal):
        """Handle receiving an accept request."""
        pass

    @abstractmethod
    async def send_learn(self, proposal):
        """Handle receiving an accept request."""
        pass

    @abstractmethod
    def receive_learn(self, proposal):
        """Handle receiving an accept request."""
        pass

    @abstractmethod
    def receive_broadcast(self, proposal):
        """Handle receiving a broadcast message indicating consensus."""
        pass
