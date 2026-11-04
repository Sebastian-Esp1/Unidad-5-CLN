from unittest.mock import Mock

import pytest

from src.application import OrderService
from src.domain import Order


def test_gateway_approved():
    gateway = Mock()
    gateway.charge.return_value = True
    assert OrderService(gateway).checkout(Order(100)) == 100
    gateway.charge.assert_called_once_with(100)


def test_gateway_rejected():
    gateway = Mock()
    gateway.charge.return_value = False
    with pytest.raises(RuntimeError):
        OrderService(gateway).checkout(Order(100))


# --- E5: pago rechazado de un pedido VIP de 200 ----------------------------------------
def test_gateway_rejected_vip_200_charges_170():
    gateway = Mock()
    gateway.charge.return_value = False
    with pytest.raises(RuntimeError, match="payment rejected"):
        OrderService(gateway).checkout(Order(200, vip=True))
    gateway.charge.assert_called_once_with(170)


def test_gateway_timeout_is_propagated():
    gateway = Mock()
    gateway.charge.side_effect = TimeoutError("gateway timeout")
    with pytest.raises(TimeoutError):
        OrderService(gateway).checkout(Order(100))


def test_known_risk_order_stays_confirmed_when_payment_is_rejected():
    """Riesgo conocido (E5): checkout confirma el pedido ANTES de cobrar.

    Si el cobro se rechaza, el pedido queda CONFIRMED sin pago. Esta prueba documenta el
    comportamiento actual; la mejora propuesta es confirmar solo después de un cobro exitoso.
    """
    gateway = Mock()
    gateway.charge.return_value = False
    order = Order(100)
    with pytest.raises(RuntimeError):
        OrderService(gateway).checkout(order)
    assert order.status == "CONFIRMED"
