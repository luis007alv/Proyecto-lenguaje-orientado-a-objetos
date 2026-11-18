"""Módulo con la clase base Dispositivo y sus clases hijas Computadora y DispositivoMovil."""

from excepciones import ValorFueraDeRangoError


class Dispositivo:
    """Clase base para los equipos tecnológicos recibidos en el taller."""

    def __init__(self, marca, modelo, fallaReportada):
        self.marca = marca
        self.modelo = modelo
        self.fallaReportada = fallaReportada

    @property
    def marca(self):
        return self._marca

    @marca.setter
    def marca(self, valor):
        texto = str(valor).strip() if valor is not None else ""
        if not texto:
            raise ValueError("La marca del dispositivo no puede estar vacía.")
        self._marca = texto

    @property
    def modelo(self):
        return self._modelo

    @modelo.setter
    def modelo(self, valor):
        texto = str(valor).strip() if valor is not None else ""
        if not texto:
            raise ValueError("El modelo del dispositivo no puede estar vacío.")
        self._modelo = texto

    @property
    def fallaReportada(self):
        return self._fallaReportada

    @fallaReportada.setter
    def fallaReportada(self, valor):
        texto = str(valor).strip() if valor is not None else ""
        if not texto:
            raise ValueError("La falla reportada no puede estar vacía.")
        self._fallaReportada = texto

    def toDict(self):
        """Convierte los atributos generales del dispositivo en diccionario."""
        return {
            "tipo": "Dispositivo",
            "marca": self._marca,
            "modelo": self._modelo,
            "fallaReportada": self._fallaReportada,
        }

    def __str__(self):
        return f"{self._marca} {self._modelo} - Falla: {self._fallaReportada}"


class Computadora(Dispositivo):
    """Clase hija que modela una computadora portátil o de escritorio con memoria RAM."""

    def __init__(self, marca, modelo, fallaReportada, ram):
        super().__init__(marca, modelo, fallaReportada)
        self.ram = ram

    @property
    def ram(self):
        return self._ram

    @ram.setter
    def ram(self, valor):
        if valor is None or str(valor).strip() == "":
            raise ValueError("La memoria RAM no puede estar vacía.")
        try:
            ramNumero = int(valor)
        except (ValueError, TypeError):
            raise ValueError("La memoria RAM debe ser un número entero.")
        if ramNumero < 1 or ramNumero > 1024:
            raise ValorFueraDeRangoError("La memoria RAM debe estar entre 1 y 1024 GB.")
        self._ram = ramNumero

    def toDict(self):
        """Convierte la computadora a diccionario conservando su tipo y RAM."""
        datos = super().toDict()
        datos["tipo"] = "Computadora"
        datos["ram"] = self._ram
        return datos

    def __str__(self):
        return f"[PC] {super().__str__()} | RAM: {self._ram}GB"


class DispositivoMovil(Dispositivo):
    """Clase hija que modela un celular o tableta identificado por su IMEI."""

    def __init__(self, marca, modelo, fallaReportada, imei):
        super().__init__(marca, modelo, fallaReportada)
        self.imei = imei

    @property
    def imei(self):
        return self._imei

    @imei.setter
    def imei(self, valor):
        texto = str(valor).strip() if valor is not None else ""
        if not texto:
            raise ValueError("El IMEI no puede estar vacío.")
        if not texto.isdigit():
            raise ValueError("El IMEI debe contener solo números.")
        if len(texto) != 15:
            raise ValorFueraDeRangoError("El IMEI debe tener exactamente 15 dígitos.")
        self._imei = texto

    def toDict(self):
        """Convierte el dispositivo móvil a diccionario conservando su tipo e IMEI."""
        datos = super().toDict()
        datos["tipo"] = "DispositivoMovil"
        datos["imei"] = self._imei
        return datos

    def __str__(self):
        return f"[Móvil] {super().__str__()} | IMEI: {self._imei}"
