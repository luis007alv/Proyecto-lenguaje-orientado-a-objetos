"""Módulo de interfaz gráfica de usuario (GUI) con Tkinter para el SGRT."""

import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

from modelos import (
    Cliente,
    Computadora,
    DispositivoMovil,
    OrdenServicio,
    RegistroDuplicadoError,
    RegistroNoEncontradoError,
    Tecnico,
    ValorFueraDeRangoError,
)
from persistencia import GestorBaseDatos, leerBitacora, registrarError


class AplicacionSGRT(tk.Tk):
    """Ventana principal del Sistema de Gestión de Reparaciones Tecnológicas."""

    ESPECIALIDADES_BASE = (
        "Microelectrónica",
        "Dispositivos Móviles",
        "Software y Sistemas",
        "Redes y Hardware",
        "Pantallas y Baterías",
    )

    def __init__(self, gestorBd=None):
        super().__init__()
        self._gestorBd = gestorBd if gestorBd is not None else GestorBaseDatos()
        self._mapaClientes = {}
        self._mapaTecnicos = {}
        self._idClienteSeleccionado = None
        self._idTecnicoSeleccionado = None
        self._logoImagen = None

        self._configurarVentana()
        self._configurarEstilos()
        self._construirEncabezado()
        self._construirPestanas()
        self._cargarTodo()

    def _configurarVentana(self):
        """Configura propiedades generales de la ventana principal."""
        self.title("SGRT - Sistema de Gestión de Reparaciones Tecnológicas")
        self.geometry("1120x700")
        self.minsize(980, 620)
        self.configure(bg="#F1F5F9")

    def _configurarEstilos(self):
        """Define la paleta de colores y estilos ttk consistentes."""
        estilo = ttk.Style(self)
        estilo.theme_use("clam")

        estilo.configure("TFrame", background="#F1F5F9")
        estilo.configure("Tarjeta.TLabelframe", background="#FFFFFF", foreground="#0F172A")
        estilo.configure(
            "Tarjeta.TLabelframe.Label",
            background="#FFFFFF",
            foreground="#0F766E",
            font=("Helvetica", 10, "bold"),
        )
        estilo.configure(
            "Formulario.TLabel",
            background="#FFFFFF",
            foreground="#1E293B",
            font=("Helvetica", 9, "bold"),
        )
        estilo.configure(
            "Calculo.TLabel",
            background="#ECFDF5",
            foreground="#065F46",
            font=("Helvetica", 10, "bold"),
            padding=6,
        )
        estilo.configure(
            "Primario.TButton",
            background="#0F766E",
            foreground="#FFFFFF",
            font=("Helvetica", 9, "bold"),
            padding=(10, 6),
        )
        estilo.map("Primario.TButton", background=[("active", "#115E59")])

        estilo.configure(
            "Secundario.TButton",
            background="#1E3A8A",
            foreground="#FFFFFF",
            font=("Helvetica", 9, "bold"),
            padding=(10, 6),
        )
        estilo.map("Secundario.TButton", background=[("active", "#1E40AF")])

        estilo.configure(
            "Peligro.TButton",
            background="#B91C1C",
            foreground="#FFFFFF",
            font=("Helvetica", 9, "bold"),
            padding=(10, 6),
        )
        estilo.map("Peligro.TButton", background=[("active", "#991B1B")])

        estilo.configure(
            "Neutro.TButton",
            background="#475569",
            foreground="#FFFFFF",
            font=("Helvetica", 9, "bold"),
            padding=(10, 6),
        )
        estilo.map("Neutro.TButton", background=[("active", "#334155")])

        estilo.configure(
            "Treeview",
            background="#FFFFFF",
            foreground="#0F172A",
            rowheight=26,
            fieldbackground="#FFFFFF",
            font=("Helvetica", 9),
        )
        estilo.configure(
            "Treeview.Heading",
            background="#0F766E",
            foreground="#FFFFFF",
            font=("Helvetica", 9, "bold"),
        )
        estilo.map("Treeview", background=[("selected", "#BAE6FD")], foreground=[("selected", "#0F172A")])

    def _construirEncabezado(self):
        """Crea la barra superior con el logo del negocio, título y resumen de métricas."""
        marcoEncabezado = tk.Frame(self, bg="#0F172A", height=96, padx=18, pady=10)
        marcoEncabezado.pack(fill="x", side="top")
        marcoEncabezado.pack_propagate(False)

        rutaLogo = Path(__file__).resolve().parent / "logo_sgrt.png"
        try:
            self._logoImagen = tk.PhotoImage(file=str(rutaLogo))
            self.iconphoto(False, self._logoImagen)
            etiquetaLogo = tk.Label(
                marcoEncabezado,
                image=self._logoImagen,
                bg="#0F172A",
            )
            etiquetaLogo.pack(side="left", padx=(0, 14))
        except (tk.TclError, FileNotFoundError) as exc:
            registrarError(f"Error al cargar imagen '{rutaLogo.name}': {exc}")
            etiquetaLogo = tk.Label(
                marcoEncabezado,
                text="[SGRT]",
                fg="#FFFFFF",
                bg="#0F766E",
                font=("Helvetica", 14, "bold"),
                padx=12,
                pady=12,
            )
            etiquetaLogo.pack(side="left", padx=(0, 14))

        marcoTitulos = tk.Frame(marcoEncabezado, bg="#0F172A")
        marcoTitulos.pack(side="left", fill="y", expand=True)

        tk.Label(
            marcoTitulos,
            text="Sistema de Gestión de Reparaciones Tecnológicas (SGRT)",
            bg="#0F172A",
            fg="#FFFFFF",
            font=("Helvetica", 15, "bold"),
            anchor="w",
        ).pack(anchor="w", pady=(8, 2))

        tk.Label(
            marcoTitulos,
            text="Administración de órdenes de servicio, clientes, técnicos y bitácora de errores",
            bg="#0F172A",
            fg="#CBD5E1",
            font=("Helvetica", 10),
            anchor="w",
        ).pack(anchor="w")

        self._varResumen = tk.StringVar(value="Órdenes: 0 | Ingresos totales: $0.00")
        tk.Label(
            marcoEncabezado,
            textvariable=self._varResumen,
            bg="#0F766E",
            fg="#FFFFFF",
            font=("Helvetica", 10, "bold"),
            padx=14,
            pady=10,
        ).pack(side="right", pady=12)

    def _construirPestanas(self):
        """Inicializa el Notebook principal con las pestañas del sistema."""
        self._cuaderno = ttk.Notebook(self)
        self._cuaderno.pack(fill="both", expand=True, padx=14, pady=12)

        self._tabOrdenes = ttk.Frame(self._cuaderno)
        self._tabClientes = ttk.Frame(self._cuaderno)
        self._tabTecnicos = ttk.Frame(self._cuaderno)
        self._tabBitacora = ttk.Frame(self._cuaderno)

        self._cuaderno.add(self._tabOrdenes, text="  Órdenes de Servicio  ")
        self._cuaderno.add(self._tabClientes, text="  Catálogo de Clientes  ")
        self._cuaderno.add(self._tabTecnicos, text="  Catálogo de Técnicos  ")
        self._cuaderno.add(self._tabBitacora, text="  Bitácora de Errores  ")

        self._construirTabOrdenes()
        self._construirTabClientes()
        self._construirTabTecnicos()
        self._construirTabBitacora()

    # =========================================================================
    # PESTAÑA 1: ÓRDENES DE SERVICIO
    # =========================================================================
    def _construirTabOrdenes(self):
        """Construye el formulario y listado Treeview de órdenes de servicio."""
        contenedor = ttk.Frame(self._tabOrdenes)
        contenedor.pack(fill="both", expand=True, padx=10, pady=10)

        # Panel izquierdo: Formulario
        marcoForm = ttk.LabelFrame(
            contenedor,
            text=" Datos de la Orden de Servicio ",
            style="Tarjeta.TLabelframe",
            padding=12,
        )
        marcoForm.pack(side="left", fill="y", padx=(0, 10))

        self._varFolio = tk.StringVar()
        self._varClienteOrden = tk.StringVar()
        self._varTecnicoOrden = tk.StringVar()
        self._varTipoDisp = tk.StringVar(value="Computadora")
        self._varMarca = tk.StringVar()
        self._varModelo = tk.StringVar()
        self._varFalla = tk.StringVar()
        self._varEspecifico = tk.StringVar()
        self._varManoObra = tk.StringVar(value="0.00")
        self._varRepuestos = tk.StringVar(value="0.00")
        self._varDescuento = tk.StringVar(value="0.00")
        self._varEstadoOrden = tk.StringVar(value="Recibido")
        self._varCalculoOrden = tk.StringVar(
            value="Subtotal: $0.00 | Total: $0.00 (IVA ref: $0.00)"
        )

        fila = 0
        ttk.Label(marcoForm, text="Folio:", style="Formulario.TLabel").grid(
            row=fila, column=0, sticky="w", pady=4
        )
        ttk.Entry(marcoForm, textvariable=self._varFolio, width=28).grid(
            row=fila, column=1, sticky="ew", pady=4, padx=(8, 0)
        )

        fila += 1
        ttk.Label(marcoForm, text="Cliente:", style="Formulario.TLabel").grid(
            row=fila, column=0, sticky="w", pady=4
        )
        self._comboClientes = ttk.Combobox(
            marcoForm, textvariable=self._varClienteOrden, state="readonly", width=26
        )
        self._comboClientes.grid(row=fila, column=1, sticky="ew", pady=4, padx=(8, 0))

        fila += 1
        ttk.Label(marcoForm, text="Técnico:", style="Formulario.TLabel").grid(
            row=fila, column=0, sticky="w", pady=4
        )
        self._comboTecnicos = ttk.Combobox(
            marcoForm, textvariable=self._varTecnicoOrden, state="readonly", width=26
        )
        self._comboTecnicos.grid(row=fila, column=1, sticky="ew", pady=4, padx=(8, 0))

        fila += 1
        ttk.Label(marcoForm, text="Tipo de Equipo:", style="Formulario.TLabel").grid(
            row=fila, column=0, sticky="w", pady=4
        )
        self._comboTipoDisp = ttk.Combobox(
            marcoForm,
            textvariable=self._varTipoDisp,
            values=("Computadora", "DispositivoMovil"),
            state="readonly",
            width=26,
        )
        self._comboTipoDisp.grid(row=fila, column=1, sticky="ew", pady=4, padx=(8, 0))
        self._comboTipoDisp.bind("<<ComboboxSelected>>", self._actualizarEtiquetaEspecifica)

        fila += 1
        ttk.Label(marcoForm, text="Marca:", style="Formulario.TLabel").grid(
            row=fila, column=0, sticky="w", pady=4
        )
        ttk.Entry(marcoForm, textvariable=self._varMarca, width=28).grid(
            row=fila, column=1, sticky="ew", pady=4, padx=(8, 0)
        )

        fila += 1
        ttk.Label(marcoForm, text="Modelo:", style="Formulario.TLabel").grid(
            row=fila, column=0, sticky="w", pady=4
        )
        ttk.Entry(marcoForm, textvariable=self._varModelo, width=28).grid(
            row=fila, column=1, sticky="ew", pady=4, padx=(8, 0)
        )

        fila += 1
        ttk.Label(marcoForm, text="Falla reportada:", style="Formulario.TLabel").grid(
            row=fila, column=0, sticky="w", pady=4
        )
        ttk.Entry(marcoForm, textvariable=self._varFalla, width=28).grid(
            row=fila, column=1, sticky="ew", pady=4, padx=(8, 0)
        )

        fila += 1
        self._etiquetaEspecifica = ttk.Label(
            marcoForm, text="RAM (GB):", style="Formulario.TLabel"
        )
        self._etiquetaEspecifica.grid(row=fila, column=0, sticky="w", pady=4)
        ttk.Entry(marcoForm, textvariable=self._varEspecifico, width=28).grid(
            row=fila, column=1, sticky="ew", pady=4, padx=(8, 0)
        )

        fila += 1
        ttk.Label(marcoForm, text="Mano de obra ($):", style="Formulario.TLabel").grid(
            row=fila, column=0, sticky="w", pady=4
        )
        ttk.Entry(marcoForm, textvariable=self._varManoObra, width=28).grid(
            row=fila, column=1, sticky="ew", pady=4, padx=(8, 0)
        )

        fila += 1
        ttk.Label(marcoForm, text="Repuestos ($):", style="Formulario.TLabel").grid(
            row=fila, column=0, sticky="w", pady=4
        )
        ttk.Entry(marcoForm, textvariable=self._varRepuestos, width=28).grid(
            row=fila, column=1, sticky="ew", pady=4, padx=(8, 0)
        )

        fila += 1
        ttk.Label(marcoForm, text="Descuento ($):", style="Formulario.TLabel").grid(
            row=fila, column=0, sticky="w", pady=4
        )
        ttk.Entry(marcoForm, textvariable=self._varDescuento, width=28).grid(
            row=fila, column=1, sticky="ew", pady=4, padx=(8, 0)
        )

        fila += 1
        ttk.Label(marcoForm, text="Estado:", style="Formulario.TLabel").grid(
            row=fila, column=0, sticky="w", pady=4
        )
        ttk.Combobox(
            marcoForm,
            textvariable=self._varEstadoOrden,
            values=OrdenServicio.ESTADOS_VALIDOS,
            state="readonly",
            width=26,
        ).grid(row=fila, column=1, sticky="ew", pady=4, padx=(8, 0))

        fila += 1
        ttk.Label(
            marcoForm,
            textvariable=self._varCalculoOrden,
            style="Calculo.TLabel",
            anchor="center",
        ).grid(row=fila, column=0, columnspan=2, sticky="ew", pady=(10, 8))

        fila += 1
        marcoBotones = tk.Frame(marcoForm, bg="#FFFFFF")
        marcoBotones.grid(row=fila, column=0, columnspan=2, sticky="ew", pady=(4, 0))
        marcoBotones.columnconfigure(0, weight=1)
        marcoBotones.columnconfigure(1, weight=1)

        ttk.Button(
            marcoBotones,
            text="Calcular Total",
            style="Secundario.TButton",
            command=self._calcularTotalFormulario,
        ).grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 6))

        ttk.Button(
            marcoBotones,
            text="Registrar Orden",
            style="Primario.TButton",
            command=self._registrarOrden,
        ).grid(row=1, column=0, sticky="ew", padx=(0, 4), pady=2)

        ttk.Button(
            marcoBotones,
            text="Modificar Orden",
            style="Secundario.TButton",
            command=self._modificarOrden,
        ).grid(row=1, column=1, sticky="ew", padx=(4, 0), pady=2)

        ttk.Button(
            marcoBotones,
            text="Eliminar Orden",
            style="Peligro.TButton",
            command=self._eliminarOrden,
        ).grid(row=2, column=0, sticky="ew", padx=(0, 4), pady=2)

        ttk.Button(
            marcoBotones,
            text="Limpiar Campos",
            style="Neutro.TButton",
            command=self._limpiarFormularioOrden,
        ).grid(row=2, column=1, sticky="ew", padx=(4, 0), pady=2)

        # Panel derecho: Búsqueda, Treeview y Detalle __str__
        marcoDerecho = ttk.Frame(contenedor)
        marcoDerecho.pack(side="right", fill="both", expand=True)

        marcoBusqueda = ttk.LabelFrame(
            marcoDerecho,
            text=" Consulta y Filtrado ",
            style="Tarjeta.TLabelframe",
            padding=10,
        )
        marcoBusqueda.pack(fill="x", pady=(0, 10))

        self._varBusquedaOrden = tk.StringVar()
        ttk.Label(
            marcoBusqueda,
            text="Folio o Cliente:",
            style="Formulario.TLabel",
        ).pack(side="left")
        ttk.Entry(
            marcoBusqueda, textvariable=self._varBusquedaOrden, width=30
        ).pack(side="left", padx=8, fill="x", expand=True)
        ttk.Button(
            marcoBusqueda,
            text="Consultar",
            style="Secundario.TButton",
            command=self._consultarOrdenes,
        ).pack(side="left", padx=(0, 6))
        ttk.Button(
            marcoBusqueda,
            text="Mostrar Todas",
            style="Neutro.TButton",
            command=self._cargarTablaOrdenes,
        ).pack(side="left")

        marcoTabla = ttk.LabelFrame(
            marcoDerecho,
            text=" Listado de Órdenes Registradas ",
            style="Tarjeta.TLabelframe",
            padding=8,
        )
        marcoTabla.pack(fill="both", expand=True, pady=(0, 10))

        columnas = ("folio", "cliente", "tecnico", "dispositivo", "estado", "total")
        self._tablaOrdenes = ttk.Treeview(
            marcoTabla, columns=columnas, show="headings", selectmode="browse"
        )
        encabezados = {
            "folio": ("Folio", 85),
            "cliente": ("Cliente", 145),
            "tecnico": ("Técnico", 130),
            "dispositivo": ("Dispositivo", 170),
            "estado": ("Estado", 105),
            "total": ("Total ($)", 85),
        }
        for clave, (titulo, ancho) in encabezados.items():
            self._tablaOrdenes.heading(clave, text=titulo)
            self._tablaOrdenes.column(clave, width=ancho, anchor="center" if clave in ("folio", "total", "estado") else "w")

        scrollY = ttk.Scrollbar(
            marcoTabla, orient="vertical", command=self._tablaOrdenes.yview
        )
        self._tablaOrdenes.configure(yscrollcommand=scrollY.set)
        self._tablaOrdenes.pack(side="left", fill="both", expand=True)
        scrollY.pack(side="right", fill="y")
        self._tablaOrdenes.bind("<<TreeviewSelect>>", self._seleccionarOrdenTabla)

        marcoDetalle = ttk.LabelFrame(
            marcoDerecho,
            text=" Detalle Polimórfico de la Orden (__str__) ",
            style="Tarjeta.TLabelframe",
            padding=8,
        )
        marcoDetalle.pack(fill="x")

        self._textoDetalleOrden = tk.Text(
            marcoDetalle,
            height=6,
            wrap="word",
            bg="#F8FAFC",
            fg="#0F172A",
            font=("Courier", 9),
            state="disabled",
            relief="flat",
        )
        self._textoDetalleOrden.pack(fill="x")

    def _actualizarEtiquetaEspecifica(self, _evento=None):
        """Cambia la etiqueta dinámica entre RAM (GB) e IMEI según el tipo de equipo."""
        if self._varTipoDisp.get() == "DispositivoMovil":
            self._etiquetaEspecifica.config(text="IMEI (15 dígitos):")
        else:
            self._etiquetaEspecifica.config(text="RAM (GB):")

    def _construirOrdenDesdeFormulario(self):
        """Valida los campos del formulario y construye un objeto OrdenServicio."""
        folio = self._varFolio.get().strip()
        if not folio:
            raise ValueError("El folio de la orden no puede estar vacío.")

        nombreCliente = self._varClienteOrden.get().strip()
        if not nombreCliente or nombreCliente not in self._mapaClientes:
            raise ValueError("Selecciona un cliente válido del catálogo.")
        cliente = self._mapaClientes[nombreCliente]

        nombreTecnico = self._varTecnicoOrden.get().strip()
        if not nombreTecnico or nombreTecnico not in self._mapaTecnicos:
            raise ValueError("Selecciona un técnico válido del catálogo.")
        tecnico = self._mapaTecnicos[nombreTecnico]

        marca = self._varMarca.get().strip()
        modelo = self._varModelo.get().strip()
        falla = self._varFalla.get().strip()
        datoEsp = self._varEspecifico.get().strip()

        if self._varTipoDisp.get() == "DispositivoMovil":
            dispositivo = DispositivoMovil(marca, modelo, falla, datoEsp)
        else:
            dispositivo = Computadora(marca, modelo, falla, datoEsp)

        orden = OrdenServicio(
            folio,
            cliente,
            tecnico,
            dispositivo,
            costoManoObra=self._varManoObra.get(),
            costoRepuestos=self._varRepuestos.get(),
            descuento=self._varDescuento.get(),
            estado=self._varEstadoOrden.get(),
        )
        orden.calcularCostoTotal()
        return orden

    def _calcularTotalFormulario(self):
        """Calcula subtotal, total e IVA en tiempo real y muestra errores si los hay."""
        try:
            ordenTemporal = OrdenServicio(
                "TEMP",
                Cliente("Temporal", "4420000000", "Sin dirección"),
                Tecnico("Temporal", "4420000000", "General"),
                Computadora("Marca", "Modelo", "Falla", 8),
                costoManoObra=self._varManoObra.get(),
                costoRepuestos=self._varRepuestos.get(),
                descuento=self._varDescuento.get(),
            )
            subtotal = ordenTemporal.calcularSubtotal()
            total = ordenTemporal.calcularCostoTotal()
            iva = ordenTemporal.calcularIva()
            self._varCalculoOrden.set(
                f"Subtotal: ${subtotal:.2f} | Total: ${total:.2f} (IVA ref: ${iva:.2f})"
            )
        except (ValueError, ValorFueraDeRangoError) as exc:
            registrarError(f"{type(exc).__name__} en cálculo: {exc}")
            self._actualizarVistaBitacora()
            messagebox.showerror("Error en cálculo", str(exc))

    def _registrarOrden(self):
        """Registra una nueva orden validando datos, duplicados y persistencia."""
        try:
            orden = self._construirOrdenDesdeFormulario()
            self._gestorBd.registrarOrden(orden)
            self._cargarTablaOrdenes()
            self._mostrarDetalleOrden(orden)
            self._actualizarCalculoEtiqueta(orden)
            messagebox.showinfo(
                "Registro exitoso",
                f"Orden '{orden.folio}' registrada y guardada correctamente.",
            )
        except RegistroDuplicadoError as exc:
            self._actualizarVistaBitacora()
            messagebox.showerror("Registro duplicado", str(exc))
        except (ValueError, TypeError, ValorFueraDeRangoError) as exc:
            registrarError(f"{type(exc).__name__} al registrar orden: {exc}")
            self._actualizarVistaBitacora()
            messagebox.showwarning("Validación de datos", str(exc))

    def _modificarOrden(self):
        """Modifica una orden existente por folio y actualiza la persistencia."""
        try:
            orden = self._construirOrdenDesdeFormulario()
            self._gestorBd.modificarOrden(orden)
            self._cargarTablaOrdenes()
            self._mostrarDetalleOrden(orden)
            self._actualizarCalculoEtiqueta(orden)
            messagebox.showinfo(
                "Actualización exitosa",
                f"Orden '{orden.folio}' modificada correctamente.",
            )
        except RegistroNoEncontradoError as exc:
            self._actualizarVistaBitacora()
            messagebox.showerror("Registro inexistente", str(exc))
        except (ValueError, TypeError, ValorFueraDeRangoError) as exc:
            registrarError(f"{type(exc).__name__} al modificar orden: {exc}")
            self._actualizarVistaBitacora()
            messagebox.showwarning("Validación de datos", str(exc))

    def _eliminarOrden(self):
        """Elimina la orden correspondiente al folio indicado previa confirmación."""
        folio = self._varFolio.get().strip().upper()
        if not folio:
            mensaje = "Selecciona una orden de la tabla o escribe un folio para eliminar."
            registrarError(f"ValueError al eliminar orden: {mensaje}")
            self._actualizarVistaBitacora()
            messagebox.showwarning("Campo vacío", mensaje)
            return

        if not messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Deseas eliminar permanentemente la orden '{folio}'?",
        ):
            return

        try:
            self._gestorBd.eliminarOrden(folio)
            self._limpiarFormularioOrden()
            self._cargarTablaOrdenes()
            messagebox.showinfo(
                "Eliminación exitosa",
                f"La orden '{folio}' fue eliminada del sistema.",
            )
        except RegistroNoEncontradoError as exc:
            self._actualizarVistaBitacora()
            messagebox.showerror("Registro inexistente", str(exc))
        except ValueError as exc:
            registrarError(f"ValueError al eliminar orden: {exc}")
            self._actualizarVistaBitacora()
            messagebox.showwarning("Validación", str(exc))

    def _consultarOrdenes(self):
        """Filtra el Treeview según el folio o nombre de cliente ingresado."""
        criterio = self._varBusquedaOrden.get()
        try:
            ordenes = self._gestorBd.buscarOrdenes(criterio)
            self._poblarTreeviewOrdenes(ordenes)
            if ordenes:
                self._mostrarDetalleOrden(ordenes[0])
        except RegistroNoEncontradoError as exc:
            self._actualizarVistaBitacora()
            messagebox.showerror("Sin resultados", str(exc))
        except ValueError as exc:
            registrarError(f"ValueError al consultar órdenes: {exc}")
            self._actualizarVistaBitacora()
            messagebox.showwarning("Campo vacío", str(exc))

    def _seleccionarOrdenTabla(self, _evento=None):
        """Carga en el formulario la orden seleccionada en el Treeview."""
        seleccion = self._tablaOrdenes.selection()
        if not seleccion:
            return
        valores = self._tablaOrdenes.item(seleccion[0], "values")
        folio = valores[0]
        try:
            resultados = self._gestorBd.buscarOrdenes(folio)
            orden = next((o for o in resultados if o.folio == folio), resultados[0])
        except (RegistroNoEncontradoError, ValueError) as exc:
            registrarError(f"{type(exc).__name__} al seleccionar orden: {exc}")
            self._actualizarVistaBitacora()
            return

        self._varFolio.set(orden.folio)
        if orden.cliente.nombre in self._mapaClientes:
            self._varClienteOrden.set(orden.cliente.nombre)
        if orden.tecnico.nombre in self._mapaTecnicos:
            self._varTecnicoOrden.set(orden.tecnico.nombre)

        if isinstance(orden.dispositivo, DispositivoMovil):
            self._varTipoDisp.set("DispositivoMovil")
            self._varEspecifico.set(orden.dispositivo.imei)
        else:
            self._varTipoDisp.set("Computadora")
            self._varEspecifico.set(str(orden.dispositivo.ram))
        self._actualizarEtiquetaEspecifica()

        self._varMarca.set(orden.dispositivo.marca)
        self._varModelo.set(orden.dispositivo.modelo)
        self._varFalla.set(orden.dispositivo.fallaReportada)
        self._varManoObra.set(f"{orden.costoManoObra:.2f}")
        self._varRepuestos.set(f"{orden.costoRepuestos:.2f}")
        self._varDescuento.set(f"{orden.descuento:.2f}")
        self._varEstadoOrden.set(orden.estado)
        self._actualizarCalculoEtiqueta(orden)
        self._mostrarDetalleOrden(orden)

    def _actualizarCalculoEtiqueta(self, orden):
        """Actualiza la etiqueta resumen con subtotal, total e IVA de una orden."""
        subtotal = orden.calcularSubtotal()
        iva = orden.calcularIva()
        self._varCalculoOrden.set(
            f"Subtotal: ${subtotal:.2f} | Total: ${orden.costoTotal:.2f} (IVA ref: ${iva:.2f})"
        )

    def _mostrarDetalleOrden(self, orden):
        """Muestra la representación polimórfica __str__ de la orden en el panel."""
        self._textoDetalleOrden.config(state="normal")
        self._textoDetalleOrden.delete("1.0", "end")
        self._textoDetalleOrden.insert("1.0", str(orden))
        self._textoDetalleOrden.config(state="disabled")

    def _limpiarFormularioOrden(self):
        """Restablece los campos del formulario de órdenes a su estado inicial."""
        self._varFolio.set("")
        self._varMarca.set("")
        self._varModelo.set("")
        self._varFalla.set("")
        self._varEspecifico.set("")
        self._varManoObra.set("0.00")
        self._varRepuestos.set("0.00")
        self._varDescuento.set("0.00")
        self._varEstadoOrden.set("Recibido")
        self._varCalculoOrden.set("Subtotal: $0.00 | Total: $0.00 (IVA ref: $0.00)")
        self._textoDetalleOrden.config(state="normal")
        self._textoDetalleOrden.delete("1.0", "end")
        self._textoDetalleOrden.config(state="disabled")
        for item in self._tablaOrdenes.selection():
            self._tablaOrdenes.selection_remove(item)

    def _poblarTreeviewOrdenes(self, ordenes):
        """Llena el Treeview con la lista de objetos OrdenServicio recibida."""
        for item in self._tablaOrdenes.get_children():
            self._tablaOrdenes.delete(item)

        ingresos = 0.0
        for orden in ordenes:
            ingresos += orden.costoTotal
            resumenDisp = f"{orden.dispositivo.marca} {orden.dispositivo.modelo}"
            self._tablaOrdenes.insert(
                "",
                "end",
                values=(
                    orden.folio,
                    orden.cliente.nombre,
                    orden.tecnico.nombre,
                    resumenDisp,
                    orden.estado,
                    f"${orden.costoTotal:.2f}",
                ),
            )
        self._varResumen.set(
            f"Órdenes: {len(ordenes)} | Ingresos totales: ${ingresos:,.2f}"
        )

    def _cargarTablaOrdenes(self):
        """Recarga todas las órdenes desde la base de datos al Treeview."""
        self._varBusquedaOrden.set("")
        ordenes = self._gestorBd.obtenerOrdenes()
        self._poblarTreeviewOrdenes(ordenes)

    # =========================================================================
    # PESTAÑA 2: CATÁLOGO DE CLIENTES
    # =========================================================================
    def _construirTabClientes(self):
        """Construye el CRUD visual para el catálogo de clientes."""
        contenedor = ttk.Frame(self._tabClientes)
        contenedor.pack(fill="both", expand=True, padx=10, pady=10)

        marcoForm = ttk.LabelFrame(
            contenedor,
            text=" Datos del Cliente ",
            style="Tarjeta.TLabelframe",
            padding=14,
        )
        marcoForm.pack(side="left", fill="y", padx=(0, 10))

        self._varNombreCliente = tk.StringVar()
        self._varTelefonoCliente = tk.StringVar()
        self._varDireccionCliente = tk.StringVar()

        ttk.Label(marcoForm, text="Nombre completo:", style="Formulario.TLabel").grid(
            row=0, column=0, sticky="w", pady=6
        )
        ttk.Entry(marcoForm, textvariable=self._varNombreCliente, width=30).grid(
            row=0, column=1, sticky="ew", pady=6, padx=(8, 0)
        )

        ttk.Label(marcoForm, text="Teléfono (10 dígitos):", style="Formulario.TLabel").grid(
            row=1, column=0, sticky="w", pady=6
        )
        ttk.Entry(marcoForm, textvariable=self._varTelefonoCliente, width=30).grid(
            row=1, column=1, sticky="ew", pady=6, padx=(8, 0)
        )

        ttk.Label(marcoForm, text="Dirección:", style="Formulario.TLabel").grid(
            row=2, column=0, sticky="w", pady=6
        )
        ttk.Entry(marcoForm, textvariable=self._varDireccionCliente, width=30).grid(
            row=2, column=1, sticky="ew", pady=6, padx=(8, 0)
        )

        marcoBotones = tk.Frame(marcoForm, bg="#FFFFFF")
        marcoBotones.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(14, 0))
        marcoBotones.columnconfigure(0, weight=1)
        marcoBotones.columnconfigure(1, weight=1)

        ttk.Button(
            marcoBotones,
            text="Registrar Cliente",
            style="Primario.TButton",
            command=self._registrarCliente,
        ).grid(row=0, column=0, sticky="ew", padx=(0, 4), pady=3)
        ttk.Button(
            marcoBotones,
            text="Modificar Cliente",
            style="Secundario.TButton",
            command=self._modificarCliente,
        ).grid(row=0, column=1, sticky="ew", padx=(4, 0), pady=3)
        ttk.Button(
            marcoBotones,
            text="Eliminar Cliente",
            style="Peligro.TButton",
            command=self._eliminarCliente,
        ).grid(row=1, column=0, sticky="ew", padx=(0, 4), pady=3)
        ttk.Button(
            marcoBotones,
            text="Limpiar",
            style="Neutro.TButton",
            command=self._limpiarFormularioCliente,
        ).grid(row=1, column=1, sticky="ew", padx=(4, 0), pady=3)

        marcoTabla = ttk.LabelFrame(
            contenedor,
            text=" Clientes Registrados (Base de Datos SQLite) ",
            style="Tarjeta.TLabelframe",
            padding=8,
        )
        marcoTabla.pack(side="right", fill="both", expand=True)

        self._tablaClientes = ttk.Treeview(
            marcoTabla,
            columns=("id", "nombre", "telefono", "direccion"),
            show="headings",
            selectmode="browse",
        )
        self._tablaClientes.heading("id", text="ID")
        self._tablaClientes.heading("nombre", text="Nombre")
        self._tablaClientes.heading("telefono", text="Teléfono")
        self._tablaClientes.heading("direccion", text="Dirección")
        self._tablaClientes.column("id", width=50, anchor="center")
        self._tablaClientes.column("nombre", width=180, anchor="w")
        self._tablaClientes.column("telefono", width=120, anchor="center")
        self._tablaClientes.column("direccion", width=230, anchor="w")

        scrollY = ttk.Scrollbar(
            marcoTabla, orient="vertical", command=self._tablaClientes.yview
        )
        self._tablaClientes.configure(yscrollcommand=scrollY.set)
        self._tablaClientes.pack(side="left", fill="both", expand=True)
        scrollY.pack(side="right", fill="y")
        self._tablaClientes.bind("<<TreeviewSelect>>", self._seleccionarClienteTabla)

    def _registrarCliente(self):
        """Valida e inserta un nuevo cliente en la base de datos."""
        try:
            cliente = Cliente(
                self._varNombreCliente.get(),
                self._varTelefonoCliente.get(),
                self._varDireccionCliente.get(),
            )
            self._gestorBd.registrarCliente(cliente)
            self._cargarClientes()
            self._limpiarFormularioCliente()
            messagebox.showinfo(
                "Cliente registrado",
                f"Cliente '{cliente.nombre}' guardado en el catálogo.",
            )
        except RegistroDuplicadoError as exc:
            self._actualizarVistaBitacora()
            messagebox.showerror("Cliente duplicado", str(exc))
        except (ValueError, ValorFueraDeRangoError) as exc:
            registrarError(f"{type(exc).__name__} al registrar cliente: {exc}")
            self._actualizarVistaBitacora()
            messagebox.showwarning("Validación de cliente", str(exc))

    def _modificarCliente(self):
        """Actualiza los datos del cliente seleccionado."""
        if self._idClienteSeleccionado is None:
            mensaje = "Selecciona un cliente del listado para modificarlo."
            registrarError(f"RegistroNoEncontradoError al modificar cliente: {mensaje}")
            self._actualizarVistaBitacora()
            messagebox.showwarning("Selección requerida", mensaje)
            return

        try:
            cliente = Cliente(
                self._varNombreCliente.get(),
                self._varTelefonoCliente.get(),
                self._varDireccionCliente.get(),
            )
            self._gestorBd.modificarCliente(self._idClienteSeleccionado, cliente)
            self._cargarClientes()
            self._limpiarFormularioCliente()
            messagebox.showinfo(
                "Cliente actualizado",
                f"Los datos de '{cliente.nombre}' fueron actualizados.",
            )
        except RegistroDuplicadoError as exc:
            self._actualizarVistaBitacora()
            messagebox.showerror("Cliente duplicado", str(exc))
        except RegistroNoEncontradoError as exc:
            self._actualizarVistaBitacora()
            messagebox.showerror("Registro inexistente", str(exc))
        except (ValueError, ValorFueraDeRangoError) as exc:
            registrarError(f"{type(exc).__name__} al modificar cliente: {exc}")
            self._actualizarVistaBitacora()
            messagebox.showwarning("Validación de cliente", str(exc))

    def _eliminarCliente(self):
        """Elimina el cliente seleccionado previa confirmación."""
        if self._idClienteSeleccionado is None:
            mensaje = "Selecciona un cliente del listado para eliminarlo."
            registrarError(f"RegistroNoEncontradoError al eliminar cliente: {mensaje}")
            self._actualizarVistaBitacora()
            messagebox.showwarning("Selección requerida", mensaje)
            return

        if not messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Eliminar al cliente '{self._varNombreCliente.get()}' del catálogo?",
        ):
            return

        try:
            self._gestorBd.eliminarCliente(self._idClienteSeleccionado)
            self._cargarClientes()
            self._limpiarFormularioCliente()
            messagebox.showinfo("Cliente eliminado", "Cliente eliminado correctamente.")
        except RegistroNoEncontradoError as exc:
            self._actualizarVistaBitacora()
            messagebox.showerror("Registro inexistente", str(exc))

    def _seleccionarClienteTabla(self, _evento=None):
        """Carga el cliente seleccionado en el formulario."""
        seleccion = self._tablaClientes.selection()
        if not seleccion:
            return
        valores = self._tablaClientes.item(seleccion[0], "values")
        self._idClienteSeleccionado = int(valores[0])
        self._varNombreCliente.set(valores[1])
        self._varTelefonoCliente.set(valores[2])
        self._varDireccionCliente.set(valores[3])

    def _limpiarFormularioCliente(self):
        """Limpia los campos del formulario de clientes."""
        self._idClienteSeleccionado = None
        self._varNombreCliente.set("")
        self._varTelefonoCliente.set("")
        self._varDireccionCliente.set("")
        for item in self._tablaClientes.selection():
            self._tablaClientes.selection_remove(item)

    def _cargarClientes(self):
        """Recarga el catálogo de clientes en la tabla y en el Combobox de órdenes."""
        for item in self._tablaClientes.get_children():
            self._tablaClientes.delete(item)
        self._mapaClientes.clear()

        registros = self._gestorBd.obtenerClientes()
        nombres = []
        for idCliente, cliente in registros:
            self._tablaClientes.insert(
                "",
                "end",
                values=(idCliente, cliente.nombre, cliente.telefono, cliente.direccion),
            )
            self._mapaClientes[cliente.nombre] = cliente
            nombres.append(cliente.nombre)

        self._comboClientes["values"] = nombres
        if nombres and self._varClienteOrden.get() not in self._mapaClientes:
            self._varClienteOrden.set(nombres[0])

    # =========================================================================
    # PESTAÑA 3: CATÁLOGO DE TÉCNICOS
    # =========================================================================
    def _construirTabTecnicos(self):
        """Construye el CRUD visual para el catálogo de técnicos."""
        contenedor = ttk.Frame(self._tabTecnicos)
        contenedor.pack(fill="both", expand=True, padx=10, pady=10)

        marcoForm = ttk.LabelFrame(
            contenedor,
            text=" Datos del Técnico ",
            style="Tarjeta.TLabelframe",
            padding=14,
        )
        marcoForm.pack(side="left", fill="y", padx=(0, 10))

        self._varNombreTecnico = tk.StringVar()
        self._varTelefonoTecnico = tk.StringVar()
        self._varEspecialidadTecnico = tk.StringVar(value=self.ESPECIALIDADES_BASE[0])

        ttk.Label(marcoForm, text="Nombre completo:", style="Formulario.TLabel").grid(
            row=0, column=0, sticky="w", pady=6
        )
        ttk.Entry(marcoForm, textvariable=self._varNombreTecnico, width=30).grid(
            row=0, column=1, sticky="ew", pady=6, padx=(8, 0)
        )

        ttk.Label(marcoForm, text="Teléfono (10 dígitos):", style="Formulario.TLabel").grid(
            row=1, column=0, sticky="w", pady=6
        )
        ttk.Entry(marcoForm, textvariable=self._varTelefonoTecnico, width=30).grid(
            row=1, column=1, sticky="ew", pady=6, padx=(8, 0)
        )

        ttk.Label(marcoForm, text="Especialidad:", style="Formulario.TLabel").grid(
            row=2, column=0, sticky="w", pady=6
        )
        ttk.Combobox(
            marcoForm,
            textvariable=self._varEspecialidadTecnico,
            values=self.ESPECIALIDADES_BASE,
            width=28,
        ).grid(row=2, column=1, sticky="ew", pady=6, padx=(8, 0))

        marcoBotones = tk.Frame(marcoForm, bg="#FFFFFF")
        marcoBotones.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(14, 0))
        marcoBotones.columnconfigure(0, weight=1)
        marcoBotones.columnconfigure(1, weight=1)

        ttk.Button(
            marcoBotones,
            text="Registrar Técnico",
            style="Primario.TButton",
            command=self._registrarTecnico,
        ).grid(row=0, column=0, sticky="ew", padx=(0, 4), pady=3)
        ttk.Button(
            marcoBotones,
            text="Modificar Técnico",
            style="Secundario.TButton",
            command=self._modificarTecnico,
        ).grid(row=0, column=1, sticky="ew", padx=(4, 0), pady=3)
        ttk.Button(
            marcoBotones,
            text="Eliminar Técnico",
            style="Peligro.TButton",
            command=self._eliminarTecnico,
        ).grid(row=1, column=0, sticky="ew", padx=(0, 4), pady=3)
        ttk.Button(
            marcoBotones,
            text="Limpiar",
            style="Neutro.TButton",
            command=self._limpiarFormularioTecnico,
        ).grid(row=1, column=1, sticky="ew", padx=(4, 0), pady=3)

        marcoTabla = ttk.LabelFrame(
            contenedor,
            text=" Técnicos Registrados (Base de Datos SQLite) ",
            style="Tarjeta.TLabelframe",
            padding=8,
        )
        marcoTabla.pack(side="right", fill="both", expand=True)

        self._tablaTecnicos = ttk.Treeview(
            marcoTabla,
            columns=("id", "nombre", "telefono", "especialidad"),
            show="headings",
            selectmode="browse",
        )
        self._tablaTecnicos.heading("id", text="ID")
        self._tablaTecnicos.heading("nombre", text="Nombre")
        self._tablaTecnicos.heading("telefono", text="Teléfono")
        self._tablaTecnicos.heading("especialidad", text="Especialidad")
        self._tablaTecnicos.column("id", width=50, anchor="center")
        self._tablaTecnicos.column("nombre", width=180, anchor="w")
        self._tablaTecnicos.column("telefono", width=120, anchor="center")
        self._tablaTecnicos.column("especialidad", width=220, anchor="w")

        scrollY = ttk.Scrollbar(
            marcoTabla, orient="vertical", command=self._tablaTecnicos.yview
        )
        self._tablaTecnicos.configure(yscrollcommand=scrollY.set)
        self._tablaTecnicos.pack(side="left", fill="both", expand=True)
        scrollY.pack(side="right", fill="y")
        self._tablaTecnicos.bind("<<TreeviewSelect>>", self._seleccionarTecnicoTabla)

    def _registrarTecnico(self):
        """Valida e inserta un nuevo técnico en la base de datos."""
        try:
            tecnico = Tecnico(
                self._varNombreTecnico.get(),
                self._varTelefonoTecnico.get(),
                self._varEspecialidadTecnico.get(),
            )
            self._gestorBd.registrarTecnico(tecnico)
            self._cargarTecnicos()
            self._limpiarFormularioTecnico()
            messagebox.showinfo(
                "Técnico registrado",
                f"Técnico '{tecnico.nombre}' guardado en el catálogo.",
            )
        except RegistroDuplicadoError as exc:
            self._actualizarVistaBitacora()
            messagebox.showerror("Técnico duplicado", str(exc))
        except (ValueError, ValorFueraDeRangoError) as exc:
            registrarError(f"{type(exc).__name__} al registrar técnico: {exc}")
            self._actualizarVistaBitacora()
            messagebox.showwarning("Validación de técnico", str(exc))

    def _modificarTecnico(self):
        """Actualiza los datos del técnico seleccionado."""
        if self._idTecnicoSeleccionado is None:
            mensaje = "Selecciona un técnico del listado para modificarlo."
            registrarError(f"RegistroNoEncontradoError al modificar técnico: {mensaje}")
            self._actualizarVistaBitacora()
            messagebox.showwarning("Selección requerida", mensaje)
            return

        try:
            tecnico = Tecnico(
                self._varNombreTecnico.get(),
                self._varTelefonoTecnico.get(),
                self._varEspecialidadTecnico.get(),
            )
            self._gestorBd.modificarTecnico(self._idTecnicoSeleccionado, tecnico)
            self._cargarTecnicos()
            self._limpiarFormularioTecnico()
            messagebox.showinfo(
                "Técnico actualizado",
                f"Los datos de '{tecnico.nombre}' fueron actualizados.",
            )
        except RegistroDuplicadoError as exc:
            self._actualizarVistaBitacora()
            messagebox.showerror("Técnico duplicado", str(exc))
        except RegistroNoEncontradoError as exc:
            self._actualizarVistaBitacora()
            messagebox.showerror("Registro inexistente", str(exc))
        except (ValueError, ValorFueraDeRangoError) as exc:
            registrarError(f"{type(exc).__name__} al modificar técnico: {exc}")
            self._actualizarVistaBitacora()
            messagebox.showwarning("Validación de técnico", str(exc))

    def _eliminarTecnico(self):
        """Elimina el técnico seleccionado previa confirmación."""
        if self._idTecnicoSeleccionado is None:
            mensaje = "Selecciona un técnico del listado para eliminarlo."
            registrarError(f"RegistroNoEncontradoError al eliminar técnico: {mensaje}")
            self._actualizarVistaBitacora()
            messagebox.showwarning("Selección requerida", mensaje)
            return

        if not messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Eliminar al técnico '{self._varNombreTecnico.get()}' del catálogo?",
        ):
            return

        try:
            self._gestorBd.eliminarTecnico(self._idTecnicoSeleccionado)
            self._cargarTecnicos()
            self._limpiarFormularioTecnico()
            messagebox.showinfo("Técnico eliminado", "Técnico eliminado correctamente.")
        except RegistroNoEncontradoError as exc:
            self._actualizarVistaBitacora()
            messagebox.showerror("Registro inexistente", str(exc))

    def _seleccionarTecnicoTabla(self, _evento=None):
        """Carga el técnico seleccionado en el formulario."""
        seleccion = self._tablaTecnicos.selection()
        if not seleccion:
            return
        valores = self._tablaTecnicos.item(seleccion[0], "values")
        self._idTecnicoSeleccionado = int(valores[0])
        self._varNombreTecnico.set(valores[1])
        self._varTelefonoTecnico.set(valores[2])
        self._varEspecialidadTecnico.set(valores[3])

    def _limpiarFormularioTecnico(self):
        """Limpia los campos del formulario de técnicos."""
        self._idTecnicoSeleccionado = None
        self._varNombreTecnico.set("")
        self._varTelefonoTecnico.set("")
        self._varEspecialidadTecnico.set(self.ESPECIALIDADES_BASE[0])
        for item in self._tablaTecnicos.selection():
            self._tablaTecnicos.selection_remove(item)

    def _cargarTecnicos(self):
        """Recarga el catálogo de técnicos en la tabla y en el Combobox de órdenes."""
        for item in self._tablaTecnicos.get_children():
            self._tablaTecnicos.delete(item)
        self._mapaTecnicos.clear()

        registros = self._gestorBd.obtenerTecnicos()
        nombres = []
        for idTecnico, tecnico in registros:
            self._tablaTecnicos.insert(
                "",
                "end",
                values=(idTecnico, tecnico.nombre, tecnico.telefono, tecnico.especialidad),
            )
            self._mapaTecnicos[tecnico.nombre] = tecnico
            nombres.append(tecnico.nombre)

        self._comboTecnicos["values"] = nombres
        if nombres and self._varTecnicoOrden.get() not in self._mapaTecnicos:
            self._varTecnicoOrden.set(nombres[0])

    # =========================================================================
    # PESTAÑA 4: BITÁCORA DE ERRORES
    # =========================================================================
    def _construirTabBitacora(self):
        """Construye el visor de la bitácora de errores (log_errores.txt)."""
        contenedor = ttk.Frame(self._tabBitacora)
        contenedor.pack(fill="both", expand=True, padx=10, pady=10)

        marcoSuperior = ttk.Frame(contenedor)
        marcoSuperior.pack(fill="x", pady=(0, 8))

        ttk.Label(
            marcoSuperior,
            text="Registro histórico de excepciones (log_errores.txt):",
            font=("Helvetica", 10, "bold"),
        ).pack(side="left")

        ttk.Button(
            marcoSuperior,
            text="Actualizar Bitácora",
            style="Secundario.TButton",
            command=self._actualizarVistaBitacora,
        ).pack(side="right")

        marcoTexto = ttk.LabelFrame(
            contenedor,
            text=" Contenido de log_errores.txt ",
            style="Tarjeta.TLabelframe",
            padding=8,
        )
        marcoTexto.pack(fill="both", expand=True)

        self._textoBitacora = tk.Text(
            marcoTexto,
            wrap="word",
            bg="#0F172A",
            fg="#E2E8F0",
            font=("Courier", 10),
            state="disabled",
        )
        scrollY = ttk.Scrollbar(
            marcoTexto, orient="vertical", command=self._textoBitacora.yview
        )
        self._textoBitacora.configure(yscrollcommand=scrollY.set)
        self._textoBitacora.pack(side="left", fill="both", expand=True)
        scrollY.pack(side="right", fill="y")

    def _actualizarVistaBitacora(self):
        """Recarga el contenido actual de log_errores.txt en la interfaz."""
        contenido = leerBitacora()
        self._textoBitacora.config(state="normal")
        self._textoBitacora.delete("1.0", "end")
        if contenido.strip():
            self._textoBitacora.insert("1.0", contenido)
        else:
            self._textoBitacora.insert(
                "1.0", "No hay errores registrados en log_errores.txt todavía."
            )
        self._textoBitacora.config(state="disabled")

    def _cargarTodo(self):
        """Carga inicial sincronizada de catálogos, órdenes y bitácora."""
        self._cargarClientes()
        self._cargarTecnicos()
        self._cargarTablaOrdenes()
        self._actualizarVistaBitacora()
