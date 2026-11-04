"""Persistencia (SQLite en memoria): commit, rollback y restricción de unicidad."""

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.sazon_repository import SqlOperacionRepository
from tests.csv_pia import cargar_operaciones


def test_guarda_operacion_con_commit(sazon_engine):
    with Session(sazon_engine) as session:
        SqlOperacionRepository(session).save(cargar_operaciones()["PED-O001"])
        session.commit()
        fila = SqlOperacionRepository(session).get("PED-O001")
        assert fila.actor_id == "PED-C011"
        assert fila.estado == "CREADO"
        assert fila.total == "7426.00"


def test_rollback_descarta_la_operacion(sazon_engine):
    with Session(sazon_engine) as session:
        SqlOperacionRepository(session).save(cargar_operaciones()["PED-O001"])
        session.rollback()
        assert SqlOperacionRepository(session).get("PED-O001") is None


def test_actualiza_estado_persistido(sazon_engine):
    operacion = cargar_operaciones()["PED-O001"]
    with Session(sazon_engine) as session:
        repo = SqlOperacionRepository(session)
        repo.save(operacion)
        session.commit()
        operacion.aceptar()
        repo.update_estado(operacion)
        session.commit()
        assert repo.get("PED-O001").estado == "ACEPTADO"


def test_id_duplicado_viola_la_restriccion_de_unicidad(sazon_engine):
    with Session(sazon_engine) as session:
        SqlOperacionRepository(session).save(cargar_operaciones()["PED-O001"])
        session.commit()
    with Session(sazon_engine) as session:
        SqlOperacionRepository(session).save(cargar_operaciones()["PED-O001"])
        with pytest.raises(IntegrityError):
            session.commit()
        session.rollback()
