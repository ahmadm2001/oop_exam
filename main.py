# main.py  — test runner with explicit Pass/Fail (no asserts)
# All prints/comments are in English.

from datetime import datetime, timedelta
from io import StringIO
from contextlib import redirect_stdout
import sys

from src.enums import PaymentType, CustomerType
from src.order_item import OrderItem
from src.customer import Customer
from src.regular_order import RegularOrder
from src.vip_order import VipOrder
from src.gifts import CouponGift
from src.repositories import OrdersRepository, CustomersRepository


def reset_repositories():
    from src.repositories import OrdersRepository, CustomersRepository
    OrdersRepository.reset()
    CustomersRepository.reset()


def must_raise(exc_type, fn, *args, **kwargs) -> bool:
    try:
        fn(*args, **kwargs)
    except exc_type:
        return True
    except Exception:
        return False
    return False


def check(name: str, condition: bool, details: str = "") -> bool:
    if condition:
        print(f"[PASS] {name}")
        return True
    else:
        print(f"[FAIL] {name}" + (f" — {details}" if details else ""))
        return False


def test_regular_and_vip_orders_and_totals() -> bool:
    reset_repositories()
    ok = True
    try:
        vip = Customer(1, "Avi", "Cohen", "avi@example.com", "Herzl 10, TLV", CustomerType.VIP, discount=0.25)
        reg = Customer(2, "Dana", "Levi", "dana@example.com", "Dizengoff 50, TLV", CustomerType.REGULAR)
        i1 = OrderItem(10, "Black T-Shirt", 100.0)
        i2 = OrderItem(11, "White Sneakers", 300.0)
        o1 = RegularOrder(100, "Dana order", reg.delivery_address, [i1, i2], reg, PaymentType.CREDIT_CARD)
        o2 = VipOrder(101, "Avi order", vip.delivery_address, [i1, i2], vip, PaymentType.CASH)

        ok &= check("Regular total is 400.0", abs(o1.total_price - 400.0) < 1e-9,
                    f"got {o1.total_price}")
        ok &= check("VIP total is 300.0 (25% off 400)", abs(o2.total_price - 300.0) < 1e-9,
                    f"got {o2.total_price}")
        ok &= check("Duplicate Order ID raises", must_raise(ValueError, RegularOrder,
                    100, "Dup ID", reg.delivery_address, [i1], reg, PaymentType.CHECK))
    except Exception as e:
        ok &= check("Regular/VIP totals & unique Order ID (no unexpected exceptions)", False, str(e))
    return ok


def test_vip_requires_vip_customer() -> bool:
    reset_repositories()
    ok = True
    try:
        reg = Customer(1, "Dana", "Levi", "dana@example.com", "Dizengoff 50, TLV", CustomerType.REGULAR)
        i1 = OrderItem(10, "Item A", 50.0)
        ok &= check("VIP order for REGULAR customer raises",
                    must_raise(ValueError, VipOrder, 100, "Invalid VIP", reg.delivery_address, [i1], reg, PaymentType.OTHER))
    except Exception as e:
        ok &= check("VIP requires VIP customer (no unexpected exceptions)", False, str(e))
    return ok


def test_duplicate_item_id_in_order() -> bool:
    reset_repositories()
    ok = True
    try:
        vip = Customer(1, "Avi", "Cohen", "avi@example.com", "Herzl 10, TLV", CustomerType.VIP, discount=0.2)
        i1 = OrderItem(10, "Shirt", 100.0)
        i2 = OrderItem(10, "Pants", 150.0)  # duplicate id inside the same order
        ok &= check("Duplicate OrderItem.id within order raises",
                    must_raise(ValueError, RegularOrder, 100, "Dup items", vip.delivery_address, [i1, i2], vip, PaymentType.CREDIT_CARD))
    except Exception as e:
        ok &= check("Duplicate item id (no unexpected exceptions)", False, str(e))
    return ok


def test_favorites_by_name() -> bool:
    reset_repositories()
    ok = True
    try:
        reg = Customer(1, "Dana", "Levi", "dana@example.com", "Dizengoff 50, TLV", CustomerType.REGULAR)
        a = OrderItem(10, "  Black   T-Shirt  ", 100.0)
        b = OrderItem(11, "black t-shirt", 100.0)
        c = OrderItem(12, "White Sneakers", 300.0)

        _ = RegularOrder(100, "Order 1", reg.delivery_address, [a, c], reg, PaymentType.CREDIT_CARD)
        _ = RegularOrder(101, "Order 2", reg.delivery_address, [b], reg, PaymentType.CASH)

        ok &= check("Favorites have exactly two unique names", len(reg.favorite_items) == 2,
                    f"{reg.favorite_items}")
        ok &= check("First favorite keeps original inner spacing",
                    reg.favorite_items[0].strip() == "Black   T-Shirt", f"{reg.favorite_items}")
        ok &= check("Second favorite is 'White Sneakers'",
                    reg.favorite_items[1] == "White Sneakers", f"{reg.favorite_items}")

        reg.add_favorite("WHITE SNEAKERS")  # should not duplicate
        ok &= check("Manual add does not duplicate by name", len(reg.favorite_items) == 2,
                    f"{reg.favorite_items}")
        reg.remove_favorite("black T-shirt")
        ok &= check("Manual remove by name works", reg.favorite_items == ["White Sneakers"],
                    f"{reg.favorite_items}")
    except Exception as e:
        ok &= check("Favorites by name (no unexpected exceptions)", False, str(e))
    return ok


