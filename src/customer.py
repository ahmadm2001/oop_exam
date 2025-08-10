from dataclasses import dataclass, field
from typing import Optional, List
from .enums import CustomerType
from .gifts import Gift
from .repositories import CustomersRepository


def _canon_name(s: str) -> str:
    # נורמליזציה למניעת כפילויות לוגיות
    return " ".join(s.strip().split()).lower()


@dataclass
class Customer:
    id: int
    first_name: str
    last_name: str
    email: str
    delivery_address: str
    type: CustomerType
    discount: Optional[float] = None  # עבור VIP בלבד; None => 0%
    favorite_items: List[str] = field(default_factory=list)  # שמות פריטים
    gift: Optional[Gift] = None

    def __post_init__(self) -> None:
        CustomersRepository.register(self.id)
        if not self.first_name.strip() or not self.last_name.strip():
            raise ValueError("Customer first_name/last_name must be non-empty.")
        if not self.email.strip():
            raise ValueError("Customer email must be non-empty.")
        if self.type == CustomerType.VIP and self.discount is not None:
            if not isinstance(self.discount, (int, float)):
                raise ValueError("Customer.discount must be a number or None.")
            if self.discount < 0 or self.discount > 1:
                raise ValueError("Customer.discount must be in [0, 1].")

        # איחוד ייצוג פנימי של שמות מועדפים:
        unique = []
        seen = set()
        for name in self.favorite_items:
            c = _canon_name(name)
            if c not in seen:
                seen.add(c)
                unique.append(name.strip())
        self.favorite_items = unique

    # ----- Favorites management -----
    def add_favorite(self, item_name: str) -> None:
        c = _canon_name(item_name)
        if c in {_canon_name(n) for n in self.favorite_items}:
            return
        self.favorite_items.append(item_name.strip())

    def remove_favorite(self, item_name: str) -> None:
        c = _canon_name(item_name)
        self.favorite_items = [
            n for n in self.favorite_items if _canon_name(n) != c
        ]

    # ----- Gifts -----
    def take_gift(self, gift: Gift) -> None:
        self.gift = gift

    def open_my_gift(self) -> None:
        if self.gift is None:
            print("No gift to open.")
            return
        self.gift.open_gift()
        
    def __repr__(self) -> str:
        return (f"Customer(id={self.id}, name='{self.first_name} {self.last_name}', "
                f"type={self.type.name}, favorites={self.favorite_items}, gift={self.gift})")
