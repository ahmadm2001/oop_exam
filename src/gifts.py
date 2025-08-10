from abc import ABC, abstractmethod


class Gift(ABC):
    """Abstract Gift interface."""

    @abstractmethod
    def open_gift(self) -> None:
        """Must print the exact required message."""
        raise NotImplementedError


class CouponGift(Gift):
    """Concrete example gift."""

    def open_gift(self) -> None:
        # חייב להיות מדויק, כולל רישיות ונקודה:
        print("Congratulations! you got a new gift! Enjoy!")
