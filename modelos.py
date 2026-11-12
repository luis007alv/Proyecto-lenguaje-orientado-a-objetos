"""Módulo de modelos de negocio y excepciones personalizadas para el SGRT."""


class ValorFueraDeRangoError(ValueError):
    """Excepción lanzada cuando un valor numérico está fuera del rango permitido."""


class RegistroDuplicadoError(ValueError):
    """Excepción lanzada al intentar registrar una clave o folio ya existente."""


class RegistroNoEncontradoError(LookupError):
    """Excepción lanzada al consultar, modificar o eliminar un registro inexistente."""


# --- CLASES BASE E HIJAS (PERSONAS) ---
class Persona:
    """Clase base que representa a una persona dentro del sistema de reparaciones."""

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
        limpio = texto.replace("-", "").replace(" ", "")
        if not limpio.isdigit():
            raise ValueError("El teléfono debe contener únicamente dígitos numéricos.")
        if len(limpio) < 8 or len(limpio) > 15:
            raise ValorFueraDeRangoError(
                "El teléfono debe tener entre 8 y 15 dígitos."
            )
        self._telefono = limpio

    def toDict(self):
        """Convierte los atributos básicos de la persona a diccionario."""
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
        """Convierte los datos del cliente a diccionario."""
        datos = super().toDict()
        datos["direccion"] = self._direccion
        return datos

    def __str__(self):
        return f"[Cliente] {super().__str__()} | Dir: {self._direccion}"


class Tecnico(Persona):
    """Clase hija que representa a un técnico especialista del taller."""

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
        """Convierte los datos del técnico a diccionario."""
        datos = super().toDict()
        datos["especialidad"] = self._especialidad
        return datos

    def __str__(self):
        return f"[Técnico] {super().__str__()} | Esp: {self._especialidad}"


# --- CLASES BASE E HIJAS (DISPOSITIVOS) ---
class Dispositivo:
    """Clase base que modela un equipo electrónico recibido para reparación."""

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
        """Convierte los datos generales del dispositivo a diccionario."""
        return {
            "tipo": "Dispositivo",
            "marca": self._marca,
            "modelo": self._modelo,
            "falla": self._fallaReportada,
        }

    def __str__(self):
        return f"{self._marca} {self._modelo} - Falla: {self._fallaReportada}"


class Computadora(Dispositivo):
    """Clase hija para computadoras de escritorio o portátiles con capacidad RAM."""

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
            ramEntero = int(valor)
        except (ValueError, TypeError) as exc:
            raise ValueError("La memoria RAM debe ser un número entero válido.") from exc
        if ramEntero < 1 or ramEntero > 1024:
            raise ValorFueraDeRangoError(
                "La memoria RAM debe estar en un rango de 1 a 1024 GB."
            )
        self._ram = ramEntero

    def toDict(self):
        """Convierte la computadora a diccionario preservando su tipo y RAM."""
        datos = super().toDict()
        datos["tipo"] = "Computadora"
        datos["ram"] = self._ram
        return datos

    def __str__(self):
        return f"[PC] {super().__str__()} | RAM: {self._ram}GB"


class DispositivoMovil(Dispositivo):
    """Clase hija para teléfonos inteligentes o tabletas con identificador IMEI."""

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
            raise ValueError("El IMEI debe contener únicamente números.")
        if len(texto) != 15:
            raise ValorFueraDeRangoError(
                "El IMEI debe tener exactamente 15 dígitos."
            )
        self._imei = texto

    def toDict(self):
        """Convierte el dispositivo móvil a diccionario preservando su tipo e IMEI."""
        datos = super().toDict()
        datos["tipo"] = "DispositivoMovil"
        datos["imei"] = self._imei
        return datos

    def __str__(self):
        return f"[Móvil] {super().__str__()} | IMEI: {self._imei}"


