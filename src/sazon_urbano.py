"""Adaptación a Sazón Urbano (PIA): operaciones de restaurante.

Las tres reglas que se prueban en la Unidad 5 se toman como referencia del paquete del PIA
(LEEME.txt) y NO reemplazan los requerimientos del BRD del equipo:

R1  puede_procesarse     actor activo AND al menos una línea AND autorizada
R2  califica_beneficio   actor preferente AND total >= 1500 MXN AND NOT promoción activa
R3  transiciones         CREADO -> ACEPTADO -> EN_PREPARACION -> ENTREGADO
                         y CREADO -> CANCELADO (no se repite ni se salta un estado)
"""

from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum

UMBRAL_BENEFICIO = Decimal(1500)


class EstadoOperacion(str, Enum):
    CREADO = "CREADO"
    ACEPTADO = "ACEPTADO"
    EN_PREPARACION = "EN_PREPARACION"
    ENTREGADO = "ENTREGADO"
    CANCELADO = "CANCELADO"


class OperacionInvalida(Exception):
    """La operación no cumple las precondiciones de negocio."""


class TransicionInvalida(Exception):
    """El cambio de estado solicitado no está permitido desde el estado actual."""


@dataclass(frozen=True)
class Actor:
    actor_id: str
    es_preferente: bool = False
    activo: bool = True


@dataclass(frozen=True)
class LineaOperacion:
    recurso_id: str
    cantidad: int
    precio: Decimal

    def __post_init__(self):
        if isinstance(self.cantidad, bool) or not isinstance(self.cantidad, int):
            raise OperacionInvalida("la cantidad debe ser un entero")
        if self.cantidad <= 0:
            raise OperacionInvalida("la cantidad debe ser mayor que cero")
        if not isinstance(self.precio, Decimal) or self.precio < 0:
            raise OperacionInvalida("el precio debe ser un Decimal no negativo")

    @property
    def subtotal(self):
        return self.precio * self.cantidad


@dataclass
class Operacion:
    operacion_id: str
    actor: Actor
    lineas: list = field(default_factory=list)
    promocion_activa: bool = False
    autorizado: bool = False
    estado: EstadoOperacion = EstadoOperacion.CREADO
    eventos: list = field(default_factory=list)

    @property
    def total(self):
        return sum((linea.subtotal for linea in self.lineas), Decimal(0))

    # R1 ---------------------------------------------------------------------------------
    def puede_procesarse(self):
        return self.actor.activo and len(self.lineas) >= 1 and self.autorizado

    # R2 ---------------------------------------------------------------------------------
    def califica_beneficio(self):
        return (
            self.actor.es_preferente
            and self.total >= UMBRAL_BENEFICIO
            and not self.promocion_activa
        )

    # R3 ---------------------------------------------------------------------------------
    def _exigir_estado(self, esperado, destino):
        if self.estado is not esperado:
            raise TransicionInvalida(
                f"no se puede pasar a {destino.value} desde {self.estado.value}"
            )

    def _cambiar(self, destino, evento):
        self.estado = destino
        self.eventos.append(evento)

    def aceptar(self):
        self._exigir_estado(EstadoOperacion.CREADO, EstadoOperacion.ACEPTADO)
        if not self.puede_procesarse():
            raise OperacionInvalida("la operación no cumple las precondiciones")
        self._cambiar(EstadoOperacion.ACEPTADO, "OperacionAceptada")

    def preparar(self):
        self._exigir_estado(EstadoOperacion.ACEPTADO, EstadoOperacion.EN_PREPARACION)
        self._cambiar(EstadoOperacion.EN_PREPARACION, "PreparacionIniciada")

    def entregar(self):
        self._exigir_estado(EstadoOperacion.EN_PREPARACION, EstadoOperacion.ENTREGADO)
        self._cambiar(EstadoOperacion.ENTREGADO, "OperacionEntregada")

    def cancelar(self):
        self._exigir_estado(EstadoOperacion.CREADO, EstadoOperacion.CANCELADO)
        self._cambiar(EstadoOperacion.CANCELADO, "OperacionCancelada")
