"""Módulo de persistencia en archivo de texto, base de datos SQLite y bitácora de errores."""

import json
import sqlite3
from datetime import datetime
from pathlib import Path

from dispositivo import DispositivoMovil
from excepciones import RegistroDuplicadoError, RegistroNoEncontradoError
from orden_servicio import OrdenServicio
from persona import Cliente, Tecnico

carpetaBase = Path(__file__).resolve().parent
rutaLog = carpetaBase / "log_errores.txt"
rutaDatos = carpetaBase / "ordenes_datos.txt"
rutaBaseDatos = carpetaBase / "catalogos_sgrt.db"


def registrarError(mensaje, rutaArchivoLog=None):
    """Escribe una línea con fecha y hora en log_errores.txt en modo agregar."""
    destino = Path(rutaArchivoLog) if rutaArchivoLog else rutaLog
    fechaHora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    linea = f"{fechaHora} | ERROR | {mensaje}\n"
    try:
        with open(destino, "a", encoding="utf-8") as archivo:
            archivo.write(linea)
    except OSError:
        pass


def leerLog(rutaArchivoLog=None):
    """Lee el contenido de log_errores.txt para mostrarlo en la interfaz."""
    destino = Path(rutaArchivoLog) if rutaArchivoLog else rutaLog
    try:
        with open(destino, "r", encoding="utf-8") as archivo:
            return archivo.read()
    except FileNotFoundError:
        return ""
    except PermissionError as e:
        registrarError(f"PermissionError: Sin permiso para leer el log. {e}", destino)
        return ""


class GestorArchivos:
    """Clase encargada de guardar y cargar las órdenes en archivo de texto."""

    @staticmethod
    def guardarOrdenes(listaOrdenes, rutaArchivo=None):
        """Guarda una lista de objetos OrdenServicio (o diccionarios) en ordenes_datos.txt."""
        destino = Path(rutaArchivo) if rutaArchivo else rutaDatos
        datos = []
        for item in listaOrdenes:
            if isinstance(item, OrdenServicio):
                datos.append(item.toDict())
            else:
                datos.append(item)

        try:
            with open(destino, "w", encoding="utf-8") as archivo:
                json.dump(datos, archivo, indent=4, ensure_ascii=False)
        except PermissionError as e:
            registrarError(f"PermissionError: No se pudo escribir en {destino.name}. {e}")
            raise
        except OSError as e:
            registrarError(f"OSError: Error al guardar {destino.name}. {e}")
            raise

    @staticmethod
    def cargarOrdenes(rutaArchivo=None):
        """Lee ordenes_datos.txt y reconstruye objetos OrdenServicio. Crea el archivo si falta."""
        origen = Path(rutaArchivo) if rutaArchivo else rutaDatos
        try:
            with open(origen, "r", encoding="utf-8") as archivo:
                contenido = archivo.read().strip()
                if not contenido:
                    return []
                datosCrudos = json.loads(contenido)
                return [OrdenServicio.desdeDict(d) for d in datosCrudos]
        except FileNotFoundError as e:
            registrarError(f"FileNotFoundError: No existía {origen.name}, se creó vacío. {e}")
            try:
                with open(origen, "w", encoding="utf-8") as nuevo:
                    nuevo.write("[]")
            except OSError as errCrear:
                registrarError(f"OSError: No se pudo crear {origen.name}. {errCrear}")
            return []
        except json.JSONDecodeError as e:
            registrarError(f"JSONDecodeError: Archivo {origen.name} vacío o con formato inválido. {e}")
            return []
        except PermissionError as e:
            registrarError(f"PermissionError: Sin permiso para leer {origen.name}. {e}")
            return []


