from .order import Order


class RegularOrder(Order):
    def _compute_total(self) -> float:
        return float(sum(it.price for it in self.items))
