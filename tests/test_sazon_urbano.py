"""E9 · Adaptación a Sazón Urbano (PIA).

Las reglas salen del LEEME del paquete del PIA. Los CSV del alumno no traen resultados
esperados, así que los oráculos se derivan de las reglas, no de un archivo de respuestas.
"""

from decimal import Decimal

import pytest

from src.sazon_urbano import (
    Actor,
    EstadoOperacion,
    LineaOperacion,
    Operacion,
    OperacionInvalida,
    TransicionInvalida,
)
from tests.csv_pia import cargar_operaciones, leer

OPERACIONES = cargar_operaciones()


def op(operacion_id):
    """Operación fresca (estado CREADO) del CSV; se recarga para no arrastrar estado."""
    return cargar_operaciones()[operacion_id]


def operacion_sintetica(precio, cantidad=1, preferente=True, promocion=False):
    return Operacion(
        "SINT-1",
        Actor("A1", es_preferente=preferente),
        [LineaOperacion("P1", cantidad, Decimal(precio))],
        promocion_activa=promocion,
        autorizado=True,
    )


# --- Total con Decimal -----------------------------------------------------------------
def test_total_se_calcula_con_decimal():
    operacion = op("PED-O001")  # 3 x 858.00 + 4 x 1213.00
    assert operacion.total == Decimal("7426.00")
    assert isinstance(operacion.total, Decimal)


def test_operacion_sin_lineas_tiene_total_cero():
    assert op("PED-O013").total == Decimal(0)


@pytest.mark.parametrize("cantidad", [0, -1])
def test_cantidad_invalida_se_rechaza(cantidad):
    with pytest.raises(OperacionInvalida):
        LineaOperacion("P1", cantidad, Decimal(100))


def test_cantidad_decimal_o_booleana_se_rechaza():
    with pytest.raises(OperacionInvalida):
        LineaOperacion("P1", 1.5, Decimal(100))
    with pytest.raises(OperacionInvalida):
        LineaOperacion("P1", True, Decimal(100))


def test_precio_debe_ser_decimal_no_negativo():
    with pytest.raises(OperacionInvalida):
        LineaOperacion("P1", 1, 100.0)
    with pytest.raises(OperacionInvalida):
        LineaOperacion("P1", 1, Decimal(-1))


# --- R1 puede_procesarse: actor activo AND >=1 línea AND autorizada --------------------
def test_r1_exito_actor_activo_con_lineas_y_autorizada():
    assert op("PED-O001").puede_procesarse() is True


def test_r1_limite_una_sola_linea_es_suficiente():
    operacion = op("PED-O003")
    assert len(operacion.lineas) == 1
    assert operacion.puede_procesarse() is True


def test_r1_error_detalle_vacio():
    operacion = op("PED-O013")
    assert operacion.lineas == []
    assert operacion.puede_procesarse() is False


def test_r1_error_no_autorizada():
    assert op("PED-O008").puede_procesarse() is False


def test_r1_error_actor_inactivo():
    operacion = op("PED-O029")  # actor inactivo, con líneas y autorizada
    assert operacion.puede_procesarse() is False


# --- R2 beneficio: preferente AND total >= 1500 AND NOT promoción ----------------------
def test_r2_exito_preferente_sobre_umbral_sin_promocion():
    assert op("PED-O023").califica_beneficio() is True


def test_r2_error_con_promocion_activa():
    operacion = op("PED-O018")  # preferente, total 6556, con promoción
    assert operacion.promocion_activa is True
    assert operacion.califica_beneficio() is False


def test_r2_error_cliente_no_preferente():
    assert operacion_sintetica("2000", preferente=False).califica_beneficio() is False


def test_r2_limite_exactamente_1500_si_califica():
    assert operacion_sintetica("1500.00").califica_beneficio() is True


def test_r2_limite_1499_99_no_califica():
    assert operacion_sintetica("1499.99").califica_beneficio() is False


def test_r2_preferente_bajo_umbral_del_csv():
    operacion = op("PED-O003")  # preferente, total 1284
    assert operacion.total == Decimal("1284.00")
    assert operacion.califica_beneficio() is False


# --- R3 máquina de estados -------------------------------------------------------------
def test_r3_exito_aceptar_registra_evento():
    operacion = op("PED-O001")
    operacion.aceptar()
    assert operacion.estado is EstadoOperacion.ACEPTADO
    assert operacion.eventos == ["OperacionAceptada"]


def test_r3_exito_flujo_completo():
    operacion = op("PED-O001")
    operacion.aceptar()
    operacion.preparar()
    operacion.entregar()
    assert operacion.estado is EstadoOperacion.ENTREGADO
    assert operacion.eventos == ["OperacionAceptada", "PreparacionIniciada", "OperacionEntregada"]


def test_r3_limite_cancelar_desde_creado():
    operacion = op("PED-O002")
    operacion.cancelar()
    assert operacion.estado is EstadoOperacion.CANCELADO
    assert operacion.eventos == ["OperacionCancelada"]


