"""Servicio de aplicación de Sazón Urbano con un puerto de notificación a cocina.

El notificador es un puerto: en producción lo implementaría un adaptador real (mensajería);
en las pruebas se sustituye por un Mock, sin llamadas externas.
"""


class ServicioOperaciones:
    def __init__(self, notificador):
        self.notificador = notificador

    def aceptar(self, operacion):
        operacion.aceptar()  # si la regla falla, se lanza la excepción y NO se notifica
        self.notificador.avisar_cocina(operacion.operacion_id)
        return operacion.estado
