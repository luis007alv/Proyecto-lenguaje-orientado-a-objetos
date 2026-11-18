"""Módulo con la clase OrdenServicio que integra cliente, técnico y dispositivo."""

from dispositivo import Computadora, Dispositivo, DispositivoMovil
from excepciones import ValorFueraDeRangoError
from persona import Cliente, Tecnico


class OrdenServicio:
    """Clase principal del negocio que administra el ciclo de vida y costo de una reparación."""

    ESTADOS_VALIDOS = ("En diagnóstico", "Reparación", "Entregado")

    def __init__(
        self,
        folio,
        cliente,
        tecnico,
        dispositivo,
        costoComponentes=0.0,
        costoManoObra=0.0,
        estado="En diagnóstico",
    ):
        self.folio = folio
        self.cliente = cliente
        self.tecnico = tecnico
        self.dispositivo = dispositivo
        self.costoComponentes = costoComponentes
        self.costoManoObra = costoManoObra
        self.estado = estado
        self._costoTotal = 0.0
        self.calcularCosto()

    @property
    def folio(self):
        return self._folio

    @folio.setter
    def folio(self, valor):
        texto = str(valor).strip().upper() if valor is not None else ""
        if not texto:
            raise ValueError("El folio de la orden no puede estar vacío.")
        self._folio = texto

    @property
    def cliente(self):
        return self._cliente

    @cliente.setter
    def cliente(self, valor):
        if not isinstance(valor, Cliente):
            raise TypeError("Debe asignarse un objeto de tipo Cliente.")
        self._cliente = valor

    @property
    def tecnico(self):
        return self._tecnico

    @tecnico.setter
    def tecnico(self, valor):
        if not isinstance(valor, Tecnico):
            raise TypeError("Debe asignarse un objeto de tipo Tecnico.")
        self._tecnico = valor

    @property
    def dispositivo(self):
        return self._dispositivo

    @dispositivo.setter
    def dispositivo(self, valor):
        if not isinstance(valor, Dispositivo):
            raise TypeError("Debe asignarse una Computadora o un DispositivoMovil.")
        self._dispositivo = valor

    def _validarMonto(self, valor, nombreCampo):
        """Valida que un monto sea numérico y esté dentro de un rango lógico."""
        if valor is None or str(valor).strip() == "":
            raise ValueError(f"El campo '{nombreCampo}' no puede estar vacío.")
        try:
            monto = float(valor)
        except (ValueError, TypeError):
            raise ValueError(f"El campo '{nombreCampo}' debe ser un número válido.")
        if monto < 0 or monto > 500000:
            raise ValorFueraDeRangoError(
                f"El campo '{nombreCampo}' debe estar entre 0 y 500,000."
            )
        return round(monto, 2)

    @property
    def costoComponentes(self):
        return self._costoComponentes

    @costoComponentes.setter
    def costoComponentes(self, valor):
        self._costoComponentes = self._validarMonto(valor, "Costo de refacciones")

    @property
    def costoManoObra(self):
        return self._costoManoObra

    @costoManoObra.setter
    def costoManoObra(self, valor):
        self._costoManoObra = self._validarMonto(valor, "Mano de obra")

    @property
    def estado(self):
        return self._estado

    @estado.setter
    def estado(self, valor):
        texto = str(valor).strip() if valor is not None else ""
        if texto not in self.ESTADOS_VALIDOS:
            raise ValueError(
                f"Estado no válido '{texto}'. Usa: {', '.join(self.ESTADOS_VALIDOS)}."
            )
        self._estado = texto

    @property
    def costoTotal(self):
        return self._costoTotal

    @costoTotal.setter
    def costoTotal(self, valor):
        if valor is None or str(valor).strip() == "":
            raise ValueError("El costo total no puede estar vacío.")
        try:
            monto = float(valor)
        except (ValueError, TypeError):
            raise ValueError("El costo total debe ser numérico.")
        if monto < 0:
            raise ValorFueraDeRangoError("El costo total de la orden no puede ser negativo.")
        if monto > 1000000:
            raise ValorFueraDeRangoError("El costo total excede el máximo permitido.")
        self._costoTotal = round(monto, 2)

    def calcularCosto(self):
        """Suma el costo de las refacciones/componentes más la mano de obra."""
        self._costoTotal = round(self._costoComponentes + self._costoManoObra, 2)
        return self._costoTotal

    def cambiarEstado(self, nuevoEstado):
        """Actualiza el estado de progreso de la orden de servicio."""
        self.estado = nuevoEstado

    def generarResumen(self):
        """Genera un ticket-factura estructurado con el desglose de la reparación."""
        return (
            f"========================================\n"
            f"      TICKET DE SERVICIO - {self._folio}\n"
            f"========================================\n"
            f"Estado:      {self._estado}\n"
            f"Cliente:     {self._cliente.nombre} (Tel: {self._cliente.telefono})\n"
            f"Dirección:   {self._cliente.direccion}\n"
            f"Técnico:     {self._tecnico.nombre} ({self._tecnico.especialidad})\n"
            f"Equipo:      {self._dispositivo}\n"
            f"----------------------------------------\n"
            f"Refacciones: ${self._costoComponentes:.2f}\n"
            f"Mano obra:   ${self._costoManoObra:.2f}\n"
            f"TOTAL:       ${self._costoTotal:.2f}\n"
            f"========================================"
        )

    def toDict(self):
        """Convierte la orden completa a diccionario para guardarla en archivo."""
        return {
            "folio": self._folio,
            "estado": self._estado,
            "costoComponentes": self._costoComponentes,
            "costoManoObra": self._costoManoObra,
            "costoTotal": self._costoTotal,
            "cliente": self._cliente.toDict(),
            "tecnico": self._tecnico.toDict(),
            "dispositivo": self._dispositivo.toDict(),
        }

    @classmethod
    def desdeDict(cls, dato):
        """Reconstruye un objeto OrdenServicio (con Computadora o DispositivoMovil) desde un diccionario."""
        datosCliente = dato["cliente"]
        cliente = Cliente(
            datosCliente["nombre"],
            datosCliente["telefono"],
            datosCliente["direccion"],
        )

        datosTecnico = dato["tecnico"]
        tecnico = Tecnico(
            datosTecnico["nombre"],
            datosTecnico["telefono"],
            datosTecnico["especialidad"],
        )

        datosDisp = dato["dispositivo"]
        falla = datosDisp.get("fallaReportada", datosDisp.get("falla", ""))
        tipoDisp = datosDisp.get("tipo", "")

        if tipoDisp == "DispositivoMovil" or ("imei" in datosDisp and datosDisp["imei"]):
            dispositivo = DispositivoMovil(
                datosDisp["marca"],
                datosDisp["modelo"],
                falla,
                datosDisp["imei"],
            )
        else:
            dispositivo = Computadora(
                datosDisp["marca"],
                datosDisp["modelo"],
                falla,
                datosDisp.get("ram", 8),
            )

        orden = cls(
            dato["folio"],
            cliente,
            tecnico,
            dispositivo,
            costoComponentes=dato.get("costoComponentes", 0.0),
            costoManoObra=dato.get("costoManoObra", 0.0),
            estado=dato.get("estado", "En diagnóstico"),
        )
        if "costoTotal" in dato and orden.costoTotal == 0.0 and dato["costoTotal"] > 0:
            orden.costoTotal = dato["costoTotal"]
        return orden

    def __str__(self):
        return (
            f"--- ORDEN {self._folio} [{self._estado}] ---\n"
            f"1. {self._cliente}\n"
            f"2. {self._tecnico}\n"
            f"3. {self._dispositivo}\n"
            f"Refacciones: ${self._costoComponentes:.2f} | Mano de obra: ${self._costoManoObra:.2f}\n"
            f"Total a pagar: ${self._costoTotal:.2f}"
        )
