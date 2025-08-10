from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import List
from abc import ABC, abstractmethod

from .order_item import OrderItem
from .customer import Customer, _canon_name
from .enums import PaymentType
from .repositories import OrdersRepository


@dataclass
class Order(ABC):
    id: int
    name: str
    delivery_address: str
    items: List[OrderItem]
    customer: Customer
    payment_type: PaymentType
    order_date: datetime = field(default_factory=datetime.now)
    total_price: float = 0.0

    def __post_init__(self) -> None:
        OrdersRepository.register(self.id)

        if not self.name.strip():
            raise ValueError("Order.name must be non-empty.")
        if not self.delivery_address.strip():
            raise ValueError("Order.delivery_address must be non-empty.")
        if not isinstance(self.items, list):
            raise TypeError("Order.items must be a list of OrderItem.")
        
        ids = [it.id for it in self.items]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate OrderItem.id within the same order.")

        
        self.total_price = self._compute_total()

        # עדכון מועדפים של הלקוח לפי שמות הפריטים (ללא כפילויות, לפי name)
        seen_canon = {_canon_name(n) for n in self.customer.favorite_items}
        for it in self.items:
            c = _canon_name(it.name)
            if c not in seen_canon:
                self.customer.favorite_items.append(it.name.strip())
                seen_canon.add(c)

    @abstractmethod
    def _compute_total(self) -> float:
        """Compute order total (regular or VIP discount logic in subclasses)."""
        raise NotImplementedError
