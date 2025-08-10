
class OrdersRepository:
    """Ensures unique Order IDs across the system."""
    _seen_ids: set[int] = set()

    @classmethod
    def register(cls, order_id: int) -> None:
        if order_id in cls._seen_ids:
            raise ValueError(f"Order ID {order_id} is already used.")
        cls._seen_ids.add(order_id)

    @classmethod
    def reset(cls) -> None:
        """Clear all stored IDs (for testing)."""
        cls._seen_ids.clear()


class CustomersRepository:
    """Ensures unique Customer IDs across the system."""
    _seen_ids: set[int] = set()

    @classmethod
    def register(cls, customer_id: int) -> None:
        if customer_id in cls._seen_ids:
            raise ValueError(f"Customer ID {customer_id} is already used.")
        cls._seen_ids.add(customer_id)

    @classmethod
    def reset(cls) -> None:
        """Clear all stored IDs (for testing)."""
        cls._seen_ids.clear()