def test_gift_message_exact() -> bool:
    reset_repositories()
    ok = True
    try:
        cust = Customer(1, "Avi", "Cohen", "avi@example.com", "Herzl 10, TLV", CustomerType.VIP, discount=0.0)
        cust.take_gift(CouponGift())
        buf = StringIO()
        with redirect_stdout(buf):
            cust.open_my_gift()
        out = buf.getvalue().strip()
        ok &= check("Gift exact message",
                    out == "Congratulations! you got a new gift! Enjoy!",
                    f"got: {out!r}")
    except Exception as e:
        ok &= check("Gift message (no unexpected exceptions)", False, str(e))
    return ok


def test_payment_enum_and_order_date() -> bool:
    reset_repositories()
    ok = True
    try:
        cust = Customer(1, "Avi", "Cohen", "avi@example.com", "Herzl 10, TLV", CustomerType.VIP, discount=0.1)
        i = OrderItem(10, "Item", 50.0)
        before = datetime.now() - timedelta(seconds=2)
        o = RegularOrder(100, "Has date", cust.delivery_address, [i], cust, PaymentType.CHECK)
        after = datetime.now() + timedelta(seconds=2)
        ok &= check("payment_type is an Enum", isinstance(o.payment_type, PaymentType))
        ok &= check("order_date defaults to now()", before <= o.order_date <= after, f"{o.order_date}")
    except Exception as e:
        ok &= check("Payment enum & date (no unexpected exceptions)", False, str(e))
    return ok


def test_discount_range_and_none() -> bool:
    reset_repositories()
    ok = True
    try:
        vip_none = Customer(1, "Avi", "Cohen", "avi@example.com", "Herzl 10, TLV", CustomerType.VIP, discount=None)
        i = OrderItem(10, "Item", 100.0)
        o = VipOrder(100, "None discount", vip_none.delivery_address, [i], vip_none, PaymentType.CASH)
        ok &= check("None discount => 0%", abs(o.total_price - 100.0) < 1e-9, f"got {o.total_price}")

        ok &= check("Discount > 1 blocked at Customer",
                    must_raise(ValueError, Customer, 2, "Bad", "VIP", "b@example.com", "Addr", CustomerType.VIP, discount=1.5))
        ok &= check("Negative discount blocked at Customer",
                    must_raise(ValueError, Customer, 3, "Bad", "VIP2", "c@example.com", "Addr", CustomerType.VIP, discount=-0.1))
    except Exception as e:
        ok &= check("Discount range & None (no unexpected exceptions)", False, str(e))
    return ok

def test_repositories_reset_allows_reuse() -> bool:
    # ריצה 1: יוצר הזמנה עם id=100
    OrdersRepository.reset(); CustomersRepository.reset()
    from src.enums import PaymentType, CustomerType
    from src.customer import Customer
    from src.order_item import OrderItem
    from src.regular_order import RegularOrder
    ok = True
    try:
        c = Customer(1, "Avi", "Cohen", "a@e.com", "Addr", CustomerType.REGULAR)
        i = OrderItem(10, "Item", 10.0)
        _ = RegularOrder(100, "o1", c.delivery_address, [i], c, PaymentType.CASH)
        # ריצה 2: reset ואז מותר להשתמש שוב ב־id=100
        OrdersRepository.reset(); CustomersRepository.reset()
        c2 = Customer(1, "Dana", "Levi", "b@e.com", "Addr", CustomerType.REGULAR)
        _ = RegularOrder(100, "o2", c2.delivery_address, [i], c2, PaymentType.CASH)
        print("[PASS] Repositories.reset() allows reusing IDs after reset")
    except Exception as e:
        print(f"[FAIL] Repositories.reset() failed — {e}")
        ok = False
    return ok
def test_repr_exist_and_readable() -> bool:
    reset_repositories()  # <<< חשוב!
    from src.enums import CustomerType
    from src.customer import Customer
    from src.order_item import OrderItem
    ok = True
    try:
        c = Customer(99, "Avi", "Cohen", "a@e.com", "Addr", CustomerType.REGULAR)  # ID חדש
        r1 = repr(c)
        i = OrderItem(77, "Hat", 25.5)  # ID חדש
        r2 = repr(i)
        cond = ("Customer(" in r1 and "OrderItem(" in r2)
        if cond:
            print("[PASS] __repr__ exists and is readable on Customer/OrderItem")
        else:
            print(f"[FAIL] __repr__ missing/unclear — {r1!r} / {r2!r}")
        return cond
    except Exception as e:
        print(f"[FAIL] __repr__ threw exception — {e}")
        return False



def run_all():
    results = [
        ("Regular/VIP totals & unique Order ID", test_regular_and_vip_orders_and_totals()),
        ("VIP requires VIP customer", test_vip_requires_vip_customer()),
        ("Duplicate item id within order", test_duplicate_item_id_in_order()),
        ("Favorites by name (auto + manual)", test_favorites_by_name()),
        ("Gift exact message", test_gift_message_exact()),
        ("Payment enum & order_date", test_payment_enum_and_order_date()),
        ("Discount validation & None", test_discount_range_and_none()),
        ("Repositories reset allows reuse", test_repositories_reset_allows_reuse()),
        ("__repr__ exists and readable", test_repr_exist_and_readable()),
    ]
    passed = sum(1 for _, ok in results if ok)
    total = len(results)
    print("\n====================")
    print(f"SUMMARY: {passed}/{total} test groups passed")
    print("====================")
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(run_all())
