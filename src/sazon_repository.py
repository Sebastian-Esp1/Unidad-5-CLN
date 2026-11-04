"""Persistencia de operaciones de Sazón Urbano con SQLAlchemy (SQLite en memoria en pruebas)."""

from sqlalchemy import Column, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Session

from src.sazon_urbano import Operacion


class Base(DeclarativeBase):
    pass


class OperacionRow(Base):
    __tablename__ = "operaciones"
    operacion_id = Column(String, primary_key=True)
    actor_id = Column(String, nullable=False)
    estado = Column(String, nullable=False)
    total = Column(String, nullable=False)  # Decimal guardado como texto, sin perder precisión


class SqlOperacionRepository:
    def __init__(self, session: Session):
        self.session = session

    def save(self, operacion: Operacion):
        self.session.add(
            OperacionRow(
                operacion_id=operacion.operacion_id,
                actor_id=operacion.actor.actor_id,
                estado=operacion.estado.value,
                total=str(operacion.total),
            )
        )

    def get(self, operacion_id):
        return self.session.get(OperacionRow, operacion_id)

    def update_estado(self, operacion: Operacion):
        self.session.get(OperacionRow, operacion.operacion_id).estado = operacion.estado.value


def make_engine(url="sqlite+pysqlite:///:memory:"):
    engine = create_engine(url)
    Base.metadata.create_all(engine)
    return engine
