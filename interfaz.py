"""Interfaz gráfica con Tkinter para el Sistema de Gestión de Reparaciones Tecnológicas."""

import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

from dispositivo import Computadora, DispositivoMovil
from excepciones import (
    RegistroDuplicadoError,
    RegistroNoEncontradoError,
    ValorFueraDeRangoError,
)
from orden_servicio import OrdenServicio
from persistencia import GestorBaseDatos, leerLog, registrarError
from persona import Cliente, Tecnico


class InterfazTaller(tk.Tk):
    """Ventana principal de la aplicación de escritorio del taller."""

    def __init__(self, gestorBd=None):
        super().__init__()
        self._gestorBd = gestorBd if gestorBd is not None else GestorBaseDatos()
        self._mapaClientes = {}
        self._mapaTecnicos = {}
        self._idClienteActual = None
        self._idTecnicoActual = None
        self._imagenLogo = None

        self.title("SGRT - Sistema de Gestión de Reparaciones Tecnológicas")
        self.geometry("1080x680")
        self.minsize(950, 600)

        self._crearEncabezado()
        self._crearPestanas()
        self._refrescarTodo()

    def _crearEncabezado(self):
        """Construye la barra superior con el logo y el título del sistema."""
        frameTop = tk.Frame(self, bg="#1F2937", padx=15, pady=10)
        frameTop.pack(fill="x")

        rutaLogo = Path(__file__).resolve().parent / "logo_sgrt.png"
        try:
            self._imagenLogo = tk.PhotoImage(file=str(rutaLogo))
            lblLogo = tk.Label(frameTop, image=self._imagenLogo, bg="#1F2937")
            lblLogo.pack(side="left", padx=(0, 12))
        except (tk.TclError, FileNotFoundError) as e:
            registrarError(f"Error al cargar logo '{rutaLogo.name}': {e}")
            lblLogo = tk.Label(
                frameTop,
                text="SGRT",
                fg="white",
                bg="#2563EB",
                font=("Arial", 14, "bold"),
                padx=12,
                pady=10,
            )
            lblLogo.pack(side="left", padx=(0, 12))

        frameTexto = tk.Frame(frameTop, bg="#1F2937")
        frameTexto.pack(side="left", fill="y")

        tk.Label(
            frameTexto,
            text="Sistema de Gestión de Reparaciones Tecnológicas",
            fg="white",
            bg="#1F2937",
            font=("Arial", 15, "bold"),
        ).pack(anchor="w")

        tk.Label(
            frameTexto,
            text="Control de Órdenes de Servicio, Clientes, Técnicos y Bitácora",
            fg="#D1D5DB",
            bg="#1F2937",
            font=("Arial", 10),
        ).pack(anchor="w", pady=(2, 0))

        self._varResumen = tk.StringVar(value="Órdenes: 0 | Total acumulado: $0.00")
        tk.Label(
            frameTop,
            textvariable=self._varResumen,
            fg="white",
            bg="#2563EB",
            font=("Arial", 10, "bold"),
            padx=12,
            pady=8,
        ).pack(side="right")

    def _crearPestanas(self):
        """Crea las pestañas principales de la interfaz."""
        self._notebook = ttk.Notebook(self)
        self._notebook.pack(fill="both", expand=True, padx=12, pady=10)

        self._tabOrdenes = tk.Frame(self._notebook)
        self._tabClientes = tk.Frame(self._notebook)
        self._tabTecnicos = tk.Frame(self._notebook)
        self._tabLog = tk.Frame(self._notebook)

        self._notebook.add(self._tabOrdenes, text="Órdenes de Servicio")
        self._notebook.add(self._tabClientes, text="Clientes")
        self._notebook.add(self._tabTecnicos, text="Técnicos")
        self._notebook.add(self._tabLog, text="Bitácora de Errores")

        self._armarTabOrdenes()
        self._armarTabClientes()
        self._armarTabTecnicos()
        self._armarTabLog()

    # --- PESTAÑA ÓRDENES ---
    def _armarTabOrdenes(self):
        """Arma el formulario y tabla de órdenes de servicio."""
        frameIzq = tk.LabelFrame(self._tabOrdenes, text="Datos de la Orden", padx=10, pady=10)
        frameIzq.pack(side="left", fill="y", padx=(10, 6), pady=10)

        self._varFolio = tk.StringVar()
        self._varCliente = tk.StringVar()
        self._varTecnico = tk.StringVar()
        self._varTipoEquipo = tk.StringVar(value="Computadora")
        self._varMarca = tk.StringVar()
        self._varModelo = tk.StringVar()
        self._varFalla = tk.StringVar()
        self._varDatoExtra = tk.StringVar()
        self._varComponentes = tk.StringVar(value="0.00")
        self._varManoObra = tk.StringVar(value="0.00")
        self._varEstado = tk.StringVar(value="En diagnóstico")
        self._varTotalTexto = tk.StringVar(value="Costo Total: $0.00")

        tk.Label(frameIzq, text="Folio:").grid(row=0, column=0, sticky="w", pady=3)
        tk.Entry(frameIzq, textvariable=self._varFolio, width=26).grid(row=0, column=1, pady=3, padx=5)

        tk.Label(frameIzq, text="Cliente:").grid(row=1, column=0, sticky="w", pady=3)
        self._comboCliente = ttk.Combobox(frameIzq, textvariable=self._varCliente, state="readonly", width=24)
        self._comboCliente.grid(row=1, column=1, pady=3, padx=5)

        tk.Label(frameIzq, text="Técnico:").grid(row=2, column=0, sticky="w", pady=3)
        self._comboTecnico = ttk.Combobox(frameIzq, textvariable=self._varTecnico, state="readonly", width=24)
        self._comboTecnico.grid(row=2, column=1, pady=3, padx=5)

        tk.Label(frameIzq, text="Tipo de equipo:").grid(row=3, column=0, sticky="w", pady=3)
        self._comboTipo = ttk.Combobox(
            frameIzq,
            textvariable=self._varTipoEquipo,
            values=("Computadora", "DispositivoMovil"),
            state="readonly",
            width=24,
        )
        self._comboTipo.grid(row=3, column=1, pady=3, padx=5)
        self._comboTipo.bind("<<ComboboxSelected>>", self._cambiarEtiquetaEquipo)

        tk.Label(frameIzq, text="Marca:").grid(row=4, column=0, sticky="w", pady=3)
        tk.Entry(frameIzq, textvariable=self._varMarca, width=26).grid(row=4, column=1, pady=3, padx=5)

        tk.Label(frameIzq, text="Modelo:").grid(row=5, column=0, sticky="w", pady=3)
        tk.Entry(frameIzq, textvariable=self._varModelo, width=26).grid(row=5, column=1, pady=3, padx=5)

        tk.Label(frameIzq, text="Falla reportada:").grid(row=6, column=0, sticky="w", pady=3)
        tk.Entry(frameIzq, textvariable=self._varFalla, width=26).grid(row=6, column=1, pady=3, padx=5)

        self._lblDatoExtra = tk.Label(frameIzq, text="RAM (GB):")
        self._lblDatoExtra.grid(row=7, column=0, sticky="w", pady=3)
        tk.Entry(frameIzq, textvariable=self._varDatoExtra, width=26).grid(row=7, column=1, pady=3, padx=5)

        tk.Label(frameIzq, text="Refacciones ($):").grid(row=8, column=0, sticky="w", pady=3)
        tk.Entry(frameIzq, textvariable=self._varComponentes, width=26).grid(row=8, column=1, pady=3, padx=5)

        tk.Label(frameIzq, text="Mano de obra ($):").grid(row=9, column=0, sticky="w", pady=3)
        tk.Entry(frameIzq, textvariable=self._varManoObra, width=26).grid(row=9, column=1, pady=3, padx=5)

        tk.Label(frameIzq, text="Estado:").grid(row=10, column=0, sticky="w", pady=3)
        ttk.Combobox(
            frameIzq,
            textvariable=self._varEstado,
            values=OrdenServicio.ESTADOS_VALIDOS,
            state="readonly",
            width=24,
        ).grid(row=10, column=1, pady=3, padx=5)

        tk.Label(
            frameIzq,
            textvariable=self._varTotalTexto,
            font=("Arial", 10, "bold"),
            fg="#065F46",
            bg="#D1FAE5",
            pady=5,
        ).grid(row=11, column=0, columnspan=2, sticky="ew", pady=8)

        frameBtns = tk.Frame(frameIzq)
        frameBtns.grid(row=12, column=0, columnspan=2, sticky="ew")
        frameBtns.columnconfigure(0, weight=1)
        frameBtns.columnconfigure(1, weight=1)

        tk.Button(frameBtns, text="Calcular Costo", command=self._calcularCostoVista).grid(
            row=0, column=0, sticky="ew", padx=2, pady=2
        )
        tk.Button(frameBtns, text="Generar Ticket", command=self._verTicketOrden).grid(
            row=0, column=1, sticky="ew", padx=2, pady=2
        )
        tk.Button(frameBtns, text="Registrar", command=self._registrarOrden).grid(
            row=1, column=0, sticky="ew", padx=2, pady=2
        )
        tk.Button(frameBtns, text="Modificar", command=self._modificarOrden).grid(
            row=1, column=1, sticky="ew", padx=2, pady=2
        )
        tk.Button(frameBtns, text="Eliminar", command=self._eliminarOrden).grid(
            row=2, column=0, sticky="ew", padx=2, pady=2
        )
        tk.Button(frameBtns, text="Limpiar", command=self._limpiarOrden).grid(
            row=2, column=1, sticky="ew", padx=2, pady=2
        )

        # Panel derecho
        frameDer = tk.Frame(self._tabOrdenes)
        frameDer.pack(side="right", fill="both", expand=True, padx=(6, 10), pady=10)

        frameBuscar = tk.LabelFrame(frameDer, text="Consultar Órdenes", padx=8, pady=8)
        frameBuscar.pack(fill="x", pady=(0, 8))

        self._varBuscar = tk.StringVar()
        tk.Label(frameBuscar, text="Folio o cliente:").pack(side="left")
        tk.Entry(frameBuscar, textvariable=self._varBuscar, width=28).pack(
            side="left", padx=6, fill="x", expand=True
        )
        tk.Button(frameBuscar, text="Buscar", command=self._buscarOrdenes).pack(side="left", padx=3)
        tk.Button(frameBuscar, text="Ver Todas", command=self._cargarTablaOrdenes).pack(side="left", padx=3)

        frameTabla = tk.LabelFrame(frameDer, text="Órdenes Registradas", padx=6, pady=6)
        frameTabla.pack(fill="both", expand=True, pady=(0, 8))

        cols = ("folio", "cliente", "tecnico", "equipo", "estado", "total")
        self._treeOrdenes = ttk.Treeview(frameTabla, columns=cols, show="headings", selectmode="browse")
        self._treeOrdenes.heading("folio", text="Folio")
        self._treeOrdenes.heading("cliente", text="Cliente")
        self._treeOrdenes.heading("tecnico", text="Técnico")
        self._treeOrdenes.heading("equipo", text="Equipo")
        self._treeOrdenes.heading("estado", text="Estado")
        self._treeOrdenes.heading("total", text="Total ($)")

        self._treeOrdenes.column("folio", width=80, anchor="center")
        self._treeOrdenes.column("cliente", width=140)
        self._treeOrdenes.column("tecnico", width=130)
        self._treeOrdenes.column("equipo", width=155)
        self._treeOrdenes.column("estado", width=105, anchor="center")
        self._treeOrdenes.column("total", width=85, anchor="center")

        scroll = ttk.Scrollbar(frameTabla, orient="vertical", command=self._treeOrdenes.yview)
        self._treeOrdenes.configure(yscrollcommand=scroll.set)
        self._treeOrdenes.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        self._treeOrdenes.bind("<<TreeviewSelect>>", self._alSeleccionarOrden)

        frameResumen = tk.LabelFrame(frameDer, text="Resumen / Ticket de la Orden", padx=6, pady=6)
        frameResumen.pack(fill="x")

        self._txtResumen = tk.Text(frameResumen, height=7, font=("Courier", 9), state="disabled")
        self._txtResumen.pack(fill="x")

    def _cambiarEtiquetaEquipo(self, _evento=None):
        if self._varTipoEquipo.get() == "DispositivoMovil":
            self._lblDatoExtra.config(text="IMEI (15 dígitos):")
        else:
            self._lblDatoExtra.config(text="RAM (GB):")

    def _crearOrdenDesdeFormulario(self):
        folio = self._varFolio.get().strip()
        if not folio:
            raise ValueError("El folio no puede estar vacío.")

        nombreCliente = self._varCliente.get().strip()
        if nombreCliente not in self._mapaClientes:
            raise ValueError("Selecciona un cliente válido.")
        cliente = self._mapaClientes[nombreCliente]

        nombreTecnico = self._varTecnico.get().strip()
        if nombreTecnico not in self._mapaTecnicos:
            raise ValueError("Selecciona un técnico válido.")
        tecnico = self._mapaTecnicos[nombreTecnico]

        marca = self._varMarca.get().strip()
        modelo = self._varModelo.get().strip()
        falla = self._varFalla.get().strip()
        extra = self._varDatoExtra.get().strip()

        if self._varTipoEquipo.get() == "DispositivoMovil":
            dispositivo = DispositivoMovil(marca, modelo, falla, extra)
        else:
            dispositivo = Computadora(marca, modelo, falla, extra)

        orden = OrdenServicio(
            folio,
            cliente,
            tecnico,
            dispositivo,
            costoComponentes=self._varComponentes.get(),
            costoManoObra=self._varManoObra.get(),
            estado=self._varEstado.get(),
        )
        orden.calcularCosto()
        return orden

    def _calcularCostoVista(self):
        try:
            comp = float(self._varComponentes.get())
            mano = float(self._varManoObra.get())
            if comp < 0 or mano < 0:
                raise ValorFueraDeRangoError("Los costos no pueden ser negativos.")
            total = comp + mano
            self._varTotalTexto.set(f"Costo Total: ${total:.2f}")
        except (ValueError, ValorFueraDeRangoError) as e:
            registrarError(f"{type(e).__name__} al calcular costo: {e}")
            self._cargarLog()
            messagebox.showerror("Error en cálculo", str(e))

    def _verTicketOrden(self):
        try:
            orden = self._crearOrdenDesdeFormulario()
            self._mostrarTextoResumen(orden.generarResumen())
        except (ValueError, TypeError, ValorFueraDeRangoError) as e:
            registrarError(f"{type(e).__name__} al generar ticket: {e}")
            self._cargarLog()
            messagebox.showwarning("Datos incompletos", str(e))

    def _registrarOrden(self):
        try:
            orden = self._crearOrdenDesdeFormulario()
            self._gestorBd.registrarOrden(orden)
            self._cargarTablaOrdenes()
            self._varTotalTexto.set(f"Costo Total: ${orden.costoTotal:.2f}")
            self._mostrarTextoResumen(orden.generarResumen())
            messagebox.showinfo("Éxito", f"Orden '{orden.folio}' registrada correctamente.")
        except RegistroDuplicadoError as e:
            self._cargarLog()
            messagebox.showerror("Folio duplicado", str(e))
        except (ValueError, TypeError, ValorFueraDeRangoError) as e:
            registrarError(f"{type(e).__name__} al registrar orden: {e}")
            self._cargarLog()
            messagebox.showwarning("Error de validación", str(e))

    def _modificarOrden(self):
        try:
            orden = self._crearOrdenDesdeFormulario()
            self._gestorBd.modificarOrden(orden)
            self._cargarTablaOrdenes()
            self._varTotalTexto.set(f"Costo Total: ${orden.costoTotal:.2f}")
            self._mostrarTextoResumen(orden.generarResumen())
            messagebox.showinfo("Éxito", f"Orden '{orden.folio}' actualizada.")
        except RegistroNoEncontradoError as e:
            self._cargarLog()
            messagebox.showerror("No encontrado", str(e))
        except (ValueError, TypeError, ValorFueraDeRangoError) as e:
            registrarError(f"{type(e).__name__} al modificar orden: {e}")
            self._cargarLog()
            messagebox.showwarning("Error de validación", str(e))

    def _eliminarOrden(self):
        folio = self._varFolio.get().strip().upper()
        if not folio:
            msg = "Selecciona una orden de la tabla o escribe su folio."
            registrarError(f"ValueError al eliminar orden: {msg}")
            self._cargarLog()
            messagebox.showwarning("Campo vacío", msg)
            return

        if not messagebox.askyesno("Confirmar", f"¿Eliminar la orden '{folio}'?"):
            return

        try:
            self._gestorBd.eliminarOrden(folio)
            self._limpiarOrden()
            self._cargarTablaOrdenes()
            messagebox.showinfo("Eliminada", f"La orden '{folio}' fue eliminada.")
        except RegistroNoEncontradoError as e:
            self._cargarLog()
            messagebox.showerror("No encontrado", str(e))

    def _buscarOrdenes(self):
        try:
            ordenes = self._gestorBd.buscarOrdenes(self._varBuscar.get())
            self._llenarTablaOrdenes(ordenes)
            if ordenes:
                self._mostrarTextoResumen(ordenes[0].generarResumen())
        except RegistroNoEncontradoError as e:
            self._cargarLog()
            messagebox.showerror("Sin resultados", str(e))
        except ValueError as e:
            registrarError(f"ValueError al buscar orden: {e}")
            self._cargarLog()
            messagebox.showwarning("Campo vacío", str(e))

    def _alSeleccionarOrden(self, _evento=None):
        sel = self._treeOrdenes.selection()
        if not sel:
            return
        folio = self._treeOrdenes.item(sel[0], "values")[0]
        try:
            lista = self._gestorBd.buscarOrdenes(folio)
            orden = next((o for o in lista if o.folio == folio), lista[0])
        except (RegistroNoEncontradoError, ValueError):
            return

        self._varFolio.set(orden.folio)
        if orden.cliente.nombre in self._mapaClientes:
            self._varCliente.set(orden.cliente.nombre)
        if orden.tecnico.nombre in self._mapaTecnicos:
            self._varTecnico.set(orden.tecnico.nombre)

        if isinstance(orden.dispositivo, DispositivoMovil):
            self._varTipoEquipo.set("DispositivoMovil")
            self._varDatoExtra.set(orden.dispositivo.imei)
        else:
            self._varTipoEquipo.set("Computadora")
            self._varDatoExtra.set(str(orden.dispositivo.ram))
        self._cambiarEtiquetaEquipo()

        self._varMarca.set(orden.dispositivo.marca)
        self._varModelo.set(orden.dispositivo.modelo)
        self._varFalla.set(orden.dispositivo.fallaReportada)
        self._varComponentes.set(f"{orden.costoComponentes:.2f}")
        self._varManoObra.set(f"{orden.costoManoObra:.2f}")
        self._varEstado.set(orden.estado)
        self._varTotalTexto.set(f"Costo Total: ${orden.costoTotal:.2f}")
        self._mostrarTextoResumen(orden.generarResumen())

    def _mostrarTextoResumen(self, texto):
        self._txtResumen.config(state="normal")
        self._txtResumen.delete("1.0", "end")
        self._txtResumen.insert("1.0", texto)
        self._txtResumen.config(state="disabled")

    def _limpiarOrden(self):
        self._varFolio.set("")
        self._varMarca.set("")
        self._varModelo.set("")
        self._varFalla.set("")
        self._varDatoExtra.set("")
        self._varComponentes.set("0.00")
        self._varManoObra.set("0.00")
        self._varEstado.set("En diagnóstico")
        self._varTotalTexto.set("Costo Total: $0.00")
        self._mostrarTextoResumen("")
        for item in self._treeOrdenes.selection():
            self._treeOrdenes.selection_remove(item)

    def _llenarTablaOrdenes(self, ordenes):
        for item in self._treeOrdenes.get_children():
            self._treeOrdenes.delete(item)

        suma = 0.0
        for o in ordenes:
            suma += o.costoTotal
            equipoTxt = f"{o.dispositivo.marca} {o.dispositivo.modelo}"
            self._treeOrdenes.insert(
                "",
                "end",
                values=(
                    o.folio,
                    o.cliente.nombre,
                    o.tecnico.nombre,
                    equipoTxt,
                    o.estado,
                    f"${o.costoTotal:.2f}",
                ),
            )
        self._varResumen.set(f"Órdenes: {len(ordenes)} | Total acumulado: ${suma:.2f}")

    def _cargarTablaOrdenes(self):
        self._varBuscar.set("")
        self._llenarTablaOrdenes(self._gestorBd.obtenerOrdenes())

    # --- PESTAÑA CLIENTES ---
    def _armarTabClientes(self):
        """Arma el formulario y tabla del catálogo de clientes."""
        frameIzq = tk.LabelFrame(self._tabClientes, text="Datos del Cliente", padx=12, pady=12)
        frameIzq.pack(side="left", fill="y", padx=(10, 6), pady=10)

        self._varNomCliente = tk.StringVar()
        self._varTelCliente = tk.StringVar()
        self._varDirCliente = tk.StringVar()

        tk.Label(frameIzq, text="Nombre:").grid(row=0, column=0, sticky="w", pady=5)
        tk.Entry(frameIzq, textvariable=self._varNomCliente, width=28).grid(row=0, column=1, pady=5, padx=5)

        tk.Label(frameIzq, text="Teléfono:").grid(row=1, column=0, sticky="w", pady=5)
        tk.Entry(frameIzq, textvariable=self._varTelCliente, width=28).grid(row=1, column=1, pady=5, padx=5)

        tk.Label(frameIzq, text="Dirección:").grid(row=2, column=0, sticky="w", pady=5)
        tk.Entry(frameIzq, textvariable=self._varDirCliente, width=28).grid(row=2, column=1, pady=5, padx=5)

        frameBtns = tk.Frame(frameIzq)
        frameBtns.grid(row=3, column=0, columnspan=2, sticky="ew", pady=10)
        frameBtns.columnconfigure(0, weight=1)
        frameBtns.columnconfigure(1, weight=1)

        tk.Button(frameBtns, text="Registrar", command=self._registrarCliente).grid(
            row=0, column=0, sticky="ew", padx=2, pady=2
        )
        tk.Button(frameBtns, text="Modificar", command=self._modificarCliente).grid(
            row=0, column=1, sticky="ew", padx=2, pady=2
        )
        tk.Button(frameBtns, text="Eliminar", command=self._eliminarCliente).grid(
            row=1, column=0, sticky="ew", padx=2, pady=2
        )
        tk.Button(frameBtns, text="Limpiar", command=self._limpiarCliente).grid(
            row=1, column=1, sticky="ew", padx=2, pady=2
        )

        frameDer = tk.LabelFrame(self._tabClientes, text="Catálogo de Clientes (SQLite)", padx=8, pady=8)
        frameDer.pack(side="right", fill="both", expand=True, padx=(6, 10), pady=10)

        self._treeClientes = ttk.Treeview(
            frameDer, columns=("id", "nombre", "telefono", "direccion"), show="headings", selectmode="browse"
        )
        self._treeClientes.heading("id", text="ID")
        self._treeClientes.heading("nombre", text="Nombre")
        self._treeClientes.heading("telefono", text="Teléfono")
        self._treeClientes.heading("direccion", text="Dirección")
        self._treeClientes.column("id", width=50, anchor="center")
        self._treeClientes.column("nombre", width=180)
        self._treeClientes.column("telefono", width=120, anchor="center")
        self._treeClientes.column("direccion", width=220)

        scroll = ttk.Scrollbar(frameDer, orient="vertical", command=self._treeClientes.yview)
        self._treeClientes.configure(yscrollcommand=scroll.set)
        self._treeClientes.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        self._treeClientes.bind("<<TreeviewSelect>>", self._alSeleccionarCliente)

    def _registrarCliente(self):
        try:
            c = Cliente(self._varNomCliente.get(), self._varTelCliente.get(), self._varDirCliente.get())
            self._gestorBd.registrarCliente(c)
            self._cargarClientes()
            self._limpiarCliente()
            messagebox.showinfo("Éxito", f"Cliente '{c.nombre}' guardado.")
        except RegistroDuplicadoError as e:
            self._cargarLog()
            messagebox.showerror("Duplicado", str(e))
        except (ValueError, ValorFueraDeRangoError) as e:
            registrarError(f"{type(e).__name__} al registrar cliente: {e}")
            self._cargarLog()
            messagebox.showwarning("Validación", str(e))

    def _modificarCliente(self):
        if self._idClienteActual is None:
            msg = "Selecciona un cliente de la tabla para modificarlo."
            registrarError(f"RegistroNoEncontradoError al modificar cliente: {msg}")
            self._cargarLog()
            messagebox.showwarning("Aviso", msg)
            return

        try:
            c = Cliente(self._varNomCliente.get(), self._varTelCliente.get(), self._varDirCliente.get())
            self._gestorBd.modificarCliente(self._idClienteActual, c)
            self._cargarClientes()
            self._limpiarCliente()
            messagebox.showinfo("Éxito", "Cliente actualizado.")
        except (RegistroDuplicadoError, RegistroNoEncontradoError) as e:
            self._cargarLog()
            messagebox.showerror("Error", str(e))
        except (ValueError, ValorFueraDeRangoError) as e:
            registrarError(f"{type(e).__name__} al modificar cliente: {e}")
            self._cargarLog()
            messagebox.showwarning("Validación", str(e))

    def _eliminarCliente(self):
        if self._idClienteActual is None:
            msg = "Selecciona un cliente de la tabla para eliminarlo."
            registrarError(f"RegistroNoEncontradoError al eliminar cliente: {msg}")
            self._cargarLog()
            messagebox.showwarning("Aviso", msg)
            return

        if not messagebox.askyesno("Confirmar", "¿Eliminar el cliente seleccionado?"):
            return

        try:
            self._gestorBd.eliminarCliente(self._idClienteActual)
            self._cargarClientes()
            self._limpiarCliente()
            messagebox.showinfo("Eliminado", "Cliente eliminado.")
        except RegistroNoEncontradoError as e:
            self._cargarLog()
            messagebox.showerror("Error", str(e))

    def _alSeleccionarCliente(self, _evento=None):
        sel = self._treeClientes.selection()
        if not sel:
            return
        vals = self._treeClientes.item(sel[0], "values")
        self._idClienteActual = int(vals[0])
        self._varNomCliente.set(vals[1])
        self._varTelCliente.set(vals[2])
        self._varDirCliente.set(vals[3])

    def _limpiarCliente(self):
        self._idClienteActual = None
        self._varNomCliente.set("")
        self._varTelCliente.set("")
        self._varDirCliente.set("")
        for item in self._treeClientes.selection():
            self._treeClientes.selection_remove(item)

    def _cargarClientes(self):
        for item in self._treeClientes.get_children():
            self._treeClientes.delete(item)
        self._mapaClientes.clear()

        nombres = []
        for idC, cliente in self._gestorBd.obtenerClientes():
            self._treeClientes.insert("", "end", values=(idC, cliente.nombre, cliente.telefono, cliente.direccion))
            self._mapaClientes[cliente.nombre] = cliente
            nombres.append(cliente.nombre)

        self._comboCliente["values"] = nombres
        if nombres and self._varCliente.get() not in self._mapaClientes:
            self._varCliente.set(nombres[0])

    # --- PESTAÑA TÉCNICOS ---
    def _armarTabTecnicos(self):
        """Arma el formulario y tabla del catálogo de técnicos."""
        frameIzq = tk.LabelFrame(self._tabTecnicos, text="Datos del Técnico", padx=12, pady=12)
        frameIzq.pack(side="left", fill="y", padx=(10, 6), pady=10)

        self._varNomTecnico = tk.StringVar()
        self._varTelTecnico = tk.StringVar()
        self._varEspTecnico = tk.StringVar(value="Microelectrónica")

        tk.Label(frameIzq, text="Nombre:").grid(row=0, column=0, sticky="w", pady=5)
        tk.Entry(frameIzq, textvariable=self._varNomTecnico, width=28).grid(row=0, column=1, pady=5, padx=5)

        tk.Label(frameIzq, text="Teléfono:").grid(row=1, column=0, sticky="w", pady=5)
        tk.Entry(frameIzq, textvariable=self._varTelTecnico, width=28).grid(row=1, column=1, pady=5, padx=5)

        tk.Label(frameIzq, text="Especialidad:").grid(row=2, column=0, sticky="w", pady=5)
        ttk.Combobox(
            frameIzq,
            textvariable=self._varEspTecnico,
            values=("Microelectrónica", "Dispositivos Móviles", "Software y Sistemas", "Hardware"),
            width=26,
        ).grid(row=2, column=1, pady=5, padx=5)

        frameBtns = tk.Frame(frameIzq)
        frameBtns.grid(row=3, column=0, columnspan=2, sticky="ew", pady=10)
        frameBtns.columnconfigure(0, weight=1)
        frameBtns.columnconfigure(1, weight=1)

        tk.Button(frameBtns, text="Registrar", command=self._registrarTecnico).grid(
            row=0, column=0, sticky="ew", padx=2, pady=2
        )
        tk.Button(frameBtns, text="Modificar", command=self._modificarTecnico).grid(
            row=0, column=1, sticky="ew", padx=2, pady=2
        )
        tk.Button(frameBtns, text="Eliminar", command=self._eliminarTecnico).grid(
            row=1, column=0, sticky="ew", padx=2, pady=2
        )
        tk.Button(frameBtns, text="Limpiar", command=self._limpiarTecnico).grid(
            row=1, column=1, sticky="ew", padx=2, pady=2
        )

        frameDer = tk.LabelFrame(self._tabTecnicos, text="Catálogo de Técnicos (SQLite)", padx=8, pady=8)
        frameDer.pack(side="right", fill="both", expand=True, padx=(6, 10), pady=10)

        self._treeTecnicos = ttk.Treeview(
            frameDer, columns=("id", "nombre", "telefono", "especialidad"), show="headings", selectmode="browse"
        )
        self._treeTecnicos.heading("id", text="ID")
        self._treeTecnicos.heading("nombre", text="Nombre")
        self._treeTecnicos.heading("telefono", text="Teléfono")
        self._treeTecnicos.heading("especialidad", text="Especialidad")
        self._treeTecnicos.column("id", width=50, anchor="center")
        self._treeTecnicos.column("nombre", width=180)
        self._treeTecnicos.column("telefono", width=120, anchor="center")
        self._treeTecnicos.column("especialidad", width=220)

        scroll = ttk.Scrollbar(frameDer, orient="vertical", command=self._treeTecnicos.yview)
        self._treeTecnicos.configure(yscrollcommand=scroll.set)
        self._treeTecnicos.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        self._treeTecnicos.bind("<<TreeviewSelect>>", self._alSeleccionarTecnico)

    def _registrarTecnico(self):
        try:
            t = Tecnico(self._varNomTecnico.get(), self._varTelTecnico.get(), self._varEspTecnico.get())
            self._gestorBd.registrarTecnico(t)
            self._cargarTecnicos()
            self._limpiarTecnico()
            messagebox.showinfo("Éxito", f"Técnico '{t.nombre}' guardado.")
        except RegistroDuplicadoError as e:
            self._cargarLog()
            messagebox.showerror("Duplicado", str(e))
        except (ValueError, ValorFueraDeRangoError) as e:
            registrarError(f"{type(e).__name__} al registrar técnico: {e}")
            self._cargarLog()
            messagebox.showwarning("Validación", str(e))

    def _modificarTecnico(self):
        if self._idTecnicoActual is None:
            msg = "Selecciona un técnico de la tabla para modificarlo."
            registrarError(f"RegistroNoEncontradoError al modificar técnico: {msg}")
            self._cargarLog()
            messagebox.showwarning("Aviso", msg)
            return

        try:
            t = Tecnico(self._varNomTecnico.get(), self._varTelTecnico.get(), self._varEspTecnico.get())
            self._gestorBd.modificarTecnico(self._idTecnicoActual, t)
            self._cargarTecnicos()
            self._limpiarTecnico()
            messagebox.showinfo("Éxito", "Técnico actualizado.")
        except (RegistroDuplicadoError, RegistroNoEncontradoError) as e:
            self._cargarLog()
            messagebox.showerror("Error", str(e))
        except (ValueError, ValorFueraDeRangoError) as e:
            registrarError(f"{type(e).__name__} al modificar técnico: {e}")
            self._cargarLog()
            messagebox.showwarning("Validación", str(e))

    def _eliminarTecnico(self):
        if self._idTecnicoActual is None:
            msg = "Selecciona un técnico de la tabla para eliminarlo."
            registrarError(f"RegistroNoEncontradoError al eliminar técnico: {msg}")
            self._cargarLog()
            messagebox.showwarning("Aviso", msg)
            return

        if not messagebox.askyesno("Confirmar", "¿Eliminar el técnico seleccionado?"):
            return

        try:
            self._gestorBd.eliminarTecnico(self._idTecnicoActual)
            self._cargarTecnicos()
            self._limpiarTecnico()
            messagebox.showinfo("Eliminado", "Técnico eliminado.")
        except RegistroNoEncontradoError as e:
            self._cargarLog()
            messagebox.showerror("Error", str(e))

    def _alSeleccionarTecnico(self, _evento=None):
        sel = self._treeTecnicos.selection()
        if not sel:
            return
        vals = self._treeTecnicos.item(sel[0], "values")
        self._idTecnicoActual = int(vals[0])
        self._varNomTecnico.set(vals[1])
        self._varTelTecnico.set(vals[2])
        self._varEspTecnico.set(vals[3])

    def _limpiarTecnico(self):
        self._idTecnicoActual = None
        self._varNomTecnico.set("")
        self._varTelTecnico.set("")
        self._varEspTecnico.set("Microelectrónica")
        for item in self._treeTecnicos.selection():
            self._treeTecnicos.selection_remove(item)

    def _cargarTecnicos(self):
        for item in self._treeTecnicos.get_children():
            self._treeTecnicos.delete(item)
        self._mapaTecnicos.clear()

        nombres = []
        for idT, tecnico in self._gestorBd.obtenerTecnicos():
            self._treeTecnicos.insert("", "end", values=(idT, tecnico.nombre, tecnico.telefono, tecnico.especialidad))
            self._mapaTecnicos[tecnico.nombre] = tecnico
            nombres.append(tecnico.nombre)

        self._comboTecnico["values"] = nombres
        if nombres and self._varTecnico.get() not in self._mapaTecnicos:
            self._varTecnico.set(nombres[0])

    # --- PESTAÑA BITÁCORA ---
    def _armarTabLog(self):
        """Arma el visor del archivo log_errores.txt."""
        frameTop = tk.Frame(self._tabLog)
        frameTop.pack(fill="x", padx=10, pady=(10, 5))

        tk.Label(frameTop, text="Registro de errores (log_errores.txt):", font=("Arial", 10, "bold")).pack(
            side="left"
        )
        tk.Button(frameTop, text="Recargar Log", command=self._cargarLog).pack(side="right")

        self._txtLog = tk.Text(self._tabLog, font=("Courier", 10), state="disabled")
        self._txtLog.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def _cargarLog(self):
        contenido = leerLog()
        self._txtLog.config(state="normal")
        self._txtLog.delete("1.0", "end")
        self._txtLog.insert("1.0", contenido if contenido else "Sin errores registrados.")
        self._txtLog.config(state="disabled")

    def _refrescarTodo(self):
        self._cargarClientes()
        self._cargarTecnicos()
        self._cargarTablaOrdenes()
        self._cargarLog()
