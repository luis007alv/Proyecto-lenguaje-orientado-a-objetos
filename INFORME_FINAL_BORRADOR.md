# Informe Final — Sistema de Gestión de Reparaciones Tecnológicas (SGRT)

> **Nota para entrega final:** Completa los datos de portada (integrantes y grupo), inserta las capturas de pantalla reales ejecutando `python3 main.py` en tu equipo y exporta este documento a PDF (`Informe_Final_SGRT.pdf`).

---

## 1. Portada
- **Nombre del proyecto:** Sistema de Gestión de Reparaciones Tecnológicas (SGRT)
- **Materia:** Lenguaje Orientado a Objetos (Python) — Anáhuac Querétaro
- **Integrantes:** `[COMPLETAR CON NOMBRES DE INTEGRANTES]`
- **Grupo:** `[COMPLETAR CON GRUPO]`
- **Fecha:** `[COMPLETAR CON FECHA DE ENTREGA]`

---

## 2. Introducción y análisis
El **SGRT** es una aplicación de escritorio orientada a objetos desarrollada en Python para administrar el flujo operativo de un taller de servicio técnico especializado en computadoras y dispositivos móviles.

### Procesos principales
1. **Gestión de catálogos (Clientes y Técnicos):** Alta, consulta, modificación y baja persistidas en base de datos SQLite (`catalogos_sgrt.db`).
2. **Administración de Órdenes de Servicio:** Registro, consulta por folio/cliente, actualización de estado, modificación de costos y eliminación, vinculando cliente, técnico y tipo de dispositivo (`Computadora` o `DispositivoMovil`).
3. **Cálculo de costos y bitácora de errores:** Cálculo automático de subtotal, descuento, costo total e IVA informativo, junto con registro automático de excepciones en `log_errores.txt`.

### Requerimientos implementados
- **POO:** 7 clases de dominio (`Persona`, `Cliente`, `Tecnico`, `Dispositivo`, `Computadora`, `DispositivoMovil`, `OrdenServicio`), más `GestorArchivos`, `GestorBaseDatos`, `AplicacionSGRT` y 3 excepciones personalizadas (`ValorFueraDeRangoError`, `RegistroDuplicadoError`, `RegistroNoEncontradoError`).
- **Interfaz gráfica:** Ventana Tkinter con logo visible (`logo_sgrt.png`), pestañas (`ttk.Notebook`), formularios, `Combobox`, `Treeview`, `messagebox` y cálculos en tiempo real.
- **Persistencia dual:** Catálogos y órdenes en SQLite (`catalogos_sgrt.db`) sincronizados con respaldo JSON en `ordenes_datos.txt` y bitácora `log_errores.txt`.

---

## 3. UML (Anterior vs. Corregido)

### UML anterior (Parte 1 y 2)
En la etapa anterior se contemplaban únicamente las 7 clases del dominio (`Persona`, `Cliente`, `Tecnico`, `Dispositivo`, `Computadora`, `DispositivoMovil`, `OrdenServicio`) y la clase utilitaria `GestorArchivos`.

- *(Insertar aquí imagen del UML de la Parte 1 / Parte 2)*

### UML corregido (Parte 3)
El diagrama actualizado se encuentra en el archivo [`uml_actualizado.svg`](uml_actualizado.svg) dentro del repositorio.

- *(Insertar aquí captura/imagen de `uml_actualizado.svg`)*

### Correcciones realizadas y justificación
1. **Polimorfismo de serialización (`toDict()` y `desdeDict()`):** Se corrigió `OrdenServicio.toDict()` y se añadió `toDict()` en `Persona`, `Cliente`, `Tecnico`, `Dispositivo`, `Computadora` y `DispositivoMovil`, porque en el diseño anterior `DispositivoMovil` perdía su `_imei` al guardarse en JSON.
2. **Desglose y cálculo de costos en `OrdenServicio`:** Se agregaron `_costoManoObra`, `_costoRepuestos`, `_descuento`, `_estado`, `calcularSubtotal()`, `calcularCostoTotal()` y `calcularIva()` para cubrir los requerimientos de cálculos en la GUI.
3. **Persistencia de catálogos en SQLite (`GestorBaseDatos`):** Se incorporó `GestorBaseDatos` (`catalogos_sgrt.db`) para almacenar de forma relacional los catálogos de clientes, técnicos y órdenes sin perder la compatibilidad con `ordenes_datos.txt`.
4. **Excepciones personalizadas:** Se añadieron `ValorFueraDeRangoError`, `RegistroDuplicadoError` y `RegistroNoEncontradoError` para distinguir claramente las reglas de negocio en las validaciones de la GUI.
5. **Clase de interfaz gráfica (`AplicacionSGRT`):** Se integró `AplicacionSGRT(tk.Tk)` como capa visual conectada a `GestorBaseDatos` y a los modelos.

