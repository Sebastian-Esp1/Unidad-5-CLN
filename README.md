# Unidad 5 · Pruebas, integración y calidad (Equipo 3)

Proyecto Python de la Unidad 5 de *Componentes de lógica de negocios* (UANL FIME). Parte del proyecto base entregado por el docente (`Proyecto_Python_Base_U5.zip`) y lo amplía con pruebas unitarias, de integración y con mocks, cobertura mayor al 80 % y un pipeline de GitHub Actions.

El módulo `sazon_urbano` adapta tres reglas del paquete de datos del PIA (Sazón Urbano) como **ejercicio de la Unidad 5**. Es independiente del trabajo final del PIA.

## 1. Cambios respecto al proyecto base

| Archivo | Cambio | Motivo |
|---|---|---|
| `pyproject.toml` | Se agregó `pythonpath = ["."]` | Sin esa línea, el comando `pytest` (el que usa el pipeline) no encontraba la carpeta `src` y fallaba al recolectar las pruebas. |
| `src/*.py`, `tests/*.py` | Imports ordenados y `datetime.UTC` | Con la versión actual de Ruff, `ruff check src tests` marcaba 12 errores y el pipeline se detenía en ese paso. |
| `src/domain.py` | Guarda `already confirmed` en `Order.confirm()` | Fase GREEN de TDD (paso 3 del laboratorio). |
| `tests/conftest.py` | Fixtures `engine` y `sazon_engine` | Cierran las conexiones SQLite de cada prueba y evitan avisos de recursos sin cerrar. |
| `src/sazon_*.py`, `tests/test_sazon_*.py`, `tests/csv_pia.py` | Archivos nuevos | Adaptación a Sazón Urbano (paso 9). |
| `tests/datos_pia/` | CSV del PIA, sin modificar | Datos de referencia; se leen con `csv.DictReader`. |

## 2. Estructura

| Archivo o carpeta | Contenido |
|---|---|
| `src/domain.py` | `Order`: descuento VIP del 15 %, total positivo, deuda del cliente y confirmación única |
| `src/application.py` | `OrderService.checkout()`: confirma y cobra con una pasarela (puerto) |
| `src/repository.py` | `SqlOrderRepository` con SQLAlchemy |
| `src/security.py` | `can_cancel()`: política de cancelación |
| `src/sazon_urbano.py` | Sazón Urbano: `Operacion`, reglas R1, R2 y R3 |
| `src/sazon_application.py` | `ServicioOperaciones` con un notificador a cocina (puerto) |
| `src/sazon_repository.py` | Persistencia de operaciones con SQLAlchemy |
| `tests/` | Pruebas del dominio, repositorio, servicio, seguridad y Sazón Urbano |
| `docs/matriz_casos_prueba.csv` | Matriz de 16 casos (7 éxito, 5 error, 4 límite) |
| `docs/matriz_pia_sazon_urbano.csv` | Matriz de 15 casos de Sazón Urbano |
| `.github/workflows/ci.yml` | Pipeline: Ruff, pytest con cobertura mínima de 80 % y compilación |

## 3. Cómo ejecutarlo (Windows PowerShell, desde la raíz del proyecto)

| Paso | Comando |
|---|---|
| Crear el entorno virtual | `py -m venv .venv` |
| Activarlo | `.\.venv\Scripts\Activate.ps1` |
| Instalar dependencias | `python -m pip install -r requirements.txt` |
| Correr las pruebas | `python -m pytest -v` |
| Revisar el estilo | `python -m ruff check src tests` |
| Cobertura con reporte HTML | `python -m pytest -v --cov=src --cov-report=term-missing --cov-report=html --cov-fail-under=80` |

Si PowerShell no activa el entorno, usa `.venv\Scripts\python.exe -m pytest -v`. El reporte HTML queda en `htmlcov/index.html`.

## 4. Reglas que se prueban

### Proyecto base

| Regla | Prueba |
|---|---|
| VIP recibe 15 % de descuento | `test_vip_discount`, `test_vip_discount_total_200` |
| Total cero o negativo se rechaza | `test_invalid_total` |
| Cliente con deuda no confirma | `test_customer_debt` |
| Un pedido no se confirma dos veces | `test_cannot_confirm_twice` |
| Cobro aprobado, rechazado y con tiempo agotado | `test_gateway_*` |
| Commit y rollback | `test_repository_*` |
| Cancelación: dueño 24 h, administrador, enviado nunca | `test_security.py` |

### Sazón Urbano (tomadas del `LEEME.txt` del paquete del PIA)

| Regla | Condición |
|---|---|
| R1 `puede_procesarse` | Actor activo AND al menos una línea AND operación autorizada |
| R2 `califica_beneficio` | Actor preferente AND total >= 1500 MXN AND NOT promoción activa |
| R3 transiciones | CREADO → ACEPTADO → EN_PREPARACION → ENTREGADO; CREADO → CANCELADO; no se repite ni se salta un estado |

Los CSV del alumno no incluyen resultados esperados. Por eso los resultados esperados de `tests/test_sazon_urbano.py` se derivan de las reglas, no de un archivo de respuestas.

## 5. TDD: cómo reproducir la fase RED

1. En `src/domain.py`, comenta las dos líneas de la guarda `if self.status == "CONFIRMED": ...`.
2. Ejecuta `python -m pytest tests/test_order.py -v`. Debe fallar `test_cannot_confirm_twice` con `DID NOT RAISE`. Captura la pantalla.
3. Descomenta las dos líneas y vuelve a ejecutar. Debe pasar (GREEN). Captura la pantalla.

## 6. Riesgo conocido

`OrderService.checkout()` confirma el pedido **antes** de cobrar. Si la pasarela rechaza el pago, el pedido queda `CONFIRMED` sin cobro. `test_known_risk_order_stays_confirmed_when_payment_is_rejected` documenta ese comportamiento. Mejora propuesta: cobrar primero y confirmar solo si el cobro fue exitoso.

## 7. Resultados verificados

| Verificación | Resultado |
|---|---|
| `pytest` | 205 pruebas pasaron |
| Cobertura de `src/` | 100 % (152 instrucciones) |
| `ruff check src tests` | Sin errores |
| Pruebas que detectan defectos | 12 de 12 defectos introducidos a propósito fueron detectados |

Se ejecutó con Python 3.13, pytest 9.2 y SQLAlchemy 2.1 en Linux. En Windows (Python 3.14) falta correrlo y capturarlo.

## 8. Evidencias (E1–E9)

Las evidencias se documentan en `docs/Documentacion_U5_Equipo3.docx`: E1 entorno, E2 pruebas unitarias, E3 TDD, E4 base de datos, E5 mock de pasarela, E6 seguridad, E7 cobertura, E8 GitHub Actions y E9 adaptación a Sazón Urbano.
