"""Servicio de aplicación con un notificador simulado (sin llamadas externas)."""

from unittest.mock import Mock

import pytest

from src.sazon_application import ServicioOperaciones
from src.sazon_urbano import EstadoOperacion, OperacionInvalida, TransicionInvalida
from tests.csv_pia import cargar_operaciones


def test_aceptar_notifica_a_cocina_una_vez():
    notificador = Mock()
    operacion = cargar_operaciones()["PED-O001"]
    estado = ServicioOperaciones(notificador).aceptar(operacion)
    assert estado is EstadoOperacion.ACEPTADO
    notificador.avisar_cocina.assert_called_once_with("PED-O001")


def test_no_notifica_si_la_operacion_no_cumple_las_reglas():
    notificador = Mock()
    operacion = cargar_operaciones()["PED-O008"]  # no autorizada
    with pytest.raises(OperacionInvalida):
        ServicioOperaciones(notificador).aceptar(operacion)
    notificador.avisar_cocina.assert_not_called()


def test_no_notifica_si_ya_estaba_aceptada():
    notificador = Mock()
    servicio = ServicioOperaciones(notificador)
    operacion = cargar_operaciones()["PED-O003"]
    servicio.aceptar(operacion)
    with pytest.raises(TransicionInvalida):
        servicio.aceptar(operacion)
    notificador.avisar_cocina.assert_called_once_with("PED-O003")


def test_si_el_notificador_falla_el_error_se_propaga():
    notificador = Mock()
    notificador.avisar_cocina.side_effect = TimeoutError("cocina no responde")
    with pytest.raises(TimeoutError):
        ServicioOperaciones(notificador).aceptar(cargar_operaciones()["PED-O001"])
