"""Módulo de persistencia en archivos de texto, base de datos SQLite y bitácora de errores."""

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

from modelos import (
    Cliente,
    Computadora,
    DispositivoMovil,
    OrdenServicio,
    RegistroDuplicadoError,
    RegistroNoEncontradoError,
    Tecnico,
)

# Rutas relativas al módulo para funcionar en cualquier carpeta limpia
carpetaBase = Path(__file__).resolve().parent
rutaLog = carpetaBase / "log_errores.txt"
rutaDatos = carpetaBase / "ordenes_datos.txt"
rutaBaseDatos = carpetaBase / "catalogos_sgrt.db"


def registrarError(mensaje, rutaArchivoLog=None):
    """Registra un error con fecha y hora en el archivo de bitácora en modo agregar."""
    destino = Path(rutaArchivoLog) if rutaArchivoLog else rutaLog
    fechaHora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    linea = f"{fechaHora} | ERROR | {mensaje}\n"
    try:
        with open(destino, "a", encoding="utf-8") as archivo:
            archivo.write(linea)
    except OSError:
        pass


def leerBitacora(rutaArchivoLog=None):
    """Lee el contenido completo del archivo de bitácora de errores."""
    destino = Path(rutaArchivoLog) if rutaArchivoLog else rutaLog
    try:
        with open(destino, "r", encoding="utf-8") as archivo:
            return archivo.read()
    except FileNotFoundError:
        return ""
    except PermissionError as exc:
        registrarError(f"PermissionError: Sin permisos para leer bitácora. {exc}", destino)
        return ""


class GestorArchivos:
    """Concentra la lectura y escritura de órdenes en formato JSON sobre archivo de texto."""

    @staticmethod
    def guardarOrdenes(listaDiccionarios, rutaArchivo=None):
        """Guarda la lista de diccionarios de órdenes en el archivo de texto UTF-8."""
        destino = Path(rutaArchivo) if rutaArchivo else rutaDatos
        try:
            with open(destino, "w", encoding="utf-8") as archivo:
                json.dump(listaDiccionarios, archivo, indent=4, ensure_ascii=False)
        except PermissionError as exc:
            registrarError(f"PermissionError: No se tienen permisos de escritura. {exc}")
            raise
        except OSError as exc:
            registrarError(f"OSError: Error de archivo al guardar órdenes. {exc}")
            raise

    @staticmethod
    def cargarDatosPreconstruidos(rutaArchivo=None):
        """Carga los diccionarios desde el archivo de texto; lo crea si no existe."""
        origen = Path(rutaArchivo) if rutaArchivo else rutaDatos
        if not origen.exists():
            try:
                with open(origen, "w", encoding="utf-8") as archivo:
                    archivo.write("[]")
            except OSError as exc:
                registrarError(f"OSError: No se pudo crear {origen.name}. {exc}")
            return []

        try:
            with open(origen, "r", encoding="utf-8") as archivo:
                contenido = archivo.read().strip()
                if not contenido:
                    return []
                return json.loads(contenido)
        except FileNotFoundError as exc:
            registrarError(f"FileNotFoundError: Archivo de datos no encontrado. {exc}")
            return []
        except PermissionError as exc:
            registrarError(f"PermissionError: Sin permisos para leer {origen.name}. {exc}")
            return []
        except json.JSONDecodeError as exc:
            registrarError(f"JSONDecodeError: Formato inválido en {origen.name}. {exc}")
            return []