---

## 4. Bitácora de cambios

| Cambio realizado | Clase, módulo o archivo afectado | Motivo | ¿Se reflejó en el UML? |
| :--- | :--- | :--- | :--- |
| Soporte completo de `DispositivoMovil` (`imei`) en serialización y reconstrucción | `modelos.py` (`Dispositivo`, `Computadora`, `DispositivoMovil`, `OrdenServicio`) | El código original solo guardaba `ram` e ignoraba `imei` al cargar | Sí |
| Desglose de costos (`costoManoObra`, `costoRepuestos`, `descuento`, `estado`) y métodos de cálculo | `modelos.py` (`OrdenServicio`) | Requisito de cálculos reales desde la interfaz gráfica | Sí |
| Validaciones con `@property` en todas las clases y creación de excepciones personalizadas | `modelos.py` | Evitar campos vacíos, texto por número, valores fuera de rango y duplicados | Sí |
| Adición de `GestorBaseDatos` con SQLite (`catalogos_sgrt.db`) y cierre seguro con `@contextmanager` | `persistencia.py` | Requisito de archivo de persistencia BD para catálogos propios del sistema | Sí |
| Creación de interfaz gráfica completa con Tkinter, `Treeview`, pestañas, `messagebox` y logo | `interfaz.py` (`AplicacionSGRT`), `logo_sgrt.png` | Requisito principal de la Tercera Parte | Sí |
| Conversión de `main.py` a lanzador de la GUI y creación de `pruebas.py` | `main.py`, `pruebas.py` | Ejecución desde un solo archivo de inicio en carpeta limpia | Sí |

---

## 5. Código y aplicación de principios POO
- **Herencia y `super().__init__()`:** `Cliente` y `Tecnico` heredan de `Persona`; `Computadora` y `DispositivoMovil` heredan de `Dispositivo`, invocando `super().__init__(...)`.
- **Encapsulamiento:** Todos los atributos sensibles utilizan prefijo `_` (`_nombre`, `_telefono`, `_ram`, `_imei`, `_costoTotal`, `_folio`, etc.) protegidos mediante `@property` y setters con validación estricta.
- **Polimorfismo:** Sobrescritura de `__str__()` y `toDict()` en todas las clases base e hijas para adaptar la salida según el tipo concreto de persona o dispositivo.
- **Nomenclatura:** Uso uniforme de `camelCase` para métodos, atributos y variables, con un único idioma (español) y docstrings descriptivos.

---

## 6. Interfaz gráfica
*(Ejecuta `python3 main.py` y agrega capturas legibles con su pie explicativo):*
1. **Ventana principal y pestaña de Órdenes de Servicio:** Logo `logo_sgrt.png` visible en el encabezado, formulario de captura, botones CRUD, cálculo de total y listado `Treeview`.
2. **Pestaña Catálogo de Clientes y Catálogo de Técnicos:** Formularios CRUD y sincronización inmediata con los `Combobox` de órdenes.
3. **Pestaña Bitácora de Errores:** Visor en tiempo real de `log_errores.txt`.

---

## 7. Manejo de excepciones y validaciones
- **Campos vacíos:** Validados en setters y formulario; registran `ValueError` en `log_errores.txt` y muestran `messagebox.showwarning`.
- **Texto en lugar de número:** Al ingresar texto en RAM o montos, se captura `ValueError`, se registra en el log y se alerta al usuario con `messagebox`.
- **Valores fuera de rango:** Costos negativos, descuento mayor al subtotal, RAM fuera de `1..1024`, IMEI distinto a 15 dígitos o teléfono fuera de `8..15` dígitos lanzan `ValorFueraDeRangoError`.
- **Registros duplicados / inexistentes:** `GestorBaseDatos` lanza `RegistroDuplicadoError` (ej. folio repetido) y `RegistroNoEncontradoError` (ej. búsqueda sin coincidencias), mostrando `messagebox.showerror`.
- **Archivos:** `GestorArchivos` captura `FileNotFoundError`, `PermissionError` y `json.JSONDecodeError`.

*(Insertar captura de `log_errores.txt` y captura de `messagebox` en pantalla).*

---

## 8. Pruebas realizadas (`pruebas.py`)
Ejecución verificada mediante `python3 pruebas.py` (12 de 12 pruebas aprobadas):

