import pytest

from src import repository, sazon_repository


@pytest.fixture
def engine():
    """Motor SQLite en memoria para el repositorio base; se cierra al terminar la prueba."""
    motor = repository.make_engine()
    yield motor
    motor.dispose()


@pytest.fixture
def sazon_engine():
    """Motor SQLite en memoria para las operaciones de Sazón Urbano."""
    motor = sazon_repository.make_engine()
    yield motor
    motor.dispose()
