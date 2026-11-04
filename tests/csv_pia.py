"""Carga los CSV del paquete del PIA (solo lectura) para usarlos como datos de prueba."""

import csv
from collections import defaultdict
from decimal import Decimal
from pathlib import Path

from src.sazon_urbano import Actor, LineaOperacion, Operacion

DATOS = Path(__file__).parent / "datos_pia"


def leer(nombre):
    with open(DATOS / nombre, encoding="utf-8-sig", newline="") as archivo:
        return list(csv.DictReader(archivo))


def cargar_operaciones():
    """Devuelve {operacion_id: Operacion} armada con actores, catálogo y detalle."""
    actores = {
        r["actor_id"]: Actor(r["actor_id"], r["es_preferente"] == "1", r["activo"] == "1")
        for r in leer("actores.csv")
    }
    precios = {r["recurso_id"]: Decimal(r["precio_mxn"]) for r in leer("catalogo.csv")}
    lineas = defaultdict(list)
    for r in leer("detalle_operaciones.csv"):
        lineas[r["operacion_id"]].append(
            LineaOperacion(r["recurso_id"], int(r["cantidad"]), precios[r["recurso_id"]])
        )
    return {
        r["operacion_id"]: Operacion(
            r["operacion_id"],
            actores[r["actor_id"]],
            lineas[r["operacion_id"]],
            promocion_activa=r["promocion_activa"] == "1",
            autorizado=r["autorizado"] == "1",
        )
        for r in leer("operaciones.csv")
    }
