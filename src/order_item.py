from dataclasses import dataclass


@dataclass(slots=True)
class OrderItem:
    id: int
    name: str
    price: float

    def __post_init__(self) -> None:
        if not isinstance(self.id, int) or self.id < 0:
            raise ValueError("OrderItem.id must be a non-negative int.")
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("OrderItem.name must be a non-empty string.")
        if not isinstance(self.price, (int, float)) or self.price < 0:
            raise ValueError("OrderItem.price must be a non-negative number.")
        self.name = self.name.strip()
    def __repr__(self) -> str:
        return f"OrderItem(id={self.id}, name='{self.name}', price={self.price})"