def test_r3_error_repetir_aprobacion():
    operacion = op("PED-O003")
    operacion.aceptar()
    with pytest.raises(TransicionInvalida):
        operacion.aceptar()
    assert operacion.eventos == ["OperacionAceptada"]


def test_r3_error_saltar_estado():
    operacion = op("PED-O004")
    with pytest.raises(TransicionInvalida):
        operacion.entregar()
    assert operacion.estado is EstadoOperacion.CREADO
    assert operacion.eventos == []


def test_r3_error_cancelar_despues_de_aceptar():
    operacion = op("PED-O005")
    operacion.aceptar()
    with pytest.raises(TransicionInvalida):
        operacion.cancelar()
    assert operacion.estado is EstadoOperacion.ACEPTADO


def test_r3_error_preparar_sin_aceptar():
    with pytest.raises(TransicionInvalida):
        op("PED-O006").preparar()


def test_r3_error_aceptar_sin_cumplir_r1_no_cambia_estado():
    operacion = op("PED-O008")  # no autorizada
    with pytest.raises(OperacionInvalida):
        operacion.aceptar()
    assert operacion.estado is EstadoOperacion.CREADO
    assert operacion.eventos == []


# --- Pruebas dirigidas por los CSV del PIA ---------------------------------------------
def esperado_procesable(operacion_id):
    """Oráculo independiente: se calcula con las columnas crudas de los CSV."""
    fila = next(r for r in leer("operaciones.csv") if r["operacion_id"] == operacion_id)
    actor = next(r for r in leer("actores.csv") if r["actor_id"] == fila["actor_id"])
    lineas = [r for r in leer("detalle_operaciones.csv") if r["operacion_id"] == operacion_id]
    return actor["activo"] == "1" and len(lineas) >= 1 and fila["autorizado"] == "1"


def esperado_beneficio(operacion_id):
    fila = next(r for r in leer("operaciones.csv") if r["operacion_id"] == operacion_id)
    actor = next(r for r in leer("actores.csv") if r["actor_id"] == fila["actor_id"])
    precios = {r["recurso_id"]: Decimal(r["precio_mxn"]) for r in leer("catalogo.csv")}
    total = sum(
        (
            precios[r["recurso_id"]] * int(r["cantidad"])
            for r in leer("detalle_operaciones.csv")
            if r["operacion_id"] == operacion_id
        ),
        Decimal(0),
    )
    return actor["es_preferente"] == "1" and total >= 1500 and fila["promocion_activa"] == "0"


CASOS = leer("casos_prueba.csv")
TRANSICIONES = leer("transiciones_prueba.csv")


@pytest.mark.parametrize("caso", CASOS, ids=[c["caso_id"] for c in CASOS])
def test_casos_prueba_csv(caso):
    operacion = op(caso["operacion_id"])
    if caso["tipo_prueba"] == "validar_operacion":
        assert operacion.puede_procesarse() is esperado_procesable(caso["operacion_id"])
    else:
        assert caso["tipo_prueba"] == "evaluar_beneficio"
        assert operacion.califica_beneficio() is esperado_beneficio(caso["operacion_id"])


def ejecutar(operacion, accion):
    """Interpreta cada acción sugerida del CSV de transiciones."""
    if accion == "aprobar":
        operacion.aceptar()
    elif accion == "cancelar":
        operacion.cancelar()
    elif accion == "repetir_aprobacion":
        operacion.aceptar()
        operacion.aceptar()
    elif accion == "saltar_estado":
        operacion.entregar()
    elif accion == "completar":
        operacion.aceptar()
        operacion.preparar()
        operacion.entregar()
    else:  # pragma: no cover - el CSV solo trae las acciones anteriores
        raise AssertionError(accion)


@pytest.mark.parametrize("fila", TRANSICIONES, ids=[t["caso_id"] for t in TRANSICIONES])
def test_transiciones_csv(fila):
    operacion = op(fila["operacion_id"])
    accion = fila["accion_sugerida"]
    procesable = esperado_procesable(fila["operacion_id"])
    if accion in ("cancelar",):
        ejecutar(operacion, accion)
        assert operacion.estado is EstadoOperacion.CANCELADO
    elif accion == "saltar_estado":
        with pytest.raises(TransicionInvalida):
            ejecutar(operacion, accion)
        assert operacion.estado is EstadoOperacion.CREADO
    elif not procesable:
        with pytest.raises(OperacionInvalida):
            ejecutar(operacion, accion)
        assert operacion.estado is EstadoOperacion.CREADO
    elif accion == "repetir_aprobacion":
        with pytest.raises(TransicionInvalida):
            ejecutar(operacion, accion)
        assert operacion.estado is EstadoOperacion.ACEPTADO
    elif accion == "aprobar":
        ejecutar(operacion, accion)
        assert operacion.estado is EstadoOperacion.ACEPTADO
    else:
        ejecutar(operacion, accion)
        assert operacion.estado is EstadoOperacion.ENTREGADO
        assert len(operacion.eventos) == 3
