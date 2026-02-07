# ==========================================
# MLang - Domain Base Contract
# File: domains/base.py
# ==========================================

from abc import ABC, abstractmethod


class DomainResponse:
    """
    Standard response object returned by domains.
    """

    def __init__(self, handled, message=None, needs_clarification=False):
        self.handled = handled
        self.message = message
        self.needs_clarification = needs_clarification


class Domain(ABC):
    """
    Abstract base class for all domains.
    """

    name = "BASE_DOMAIN"

    @abstractmethod
    def can_handle(self, context):
        """
        Decide if this domain can handle the request.
        """
        pass

    @abstractmethod
    def handle(self, context):
        """
        Perform domain-specific handling.
        """
        pass