# --- CLASE GESTORA ---
class OrdenServicio:
    """Clase que vincula cliente, técnico y dispositivo en una orden de reparación."""

    ESTADOS_VALIDOS = (
        "Recibido",
        "En diagnóstico",
        "En reparación",
        "Listo",
        "Entregado",
    )

    def __init__(
        self,
        folio,
        cliente,
        tecnico,
        dispositivo,
        costoManoObra=0.0,
        costoRepuestos=0.0,
        descuento=0.0,
        estado="Recibido",
    ):
        self.folio = folio
        self.cliente = cliente
        self.tecnico = tecnico
        self.dispositivo = dispositivo
        self.costoManoObra = costoManoObra
        self.costoRepuestos = costoRepuestos
        self.descuento = descuento
        self.estado = estado
        self._costoTotal = 0.0
        if self._costoManoObra > 0 or self._costoRepuestos > 0 or self._descuento > 0:
            self.calcularCostoTotal()

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
            raise TypeError("El cliente debe ser una instancia de la clase Cliente.")
        self._cliente = valor

    @property
    def tecnico(self):
        return self._tecnico

    @tecnico.setter
    def tecnico(self, valor):
        if not isinstance(valor, Tecnico):
            raise TypeError("El técnico debe ser una instancia de la clase Tecnico.")
        self._tecnico = valor

    @property
    def dispositivo(self):
        return self._dispositivo

    @dispositivo.setter
    def dispositivo(self, valor):
        if not isinstance(valor, Dispositivo):
            raise TypeError(
                "El dispositivo debe ser una instancia de Computadora o DispositivoMovil."
            )
        self._dispositivo = valor

    def _validarMonto(self, valor, nombreCampo):
        """Valida que un monto sea numérico y se encuentre dentro del rango permitido."""
        if valor is None or str(valor).strip() == "":
            raise ValueError(f"El campo '{nombreCampo}' no puede estar vacío.")
        try:
            monto = float(valor)
        except (ValueError, TypeError) as exc:
            raise ValueError(
                f"El campo '{nombreCampo}' debe ser un valor numérico válido."
            ) from exc
        if monto < 0 or monto > 1000000:
            raise ValorFueraDeRangoError(
                f"El campo '{nombreCampo}' debe estar entre 0 y 1,000,000."
            )
        return round(monto, 2)

    @property
    def costoManoObra(self):
        return self._costoManoObra

    @costoManoObra.setter
    def costoManoObra(self, valor):
        self._costoManoObra = self._validarMonto(valor, "Mano de obra")

    @property
    def costoRepuestos(self):
        return self._costoRepuestos

    @costoRepuestos.setter
    def costoRepuestos(self, valor):
        self._costoRepuestos = self._validarMonto(valor, "Repuestos")

    @property
    def descuento(self):
        return self._descuento

    @descuento.setter
    def descuento(self, valor):
        self._descuento = self._validarMonto(valor, "Descuento")

    @property
    def estado(self):
        return self._estado

    @estado.setter
    def estado(self, valor):
        texto = str(valor).strip() if valor is not None else ""
        if texto not in self.ESTADOS_VALIDOS:
            raise ValueError(
                f"Estado inválido '{texto}'. Valores permitidos: {', '.join(self.ESTADOS_VALIDOS)}."
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
        except (ValueError, TypeError) as exc:
            raise ValueError("El costo total debe ser un número válido.") from exc
        if monto < 0:
            raise ValorFueraDeRangoError(
                "El costo total de la orden no puede ser negativo."
            )
        if monto > 2000000:
            raise ValorFueraDeRangoError(
                "El costo total excede el límite permitido (2,000,000)."
            )
        self._costoTotal = round(monto, 2)

    def calcularSubtotal(self):
        """Calcula el subtotal sumando mano de obra y repuestos."""
        return round(self._costoManoObra + self._costoRepuestos, 2)

    def calcularCostoTotal(self):
        """Calcula y actualiza el costo total validando que el descuento no supere el subtotal."""
        subtotal = self.calcularSubtotal()
        if self._descuento > subtotal:
            raise ValorFueraDeRangoError(
                "El descuento no puede ser mayor al subtotal (mano de obra + repuestos)."
            )
        self._costoTotal = round(subtotal - self._descuento, 2)
        return self._costoTotal

    def calcularIva(self, tasa=0.16):
        """Calcula el IVA informativo correspondiente al costo total de la orden."""
        return round(self._costoTotal * tasa, 2)

    def toDict(self):
        """Convierte la orden y sus objetos asociados a un diccionario serializable."""
        return {
            "folio": self._folio,
            "estado": self._estado,
            "costoManoObra": self._costoManoObra,
            "costoRepuestos": self._costoRepuestos,
            "descuento": self._descuento,
            "costoTotal": self._costoTotal,
            "cliente": self._cliente.toDict(),
            "tecnico": self._tecnico.toDict(),
            "dispositivo": self._dispositivo.toDict(),
        }

    @classmethod
    def desdeDict(cls, dato):
        """Reconstruye una instancia completa de OrdenServicio desde un diccionario."""
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
        tipoDisp = datosDisp.get("tipo")
        if tipoDisp == "DispositivoMovil" or (
            tipoDisp is None and datosDisp.get("imei") is not None
        ):
            dispositivo = DispositivoMovil(
                datosDisp["marca"],
                datosDisp["modelo"],
                datosDisp["falla"],
                datosDisp["imei"],
            )
        else:
            ramValor = datosDisp.get("ram", 8)
            dispositivo = Computadora(
                datosDisp["marca"],
                datosDisp["modelo"],
                datosDisp["falla"],
                ramValor,
            )

        orden = cls(
            dato["folio"],
            cliente,
            tecnico,
            dispositivo,
            costoManoObra=dato.get("costoManoObra", 0.0),
            costoRepuestos=dato.get("costoRepuestos", 0.0),
            descuento=dato.get("descuento", 0.0),
            estado=dato.get("estado", "Recibido"),
        )
        if "costoTotal" in dato:
            orden.costoTotal = dato["costoTotal"]
        return orden

    def __str__(self):
        return (
            f"--- ORDEN {self._folio} [{self._estado}] ---\n"
            f"1. {self._cliente}\n"
            f"2. {self._tecnico}\n"
            f"3. {self._dispositivo}\n"
            f"Mano de obra: ${self._costoManoObra:.2f} | "
            f"Repuestos: ${self._costoRepuestos:.2f} | "
            f"Descuento: ${self._descuento:.2f}\n"
            f"Total a pagar: ${self._costoTotal:.2f} "
            f"(IVA incl. ref.: ${self.calcularIva():.2f})"
        )
