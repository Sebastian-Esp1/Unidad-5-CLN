from datetime import UTC, datetime, timedelta

import pytest

from src.security import can_cancel

AHORA = datetime(2026, 11, 4, 12, 0, tzinfo=UTC)


def test_owner_within_24h():
    now = datetime.now(UTC)
    assert can_cancel("NEW", 1, 1, False, now - timedelta(hours=1), now)


def test_stranger_denied():
    now = datetime.now(UTC)
    assert not can_cancel("NEW", 1, 2, False, now, now)


def test_shipped_denied_even_admin():
    now = datetime.now(UTC)
    assert not can_cancel("SHIPPED", 1, 1, True, now, now)


def test_expired_denied():
    now = datetime.now(UTC)
    assert not can_cancel("NEW", 1, 1, False, now - timedelta(hours=25), now)


# --- E6: casos nuevos con fechas fijas -------------------------------------------------
def test_admin_can_cancel_new_order_of_another_user():
    assert can_cancel("NEW", 1, 99, True, AHORA - timedelta(days=3), AHORA)


def test_owner_exactly_24h_is_denied():
    assert not can_cancel("NEW", 1, 1, False, AHORA - timedelta(hours=24), AHORA)


def test_owner_just_before_24h_is_allowed():
    created = AHORA - timedelta(hours=23, minutes=59)
    assert can_cancel("NEW", 1, 1, False, created, AHORA)


@pytest.mark.parametrize(
    ("status", "owner", "user", "is_admin", "hours", "allowed"),
    [
        ("NEW", 1, 1, False, 1, True),  # dueño dentro de 24 h
        ("NEW", 1, 1, False, 24, False),  # dueño a las 24 h exactas
        ("NEW", 1, 2, False, 1, False),  # tercero sin permisos
        ("NEW", 1, 2, True, 100, True),  # administrador
        ("SHIPPED", 1, 1, False, 1, False),  # enviado, dueño
        ("SHIPPED", 1, 2, True, 1, False),  # enviado, administrador
    ],
)
def test_authorization_matrix(status, owner, user, is_admin, hours, allowed):
    created = AHORA - timedelta(hours=hours)
    assert can_cancel(status, owner, user, is_admin, created, AHORA) is allowed
