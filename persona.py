"""Módulo con la clase base Persona y sus clases hijas Cliente y Tecnico."""

from excepciones import ValorFueraDeRangoError


class Persona:
    """Clase base que representa a una persona registrada en el taller."""

    def __init__(self, nombre, telefono):
        self.nombre = nombre
        self.telefono = telefono

    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, valor):
        texto = str(valor).strip() if valor is not None else ""
        if not texto:
            raise ValueError("El nombre no puede estar vacío.")
        self._nombre = texto

    @property
    def telefono(self):
        return self._telefono

    @telefono.setter
    def telefono(self, valor):
        texto = str(valor).strip() if valor is not None else ""
        if not texto:
            raise ValueError("El teléfono no puede estar vacío.")
        soloDigitos = texto.replace("-", "").replace(" ", "")
        if not soloDigitos.isdigit():
            raise ValueError("El teléfono solo debe contener números.")
        if len(soloDigitos) < 8 or len(soloDigitos) > 15:
            raise ValorFueraDeRangoError("El teléfono debe tener entre 8 y 15 dígitos.")
        self._telefono = soloDigitos

    def toDict(self):
        """Convierte los datos básicos de la persona en diccionario."""
        return {
            "nombre": self._nombre,
            "telefono": self._telefono,
        }

    def __str__(self):
        return f"{self._nombre} (Tel: {self._telefono})"


class Cliente(Persona):
    """Clase hija que representa a un cliente del taller con su dirección."""

    def __init__(self, nombre, telefono, direccion):
        super().__init__(nombre, telefono)
        self.direccion = direccion

    @property
    def direccion(self):
        return self._direccion

    @direccion.setter
    def direccion(self, valor):
        texto = str(valor).strip() if valor is not None else ""
        if not texto:
            raise ValueError("La dirección del cliente no puede estar vacía.")
        self._direccion = texto

    def toDict(self):
        """Convierte los datos del cliente en diccionario."""
        datos = super().toDict()
        datos["direccion"] = self._direccion
        return datos

    def __str__(self):
        return f"[Cliente] {super().__str__()} | Dir: {self._direccion}"


class Tecnico(Persona):
    """Clase hija que representa a un técnico del taller y su especialidad."""

    def __init__(self, nombre, telefono, especialidad):
        super().__init__(nombre, telefono)
        self.especialidad = especialidad

    @property
    def especialidad(self):
        return self._especialidad

    @especialidad.setter
    def especialidad(self, valor):
        texto = str(valor).strip() if valor is not None else ""
        if not texto:
            raise ValueError("La especialidad del técnico no puede estar vacía.")
        self._especialidad = texto

    def toDict(self):
        """Convierte los datos del técnico en diccionario."""
        datos = super().toDict()
        datos["especialidad"] = self._especialidad
        return datos

    def __str__(self):
        return f"[Técnico] {super().__str__()} | Esp: {self._especialidad}"