| N.º | Funcionalidad probada | Datos de entrada | Resultado esperado | Resultado obtenido | ¿Pasó? | Captura |
| :---: | :--- | :--- | :--- | :--- | :---: | :--- |
| 1 | Alta de orden (Computadora) y cálculo | Folio `ORD-201`, HP Pavilion 15, RAM `16`, Mano de obra `800`, Repuestos `1200`, Descuento `100` | Registro guardado y total `$1900.00` | Orden guardada con total `$1900.00` | Sí | *(Agregar)* |
| 2 | Alta de orden (DispositivoMovil) y polimorfismo | Folio `ORD-202`, Samsung Galaxy S23, IMEI `123456789012345` | Registro con etiqueta `[Móvil]` e IMEI visible | `[Móvil]` e IMEI verificados en `__str__()` | Sí | *(Agregar)* |
| 3 | Consulta por folio y cliente | Criterio `"ORD-100"` y `"Santiago"` | Retorna órdenes coincidentes | Coincidencias recuperadas correctamente | Sí | *(Agregar)* |
| 4 | Modificación de orden y recálculo | `ORD-100`: Mano de obra `1500`, Repuestos `1500`, Descuento `200`, Estado `Listo` | Total actualizado a `$2800.00` y estado `Listo` | Actualización persistida y verificada | Sí | *(Agregar)* |
| 5 | Baja (eliminación) de orden | Folio `ORD-100` | Orden eliminada; nueva búsqueda lanza `RegistroNoEncontradoError` | Eliminada y excepción verificada | Sí | *(Agregar)* |
| 6 | Persistencia al reabrir aplicación | Alta de cliente `Carlos Sandoval`, reinicio de `GestorBaseDatos` | Los registros permanecen en SQLite y `ordenes_datos.txt` | Cliente y órdenes intactos al reabrir | Sí | *(Agregar)* |
| 7 | Error: campos vacíos | Cliente con nombre `""` | Lanza `ValueError` | `ValueError` capturado correctamente | Sí | *(Agregar)* |
| 8 | Error: texto en lugar de número | Computadora con RAM `"dieciseis"` | Lanza `ValueError` | `ValueError` capturado correctamente | Sí | *(Agregar)* |
| 9 | Error: valor fuera de rango | `costoTotal = -50.0` y RAM `4096` | Lanza `ValorFueraDeRangoError` | `ValorFueraDeRangoError` capturado | Sí | *(Agregar)* |
| 10 | Error: registro duplicado | Registrar folio existente `ORD-100` | Lanza `RegistroDuplicadoError` | `RegistroDuplicadoError` capturado | Sí | *(Agregar)* |
| 11 | Error: registro inexistente | Buscar o eliminar folio `ORD-999` | Lanza `RegistroNoEncontradoError` | `RegistroNoEncontradoError` capturado | Sí | *(Agregar)* |
| 12 | Bitácora de errores | `registrarError("ValueError: ...")` | Se guarda línea con fecha, hora y mensaje | Línea escrita y leída desde archivo | Sí | *(Agregar)* |

---

## 9. Errores encontrados y cómo se resolvieron
1. **`TypeError` al inicializar `OrdenServicio` con valores numéricos en cadena desde la GUI:**
   - *Problema:* El constructor comparaba `if costoManoObra > 0` usando el parámetro crudo (`str` proveniente de `tk.StringVar`) en lugar del atributo ya convertido a `float` por el setter.
   - *Solución:* Se corrigió la condición a `if self._costoManoObra > 0 or self._costoRepuestos > 0 or self._descuento > 0:` en `modelos.py` y se agregó prueba de regresión en `pruebas.py`.
2. **`ResourceWarning: unclosed database` en conexiones SQLite bajo Python 3.14:**
   - *Problema:* `with sqlite3.connect(...)` gestiona transacciones (`commit`/`rollback`) pero no cierra automáticamente la conexión al salir del bloque.
   - *Solución:* Se implementó `_conectar()` con `@contextmanager` en `persistencia.py` garantizando `conexion.commit()`, `rollback()` ante errores y `conexion.close()` en `finally`.
3. **Pérdida del atributo `imei` de `DispositivoMovil` en `toDict()`:**
   - *Problema:* En la Parte 2 `toDict()` solo serializaba `ram` y no incluía el tipo de dispositivo ni `imei`.
   - *Solución:* Se implementó `toDict()` polimórfico en `Dispositivo`, `Computadora` y `DispositivoMovil`, junto con `OrdenServicio.desdeDict()`.

---

## 10. Repositorio en GitHub
- **URL del repositorio:** https://github.com/luis007alv/Proyecto-lenguaje-orientado-a-objetos
- **Colaboradora invitada:** `amkaguilar@gmail.com` *(Verificar en Settings → Collaborators → Add people en GitHub).*

---

## 11. Conclusiones
- Se integró exitosamente una interfaz gráfica completa en Tkinter con los modelos POO, persistencia dual (SQLite + JSON en texto) y manejo robusto de excepciones con `messagebox` y bitácora en `log_errores.txt`.
- Como mejora futura se plantea generar recibos imprimibles en PDF por orden y añadir filtros por rango de fechas o técnico asignado.
