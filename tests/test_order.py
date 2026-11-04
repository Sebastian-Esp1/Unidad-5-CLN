import pytest

from src.domain import CustomerHasDebt, Order


# --- Pruebas del proyecto base ---------------------------------------------------------
def test_vip_discount():
    o = Order(100, vip=True)
    assert o.confirm() == 85
    assert o.status == "CONFIRMED"


def test_regular_no_discount():
    assert Order(100).confirm() == 100


def test_customer_debt():
    with pytest.raises(CustomerHasDebt):
        Order(100).confirm(customer_debt=50)


@pytest.mark.parametrize("total", [0, -1])
def test_invalid_total(total):
    with pytest.raises(ValueError):
        Order(total).confirm()


# --- E2: pruebas nuevas (descuento VIP) ------------------------------------------------
def test_vip_discount_total_200():
    order = Order(200, vip=True)
    assert order.confirm() == 170
    assert order.discount == 30


def test_regular_customer_total_200_has_no_discount():
    order = Order(200)
    assert order.confirm() == 200
    assert order.discount == 0


# --- Casos límite y de error adicionales -----------------------------------------------
def test_smallest_positive_total_is_valid():
    assert Order(0.01).confirm() == 0.01


def test_debt_equal_to_zero_is_allowed():
    assert Order(100).confirm(customer_debt=0) == 100


def test_failed_confirmation_keeps_status_new():
    order = Order(100)
    with pytest.raises(CustomerHasDebt):
        order.confirm(customer_debt=500)
    assert order.status == "NEW"


# --- E3: TDD (RED -> GREEN -> REFACTOR) ------------------------------------------------
def test_cannot_confirm_twice():
    order = Order(100)
    order.confirm()
    with pytest.raises(ValueError, match="already confirmed"):
        order.confirm()
