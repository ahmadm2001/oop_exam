from .order import Order
from .enums import CustomerType


class VipOrder(Order):
    def _compute_total(self) -> float:
        # ולידציה: לקוח חייב להיות VIP
        if self.customer.type != CustomerType.VIP:
            raise ValueError("VIP order cannot be created for a non-VIP customer.")

        base = float(sum(it.price for it in self.items))
        discount = 0.0 if self.customer.discount is None else float(self.customer.discount)
        if discount < 0 or discount > 1:
            raise ValueError("Customer.discount must be in [0, 1].")
        return base * (1.0 - discount)