class GestorBaseDatos:
    """Administra el almacenamiento en SQLite de los catálogos de clientes, técnicos y órdenes."""

    def __init__(self, rutaBd=None, rutaTxt=None):
        self._rutaBd = Path(rutaBd) if rutaBd else rutaBaseDatos
        self._rutaTxt = Path(rutaTxt) if rutaTxt else rutaDatos
        self.crearTablas()
        self.cargarDatosIniciales()

    def _abrirConexion(self):
        """Abre una conexión con la base de datos SQLite."""
        return sqlite3.connect(self._rutaBd)

    def crearTablas(self):
        """Crea las tablas de clientes, técnicos y órdenes si aún no existen."""
        conexion = None
        try:
            conexion = self._abrirConexion()
            cursor = conexion.cursor()
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
                    fallaReportada TEXT NOT NULL,
                    ram INTEGER,
                    imei TEXT,
                    costoComponentes REAL NOT NULL,
                    costoManoObra REAL NOT NULL,
                    costoTotal REAL NOT NULL,
                    estado TEXT NOT NULL
                )
                """
            )
            conexion.commit()
        except sqlite3.Error as e:
            registrarError(f"sqlite3.Error: Error al crear tablas. {e}")
            raise
        finally:
            if conexion:
                conexion.close()

    def cargarDatosIniciales(self):
        """Inserta registros iniciales de ejemplo si la base de datos está vacía."""
        if self.obtenerClientes() or self.obtenerTecnicos() or self.obtenerOrdenes():
            return

        try:
            c1 = Cliente("Santiago Alarcón", "4421112233", "Centro Histórico, Querétaro")
            c2 = Cliente("Sofía Hernández", "4423456789", "Juriquilla Santa Fe 45")
            self.registrarCliente(c1)
            self.registrarCliente(c2)

            t1 = Tecnico("Luis Álvarez", "4429998877", "Microelectrónica")
            t2 = Tecnico("Valeria Domínguez", "4425551122", "Dispositivos Móviles")
            self.registrarTecnico(t1)
            self.registrarTecnico(t2)

            from dispositivo import Computadora

            pc = Computadora("Dell", "XPS 13", "Pantalla rota", 16)
            movil = DispositivoMovil("Samsung", "Galaxy S23", "Batería inflada", "356789012345678")

            orden1 = OrdenServicio("ORD-100", c1, t1, pc, 1500.0, 1000.0, "Reparación")
            orden2 = OrdenServicio("ORD-101", c2, t2, movil, 850.0, 500.0, "En diagnóstico")
            self.registrarOrden(orden1)
            self.registrarOrden(orden2)
        except Exception as e:
            registrarError(f"{type(e).__name__}: Error al cargar datos iniciales. {e}")

    def _sincronizarTxt(self):
        """Actualiza ordenes_datos.txt con las órdenes guardadas en la base de datos."""
        ordenes = self.obtenerOrdenes()
        GestorArchivos.guardarOrdenes(ordenes, self._rutaTxt)

    # --- OPERACIONES CLIENTES ---
    def registrarCliente(self, cliente):
        """Inserta un nuevo cliente en la tabla clientes."""
        conexion = None
        try:
            conexion = self._abrirConexion()
            cursor = conexion.cursor()
            cursor.execute(
                "INSERT INTO clientes (nombre, telefono, direccion) VALUES (?, ?, ?)",
                (cliente.nombre, cliente.telefono, cliente.direccion),
            )
            conexion.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError as e:
            msg = f"Ya existe un cliente registrado con el nombre '{cliente.nombre}'."
            registrarError(f"RegistroDuplicadoError: {msg} ({e})")
            raise RegistroDuplicadoError(msg)
        except sqlite3.Error as e:
            registrarError(f"sqlite3.Error al registrar cliente: {e}")
            raise
        finally:
            if conexion:
                conexion.close()

    def obtenerClientes(self):
        """Devuelve una lista de tuplas (id, Cliente) ordenadas por nombre."""
        conexion = None
        try:
            conexion = self._abrirConexion()
            cursor = conexion.cursor()
            cursor.execute(
                "SELECT id, nombre, telefono, direccion FROM clientes ORDER BY nombre ASC"
            )
            filas = cursor.fetchall()
            return [(f[0], Cliente(f[1], f[2], f[3])) for f in filas]
        except sqlite3.Error as e:
            registrarError(f"sqlite3.Error al consultar clientes: {e}")
            return []
        finally:
            if conexion:
                conexion.close()

    def modificarCliente(self, idCliente, cliente):
        """Actualiza los datos de un cliente existente por su ID."""
        conexion = None
        try:
            conexion = self._abrirConexion()
            cursor = conexion.cursor()
            cursor.execute(
                "UPDATE clientes SET nombre = ?, telefono = ?, direccion = ? WHERE id = ?",
                (cliente.nombre, cliente.telefono, cliente.direccion, idCliente),
            )
            if cursor.rowcount == 0:
                raise RegistroNoEncontradoError(f"No existe el cliente con ID {idCliente}.")
            conexion.commit()
        except sqlite3.IntegrityError as e:
            msg = f"Ya existe otro cliente con el nombre '{cliente.nombre}'."
            registrarError(f"RegistroDuplicadoError: {msg} ({e})")
            raise RegistroDuplicadoError(msg)
        except RegistroNoEncontradoError as e:
            registrarError(f"RegistroNoEncontradoError: {e}")
            raise
        except sqlite3.Error as e:
            registrarError(f"sqlite3.Error al modificar cliente: {e}")
            raise
        finally:
            if conexion:
                conexion.close()

    def eliminarCliente(self, idCliente):
        """Elimina un cliente de la base de datos por su ID."""
        conexion = None
        try:
            conexion = self._abrirConexion()
            cursor = conexion.cursor()
            cursor.execute("DELETE FROM clientes WHERE id = ?", (idCliente,))
            if cursor.rowcount == 0:
                raise RegistroNoEncontradoError(f"No se encontró el cliente con ID {idCliente}.")
            conexion.commit()
        except RegistroNoEncontradoError as e:
            registrarError(f"RegistroNoEncontradoError: {e}")
            raise
        except sqlite3.Error as e:
            registrarError(f"sqlite3.Error al eliminar cliente: {e}")
            raise
        finally:
            if conexion:
                conexion.close()

    # --- OPERACIONES TÉCNICOS ---
    def registrarTecnico(self, tecnico):
        """Inserta un nuevo técnico en la tabla tecnicos."""
        conexion = None
        try:
            conexion = self._abrirConexion()
            cursor = conexion.cursor()
            cursor.execute(
                "INSERT INTO tecnicos (nombre, telefono, especialidad) VALUES (?, ?, ?)",
                (tecnico.nombre, tecnico.telefono, tecnico.especialidad),
            )
            conexion.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError as e:
            msg = f"Ya existe un técnico registrado con el nombre '{tecnico.nombre}'."
            registrarError(f"RegistroDuplicadoError: {msg} ({e})")
            raise RegistroDuplicadoError(msg)
        except sqlite3.Error as e:
            registrarError(f"sqlite3.Error al registrar técnico: {e}")
            raise
        finally:
            if conexion:
                conexion.close()

    def obtenerTecnicos(self):
        """Devuelve una lista de tuplas (id, Tecnico) ordenadas por nombre."""
        conexion = None
        try:
            conexion = self._abrirConexion()
            cursor = conexion.cursor()
            cursor.execute(
                "SELECT id, nombre, telefono, especialidad FROM tecnicos ORDER BY nombre ASC"
            )
            filas = cursor.fetchall()
            return [(f[0], Tecnico(f[1], f[2], f[3])) for f in filas]
        except sqlite3.Error as e:
            registrarError(f"sqlite3.Error al consultar técnicos: {e}")
            return []
        finally:
            if conexion:
                conexion.close()

    def modificarTecnico(self, idTecnico, tecnico):
        """Actualiza los datos de un técnico existente por su ID."""
        conexion = None
        try:
            conexion = self._abrirConexion()
            cursor = conexion.cursor()
            cursor.execute(
                "UPDATE tecnicos SET nombre = ?, telefono = ?, especialidad = ? WHERE id = ?",
                (tecnico.nombre, tecnico.telefono, tecnico.especialidad, idTecnico),
            )
            if cursor.rowcount == 0:
                raise RegistroNoEncontradoError(f"No existe el técnico con ID {idTecnico}.")
            conexion.commit()
        except sqlite3.IntegrityError as e:
            msg = f"Ya existe otro técnico con el nombre '{tecnico.nombre}'."
            registrarError(f"RegistroDuplicadoError: {msg} ({e})")
            raise RegistroDuplicadoError(msg)
        except RegistroNoEncontradoError as e:
            registrarError(f"RegistroNoEncontradoError: {e}")
            raise
        except sqlite3.Error as e:
            registrarError(f"sqlite3.Error al modificar técnico: {e}")
            raise
        finally:
            if conexion:
                conexion.close()

    def eliminarTecnico(self, idTecnico):
        """Elimina un técnico de la base de datos por su ID."""
        conexion = None
        try:
            conexion = self._abrirConexion()
            cursor = conexion.cursor()
            cursor.execute("DELETE FROM tecnicos WHERE id = ?", (idTecnico,))
            if cursor.rowcount == 0:
                raise RegistroNoEncontradoError(f"No se encontró el técnico con ID {idTecnico}.")
            conexion.commit()
        except RegistroNoEncontradoError as e:
            registrarError(f"RegistroNoEncontradoError: {e}")
            raise
        except sqlite3.Error as e:
            registrarError(f"sqlite3.Error al eliminar técnico: {e}")
            raise
        finally:
            if conexion:
                conexion.close()

    # --- OPERACIONES ÓRDENES ---
    def _filaAOrden(self, fila):
        """Reconstruye un objeto OrdenServicio desde una tupla obtenida de SQLite."""
        from dispositivo import Computadora

        cliente = Cliente(fila[1], fila[2], fila[3])
        tecnico = Tecnico(fila[4], fila[5], fila[6])
        if fila[7] == "DispositivoMovil":
            dispositivo = DispositivoMovil(fila[8], fila[9], fila[10], fila[12])
        else:
            dispositivo = Computadora(fila[8], fila[9], fila[10], fila[11])

        orden = OrdenServicio(
            fila[0],
            cliente,
            tecnico,
            dispositivo,
            costoComponentes=fila[13],
            costoManoObra=fila[14],
            estado=fila[16],
        )
        orden.costoTotal = fila[15]
        return orden

    def registrarOrden(self, orden):
        """Guarda una nueva orden en SQLite y actualiza ordenes_datos.txt."""
        esMovil = isinstance(orden.dispositivo, DispositivoMovil)
        tipoDisp = "DispositivoMovil" if esMovil else "Computadora"
        ramValor = None if esMovil else orden.dispositivo.ram
        imeiValor = orden.dispositivo.imei if esMovil else None

        conexion = None
        try:
            conexion = self._abrirConexion()
            cursor = conexion.cursor()
            cursor.execute(
                """
                INSERT INTO ordenes VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                    orden.costoComponentes,
                    orden.costoManoObra,
                    orden.costoTotal,
                    orden.estado,
                ),
            )
            conexion.commit()
            self._sincronizarTxt()
        except sqlite3.IntegrityError as e:
            msg = f"El folio '{orden.folio}' ya está registrado."
            registrarError(f"RegistroDuplicadoError: {msg} ({e})")
            raise RegistroDuplicadoError(msg)
        except sqlite3.Error as e:
            registrarError(f"sqlite3.Error al registrar orden: {e}")
            raise
        finally:
            if conexion:
                conexion.close()

    def obtenerOrdenes(self):
        """Devuelve todas las órdenes almacenadas en la base de datos."""
        conexion = None
        try:
            conexion = self._abrirConexion()
            cursor = conexion.cursor()
            cursor.execute("SELECT * FROM ordenes ORDER BY folio ASC")
            return [self._filaAOrden(f) for f in cursor.fetchall()]
        except sqlite3.Error as e:
            registrarError(f"sqlite3.Error al listar órdenes: {e}")
            return []
        finally:
            if conexion:
                conexion.close()

    def buscarOrdenes(self, criterio):
        """Busca órdenes por folio o por nombre del cliente."""
        texto = str(criterio).strip() if criterio is not None else ""
        if not texto:
            raise ValueError("Escribe un folio o nombre de cliente para buscar.")

        conexion = None
        try:
            conexion = self._abrirConexion()
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
                    f"No se encontraron órdenes con '{texto}'."
                )
            return [self._filaAOrden(f) for f in filas]
        except RegistroNoEncontradoError as e:
            registrarError(f"RegistroNoEncontradoError: {e}")
            raise
        except sqlite3.Error as e:
            registrarError(f"sqlite3.Error al buscar órdenes: {e}")
            raise
        finally:
            if conexion:
                conexion.close()

    def modificarOrden(self, orden):
        """Modifica los datos de una orden existente identificada por su folio."""
        esMovil = isinstance(orden.dispositivo, DispositivoMovil)
        tipoDisp = "DispositivoMovil" if esMovil else "Computadora"
        ramValor = None if esMovil else orden.dispositivo.ram
        imeiValor = orden.dispositivo.imei if esMovil else None

        conexion = None
        try:
            conexion = self._abrirConexion()
            cursor = conexion.cursor()
            cursor.execute(
                """
                UPDATE ordenes SET
                    clienteNombre = ?, clienteTelefono = ?, clienteDireccion = ?,
                    tecnicoNombre = ?, tecnicoTelefono = ?, tecnicoEspecialidad = ?,
                    tipoDispositivo = ?, marca = ?, modelo = ?, fallaReportada = ?,
                    ram = ?, imei = ?, costoComponentes = ?, costoManoObra = ?,
                    costoTotal = ?, estado = ?
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
                    orden.costoComponentes,
                    orden.costoManoObra,
                    orden.costoTotal,
                    orden.estado,
                    orden.folio,
                ),
            )
            if cursor.rowcount == 0:
                raise RegistroNoEncontradoError(
                    f"No existe una orden con el folio '{orden.folio}'."
                )
            conexion.commit()
            self._sincronizarTxt()
        except RegistroNoEncontradoError as e:
            registrarError(f"RegistroNoEncontradoError: {e}")
            raise
        except sqlite3.Error as e:
            registrarError(f"sqlite3.Error al modificar orden: {e}")
            raise
        finally:
            if conexion:
                conexion.close()

    def eliminarOrden(self, folio):
        """Elimina una orden de la base de datos por su folio."""
        folioLimpio = str(folio).strip().upper() if folio is not None else ""
        if not folioLimpio:
            raise ValueError("Indica el folio de la orden que deseas eliminar.")

        conexion = None
        try:
            conexion = self._abrirConexion()
            cursor = conexion.cursor()
            cursor.execute("DELETE FROM ordenes WHERE folio = ?", (folioLimpio,))
            if cursor.rowcount == 0:
                raise RegistroNoEncontradoError(
                    f"No existe una orden con el folio '{folioLimpio}'."
                )
            conexion.commit()
            self._sincronizarTxt()
        except RegistroNoEncontradoError as e:
            registrarError(f"RegistroNoEncontradoError: {e}")
            raise
        except sqlite3.Error as e:
            registrarError(f"sqlite3.Error al eliminar orden: {e}")
            raise
        finally:
            if conexion:
                conexion.close()
