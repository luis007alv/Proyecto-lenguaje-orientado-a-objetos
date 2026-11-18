"""Excepciones personalizadas para las validaciones del sistema."""


class ValorFueraDeRangoError(ValueError):
    """Se lanza cuando un dato numérico sale del rango permitido."""


class RegistroDuplicadoError(ValueError):
    """Se lanza cuando se intenta guardar un registro que ya existe."""


class RegistroNoEncontradoError(LookupError):
    """Se lanza cuando no se encuentra un registro solicitado."""