class GestorBaseDatos:
    """Administra la persistencia de catálogos y órdenes de servicio en SQLite."""

    def __init__(self, rutaBd=None, rutaTxt=None):
        self._rutaBd = Path(rutaBd) if rutaBd else rutaBaseDatos
        self._rutaTxt = Path(rutaTxt) if rutaTxt else rutaDatos
        self.inicializarTablas()
        self.cargarCatalogosIniciales()

    @contextmanager
    def _conectar(self):
        """Abre y cierra de forma segura una conexión SQLite con soporte de columnas por nombre."""
        conexion = sqlite3.connect(self._rutaBd)
        conexion.row_factory = sqlite3.Row
        try:
            yield conexion
            conexion.commit()
        except Exception:
            conexion.rollback()
            raise
        finally:
            conexion.close()

    def inicializarTablas(self):
        """Crea las tablas del sistema en la base de datos si todavía no existen."""
        try:
            with self._conectar() as conexion:
                cursor = conexion.cursor()
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS configuracion (
                        clave TEXT PRIMARY KEY,
                        valor TEXT NOT NULL
                    )
                    """
                )
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS clientes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nombre TEXT NOT NULL UNIQUE,
                        telefono TEXT NOT NULL,
                        direccion TEXT NOT NULL
                    )
                    """
                )
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS tecnicos (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nombre TEXT NOT NULL UNIQUE,
                        telefono TEXT NOT NULL,
                        especialidad TEXT NOT NULL
                    )
                    """
                )
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS ordenes (
                        folio TEXT PRIMARY KEY,
                        clienteNombre TEXT NOT NULL,
                        clienteTelefono TEXT NOT NULL,
                        clienteDireccion TEXT NOT NULL,
                        tecnicoNombre TEXT NOT NULL,
                        tecnicoTelefono TEXT NOT NULL,
                        tecnicoEspecialidad TEXT NOT NULL,
                        tipoDispositivo TEXT NOT NULL,
                        marca TEXT NOT NULL,
                        modelo TEXT NOT NULL,
                        falla TEXT NOT NULL,
                        ram INTEGER,
                        imei TEXT,
                        costoManoObra REAL NOT NULL,
                        costoRepuestos REAL NOT NULL,
                        descuento REAL NOT NULL,
                        costoTotal REAL NOT NULL,
                        estado TEXT NOT NULL
                    )
                    """
                )
                conexion.commit()
        except sqlite3.Error as exc:
            registrarError(f"sqlite3.Error: Fallo al inicializar tablas. {exc}")
            raise

    def cargarCatalogosIniciales(self):
        """Precarga catálogos base únicamente la primera vez que se crea la base de datos."""
        try:
            with self._conectar() as conexion:
                cursor = conexion.cursor()
                cursor.execute(
                    "SELECT valor FROM configuracion WHERE clave = 'inicializado'"
                )
                fila = cursor.fetchone()
                if fila is not None:
                    return

                clientesBase = [
                    Cliente("Santiago Alarcón", "4421112233", "Av. Constituyentes 120, Centro"),
                    Cliente("Sofía Hernández", "4423456789", "Juriquilla Santa Fe 45"),
                    Cliente("Andrés Martínez", "4429876543", "Álamos 2da Sección 88"),
                ]
                for cliente in clientesBase:
                    cursor.execute(
                        "INSERT OR IGNORE INTO clientes (nombre, telefono, direccion) VALUES (?, ?, ?)",
                        (cliente.nombre, cliente.telefono, cliente.direccion),
                    )

                tecnicosBase = [
                    Tecnico("Samuel Isaza", "4429998877", "Microelectrónica"),
                    Tecnico("Valeria Domínguez", "4425551122", "Dispositivos Móviles"),
                    Tecnico("Carlos Mendoza", "4427773344", "Software y Sistemas"),
                ]
                for tecnico in tecnicosBase:
                    cursor.execute(
                        "INSERT OR IGNORE INTO tecnicos (nombre, telefono, especialidad) VALUES (?, ?, ?)",
                        (tecnico.nombre, tecnico.telefono, tecnico.especialidad),
                    )

                # Si existen órdenes previas en ordenes_datos.txt, las migra a la BD
                datosPrevios = GestorArchivos.cargarDatosPreconstruidos(self._rutaTxt)
                if datosPrevios:
                    for dato in datosPrevios:
                        orden = OrdenServicio.desdeDict(dato)
                        cursor.execute(
                            "INSERT OR IGNORE INTO clientes (nombre, telefono, direccion) VALUES (?, ?, ?)",
                            (orden.cliente.nombre, orden.cliente.telefono, orden.cliente.direccion),
                        )
                        cursor.execute(
                            "INSERT OR IGNORE INTO tecnicos (nombre, telefono, especialidad) VALUES (?, ?, ?)",
                            (orden.tecnico.nombre, orden.tecnico.telefono, orden.tecnico.especialidad),
                        )
                        self._insertarOrdenEnCursor(cursor, orden)
                else:
                    ordenEjemplo = OrdenServicio(
                        "ORD-100",
                        clientesBase[0],
                        tecnicosBase[0],
                        Computadora("Dell", "XPS 13", "Pantalla rota", 16),
                        costoManoObra=1200.0,
                        costoRepuestos=1300.0,
                        descuento=0.0,
                        estado="En reparación",
                    )
                    self._insertarOrdenEnCursor(cursor, ordenEjemplo)

                cursor.execute(
                    "INSERT INTO configuracion (clave, valor) VALUES ('inicializado', '1')"
                )
                conexion.commit()
            self._sincronizarArchivoOrdenes()
        except (sqlite3.Error, ValueError, TypeError) as exc:
            registrarError(f"Error al cargar catálogos iniciales: {exc}")

    def _insertarOrdenEnCursor(self, cursor, orden):
        """Inserta una instancia de OrdenServicio utilizando un cursor SQLite abierto."""
        esMovil = isinstance(orden.dispositivo, DispositivoMovil)
        tipoDisp = "DispositivoMovil" if esMovil else "Computadora"
        ramValor = None if esMovil else orden.dispositivo.ram
        imeiValor = orden.dispositivo.imei if esMovil else None

        cursor.execute(
            """
            INSERT INTO ordenes (
                folio, clienteNombre, clienteTelefono, clienteDireccion,
                tecnicoNombre, tecnicoTelefono, tecnicoEspecialidad,
                tipoDispositivo, marca, modelo, falla, ram, imei,
                costoManoObra, costoRepuestos, descuento, costoTotal, estado
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                orden.folio,
                orden.cliente.nombre,
                orden.cliente.telefono,
                orden.cliente.direccion,
                orden.tecnico.nombre,
                orden.tecnico.telefono,
                orden.tecnico.especialidad,
                tipoDisp,
                orden.dispositivo.marca,
                orden.dispositivo.modelo,
                orden.dispositivo.fallaReportada,
                ramValor,
                imeiValor,
                orden.costoManoObra,
                orden.costoRepuestos,
                orden.descuento,
                orden.costoTotal,
                orden.estado,
            ),
        )

    def _filaAOrden(self, fila):
        """Convierte una fila SQLite en una instancia completa de OrdenServicio."""
        cliente = Cliente(
            fila["clienteNombre"],
            fila["clienteTelefono"],
            fila["clienteDireccion"],
        )
        tecnico = Tecnico(
            fila["tecnicoNombre"],
            fila["tecnicoTelefono"],
            fila["tecnicoEspecialidad"],
        )
        if fila["tipoDispositivo"] == "DispositivoMovil":
            dispositivo = DispositivoMovil(
                fila["marca"], fila["modelo"], fila["falla"], fila["imei"]
            )
        else:
            dispositivo = Computadora(
                fila["marca"], fila["modelo"], fila["falla"], fila["ram"]
            )
        orden = OrdenServicio(
            fila["folio"],
            cliente,
            tecnico,
            dispositivo,
            costoManoObra=fila["costoManoObra"],
            costoRepuestos=fila["costoRepuestos"],
            descuento=fila["descuento"],
            estado=fila["estado"],
        )
        orden.costoTotal = fila["costoTotal"]
        return orden

    def _sincronizarArchivoOrdenes(self):
        """Mantiene actualizado el archivo ordenes_datos.txt con las órdenes de la BD."""
        ordenes = self.obtenerOrdenes()
        listaDiccionarios = [orden.toDict() for orden in ordenes]
        GestorArchivos.guardarOrdenes(listaDiccionarios, self._rutaTxt)

    # --- CRUD CLIENTES ---
    def registrarCliente(self, cliente):
        """Registra un nuevo cliente en el catálogo SQLite."""
        try:
            with self._conectar() as conexion:
                cursor = conexion.cursor()
                cursor.execute(
                    "INSERT INTO clientes (nombre, telefono, direccion) VALUES (?, ?, ?)",
                    (cliente.nombre, cliente.telefono, cliente.direccion),
                )
                conexion.commit()
                return cursor.lastrowid
        except sqlite3.IntegrityError as exc:
            mensaje = f"Ya existe un cliente registrado con el nombre '{cliente.nombre}'."
            registrarError(f"RegistroDuplicadoError: {mensaje} ({exc})")
            raise RegistroDuplicadoError(mensaje) from exc
        except sqlite3.Error as exc:
            registrarError(f"sqlite3.Error al registrar cliente: {exc}")
            raise

    def obtenerClientes(self):
        """Retorna una lista de tuplas (id, Cliente) ordenadas alfabéticamente."""
        try:
            with self._conectar() as conexion:
                cursor = conexion.cursor()
                cursor.execute(
                    "SELECT id, nombre, telefono, direccion FROM clientes ORDER BY nombre ASC"
                )
                resultado = []
                for fila in cursor.fetchall():
                    cliente = Cliente(
                        fila["nombre"], fila["telefono"], fila["direccion"]
                    )
                    resultado.append((fila["id"], cliente))
                return resultado
        except sqlite3.Error as exc:
            registrarError(f"sqlite3.Error al obtener clientes: {exc}")
            return []

    def modificarCliente(self, idCliente, clienteActualizado):
        """Actualiza los datos de un cliente existente por su ID."""
        try:
            with self._conectar() as conexion:
                cursor = conexion.cursor()
                cursor.execute(
                    """
                    UPDATE clientes
                    SET nombre = ?, telefono = ?, direccion = ?
                    WHERE id = ?
                    """,
                    (
                        clienteActualizado.nombre,
                        clienteActualizado.telefono,
                        clienteActualizado.direccion,
                        idCliente,
                    ),
                )
                if cursor.rowcount == 0:
                    raise RegistroNoEncontradoError(
                        f"No existe el cliente con ID {idCliente}."
                    )
                conexion.commit()
        except sqlite3.IntegrityError as exc:
            mensaje = (
                f"Ya existe otro cliente con el nombre '{clienteActualizado.nombre}'."
            )
            registrarError(f"RegistroDuplicadoError: {mensaje} ({exc})")
            raise RegistroDuplicadoError(mensaje) from exc
        except RegistroNoEncontradoError as exc:
            registrarError(f"RegistroNoEncontradoError: {exc}")
            raise
        except sqlite3.Error as exc:
            registrarError(f"sqlite3.Error al modificar cliente: {exc}")
            raise

    def eliminarCliente(self, idCliente):
        """Elimina un cliente existente del catálogo por su ID."""
        try:
            with self._conectar() as conexion:
                cursor = conexion.cursor()
                cursor.execute("DELETE FROM clientes WHERE id = ?", (idCliente,))
                if cursor.rowcount == 0:
                    raise RegistroNoEncontradoError(
                        f"No se encontró el cliente con ID {idCliente} para eliminar."
                    )
                conexion.commit()
        except RegistroNoEncontradoError as exc:
            registrarError(f"RegistroNoEncontradoError: {exc}")
            raise
        except sqlite3.Error as exc:
            registrarError(f"sqlite3.Error al eliminar cliente: {exc}")
            raise

    # --- CRUD TÉCNICOS ---
    def registrarTecnico(self, tecnico):
        """Registra un nuevo técnico en el catálogo SQLite."""
        try:
            with self._conectar() as conexion:
                cursor = conexion.cursor()
                cursor.execute(
                    "INSERT INTO tecnicos (nombre, telefono, especialidad) VALUES (?, ?, ?)",
                    (tecnico.nombre, tecnico.telefono, tecnico.especialidad),
                )
                conexion.commit()
                return cursor.lastrowid
        except sqlite3.IntegrityError as exc:
            mensaje = f"Ya existe un técnico registrado con el nombre '{tecnico.nombre}'."
            registrarError(f"RegistroDuplicadoError: {mensaje} ({exc})")
            raise RegistroDuplicadoError(mensaje) from exc
        except sqlite3.Error as exc:
            registrarError(f"sqlite3.Error al registrar técnico: {exc}")
            raise

    def obtenerTecnicos(self):
        """Retorna una lista de tuplas (id, Tecnico) ordenadas alfabéticamente."""
        try:
            with self._conectar() as conexion:
                cursor = conexion.cursor()
                cursor.execute(
                    "SELECT id, nombre, telefono, especialidad FROM tecnicos ORDER BY nombre ASC"
                )
                resultado = []
                for fila in cursor.fetchall():
                    tecnico = Tecnico(
                        fila["nombre"], fila["telefono"], fila["especialidad"]
                    )
                    resultado.append((fila["id"], tecnico))
                return resultado
        except sqlite3.Error as exc:
            registrarError(f"sqlite3.Error al obtener técnicos: {exc}")
            return []

    def modificarTecnico(self, idTecnico, tecnicoActualizado):
        """Actualiza los datos de un técnico existente por su ID."""
        try:
            with self._conectar() as conexion:
                cursor = conexion.cursor()
                cursor.execute(
                    """
                    UPDATE tecnicos
                    SET nombre = ?, telefono = ?, especialidad = ?
                    WHERE id = ?
                    """,
                    (
                        tecnicoActualizado.nombre,
                        tecnicoActualizado.telefono,
                        tecnicoActualizado.especialidad,
                        idTecnico,
                    ),
                )
                if cursor.rowcount == 0:
                    raise RegistroNoEncontradoError(
                        f"No existe el técnico con ID {idTecnico}."
                    )
                conexion.commit()
        except sqlite3.IntegrityError as exc:
            mensaje = (
                f"Ya existe otro técnico con el nombre '{tecnicoActualizado.nombre}'."
            )
            registrarError(f"RegistroDuplicadoError: {mensaje} ({exc})")
            raise RegistroDuplicadoError(mensaje) from exc
        except RegistroNoEncontradoError as exc:
            registrarError(f"RegistroNoEncontradoError: {exc}")
            raise
        except sqlite3.Error as exc:
            registrarError(f"sqlite3.Error al modificar técnico: {exc}")
            raise

    def eliminarTecnico(self, idTecnico):
        """Elimina un técnico existente del catálogo por su ID."""
        try:
            with self._conectar() as conexion:
                cursor = conexion.cursor()
                cursor.execute("DELETE FROM tecnicos WHERE id = ?", (idTecnico,))
                if cursor.rowcount == 0:
                    raise RegistroNoEncontradoError(
                        f"No se encontró el técnico con ID {idTecnico} para eliminar."
                    )
                conexion.commit()
        except RegistroNoEncontradoError as exc:
            registrarError(f"RegistroNoEncontradoError: {exc}")
            raise
        except sqlite3.Error as exc:
            registrarError(f"sqlite3.Error al eliminar técnico: {exc}")
            raise

    # --- CRUD ÓRDENES DE SERVICIO ---
    def registrarOrden(self, orden):
        """Registra una nueva orden de servicio y la sincroniza en el archivo de texto."""
        try:
            with self._conectar() as conexion:
                cursor = conexion.cursor()
                self._insertarOrdenEnCursor(cursor, orden)
                conexion.commit()
            self._sincronizarArchivoOrdenes()
        except sqlite3.IntegrityError as exc:
            mensaje = f"El folio '{orden.folio}' ya se encuentra registrado."
            registrarError(f"RegistroDuplicadoError: {mensaje} ({exc})")
            raise RegistroDuplicadoError(mensaje) from exc
        except sqlite3.Error as exc:
            registrarError(f"sqlite3.Error al registrar orden: {exc}")
            raise

    def obtenerOrdenes(self):
        """Obtiene todas las órdenes de servicio reconstruidas como objetos OrdenServicio."""
        try:
            with self._conectar() as conexion:
                cursor = conexion.cursor()
                cursor.execute("SELECT * FROM ordenes ORDER BY folio ASC")
                return [self._filaAOrden(fila) for fila in cursor.fetchall()]
        except sqlite3.Error as exc:
            registrarError(f"sqlite3.Error al listar órdenes: {exc}")
            return []

    def buscarOrdenes(self, criterio):
        """Consulta órdenes por folio o nombre de cliente; lanza error si no hay coincidencias."""
        texto = str(criterio).strip() if criterio is not None else ""
        if not texto:
            raise ValueError("Ingresa un folio o nombre de cliente para consultar.")
        try:
            with self._conectar() as conexion:
                cursor = conexion.cursor()
                patron = f"%{texto}%"
                cursor.execute(
                    """
                    SELECT * FROM ordenes
                    WHERE UPPER(folio) LIKE UPPER(?) OR LOWER(clienteNombre) LIKE LOWER(?)
                    ORDER BY folio ASC
                    """,
                    (patron, patron),
                )
                filas = cursor.fetchall()
                if not filas:
                    raise RegistroNoEncontradoError(
                        f"No se encontraron órdenes que coincidan con '{texto}'."
                    )
                return [self._filaAOrden(fila) for fila in filas]
        except RegistroNoEncontradoError as exc:
            registrarError(f"RegistroNoEncontradoError: {exc}")
            raise
        except sqlite3.Error as exc:
            registrarError(f"sqlite3.Error al buscar órdenes: {exc}")
            raise

    def modificarOrden(self, orden):
        """Actualiza una orden existente identificada por su folio y sincroniza el respaldo."""
        esMovil = isinstance(orden.dispositivo, DispositivoMovil)
        tipoDisp = "DispositivoMovil" if esMovil else "Computadora"
        ramValor = None if esMovil else orden.dispositivo.ram
        imeiValor = orden.dispositivo.imei if esMovil else None

        try:
            with self._conectar() as conexion:
                cursor = conexion.cursor()
                cursor.execute(
                    """
                    UPDATE ordenes SET
                        clienteNombre = ?, clienteTelefono = ?, clienteDireccion = ?,
                        tecnicoNombre = ?, tecnicoTelefono = ?, tecnicoEspecialidad = ?,
                        tipoDispositivo = ?, marca = ?, modelo = ?, falla = ?,
                        ram = ?, imei = ?, costoManoObra = ?, costoRepuestos = ?,
                        descuento = ?, costoTotal = ?, estado = ?
                    WHERE folio = ?
                    """,
                    (
                        orden.cliente.nombre,
                        orden.cliente.telefono,
                        orden.cliente.direccion,
                        orden.tecnico.nombre,
                        orden.tecnico.telefono,
                        orden.tecnico.especialidad,
                        tipoDisp,
                        orden.dispositivo.marca,
                        orden.dispositivo.modelo,
                        orden.dispositivo.fallaReportada,
                        ramValor,
                        imeiValor,
                        orden.costoManoObra,
                        orden.costoRepuestos,
                        orden.descuento,
                        orden.costoTotal,
                        orden.estado,
                        orden.folio,
                    ),
                )
                if cursor.rowcount == 0:
                    raise RegistroNoEncontradoError(
                        f"No existe una orden registrada con el folio '{orden.folio}'."
                    )
                conexion.commit()
            self._sincronizarArchivoOrdenes()
        except RegistroNoEncontradoError as exc:
            registrarError(f"RegistroNoEncontradoError: {exc}")
            raise
        except sqlite3.Error as exc:
            registrarError(f"sqlite3.Error al modificar orden: {exc}")
            raise

    def eliminarOrden(self, folio):
        """Elimina una orden existente por su folio y sincroniza el respaldo."""
        folioNormalizado = str(folio).strip().upper() if folio is not None else ""
        if not folioNormalizado:
            raise ValueError("Debes indicar el folio de la orden a eliminar.")
        try:
            with self._conectar() as conexion:
                cursor = conexion.cursor()
                cursor.execute(
                    "DELETE FROM ordenes WHERE folio = ?", (folioNormalizado,)
                )
                if cursor.rowcount == 0:
                    raise RegistroNoEncontradoError(
                        f"No existe una orden registrada con el folio '{folioNormalizado}'."
                    )
                conexion.commit()
            self._sincronizarArchivoOrdenes()
        except RegistroNoEncontradoError as exc:
            registrarError(f"RegistroNoEncontradoError: {exc}")
            raise
        except sqlite3.Error as exc:
            registrarError(f"sqlite3.Error al eliminar orden: {exc}")
            raise
