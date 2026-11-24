# Informe Final — Sistema de Gestión de Reparaciones Tecnológicas (SGRT)

> **Nota para entrega final:** Completa el grupo y la fecha en la portada, inserta las capturas de pantalla reales ejecutando `python3 main.py` y `python3 pruebas.py` en tu equipo, y exporta este documento a PDF (`Informe_Final_SGRT.pdf`).

---

## 1. Portada
- **Nombre del proyecto:** Sistema de Gestión de Reparaciones Tecnológicas (SGRT)
- **Materia:** Lenguaje Orientado a Objetos (Python) — Universidad Anáhuac Querétaro
- **Integrantes:** Santiago Alarcón Díaz, Luis Eduardo Álvarez Ayala
- **Grupo:** `Santiago Alarcón Díaz, Luis Álvarez`
- **Fecha:** `25 de noviembre`

---

## 2. Introducción y análisis
El **SGRT** es una aplicación de escritorio orientada a objetos desarrollada en Python para administrar el flujo operativo de un taller de servicio técnico especializado en computadoras y dispositivos móviles.

### Procesos principales
1. **Gestión de catálogos (Clientes y Técnicos):** Alta, consulta, modificación y baja persistidas en base de datos SQLite (`catalogos_sgrt.db`), validando integridad referencial para impedir borrar registros con órdenes asociadas.
2. **Administración de Órdenes de Servicio:** Registro, consulta por folio o cliente, actualización de estado (`En diagnóstico`, `Reparación`, `Entregado`), modificación de costos y eliminación, vinculando cliente, técnico y tipo de dispositivo (`Computadora` o `DispositivoMovil`).
3. **Cálculo de costos y bitácora de errores:** Cálculo automático del costo total (`costoComponentes + costoManoObra`), generación de ticket-factura y registro automático de excepciones con fecha y hora en `log_errores.txt`.

### Requerimientos implementados
- **POO:** 7 clases de dominio (`Persona`, `Cliente`, `Tecnico`, `Dispositivo`, `Computadora`, `DispositivoMovil`, `OrdenServicio`), 2 clases de persistencia (`GestorArchivos`, `GestorBaseDatos`), la clase visual `InterfazTaller` y 3 excepciones personalizadas (`ValorFueraDeRangoError`, `RegistroDuplicadoError`, `RegistroNoEncontradoError`).
- **Interfaz gráfica:** Ventana Tkinter (`InterfazTaller`) con logo visible (`logo_sgrt.png`), pestañas (`ttk.Notebook`), formularios, `Combobox`, `Treeview`, `messagebox` y cálculo de costos en tiempo real.
- **Persistencia dual:** Catálogos y órdenes en SQLite (`catalogos_sgrt.db`) sincronizados con respaldo JSON en `ordenes_datos.txt` y bitácora `log_errores.txt`.

---

## 3. UML (Anterior vs. Corregido)

### UML anterior (Parte 1 y 2)
En la etapa anterior se contemplaban únicamente las 7 clases del dominio (`Persona`, `Cliente`, `Tecnico`, `Dispositivo`, `Computadora`, `DispositivoMovil`, `OrdenServicio`) y la clase utilitaria `GestorArchivos`.

- <img width="1111" height="754" alt="image" src="https://github.com/user-attachments/assets/3410144a-73c2-4753-92a7-8e2236a69e5b" />
- <img width="1111" height="754" alt="image" src="https://github.com/user-attachments/assets/9431ee2c-fe89-4c01-add1-93f7528026e5" />

### UML corregido (Parte 3)
El diagrama actualizado se encuentra en el archivo [`uml_actualizado.svg`](uml_actualizado.svg) dentro del repositorio, mostrando tanto atributos privados (`-`) como métodos auxiliares privados (`- _...`) y métodos públicos (`+`).

- <img width="1416" height="951" alt="image" src="https://github.com/user-attachments/assets/858d561f-10cd-4ce3-88a5-3fc5dd3c1e3a" />


### Correcciones realizadas y justificación
1. **Polimorfismo de serialización (`toDict()` y `desdeDict()`):** Se implementó `toDict()` en `Persona`, `Cliente`, `Tecnico`, `Dispositivo`, `Computadora`, `DispositivoMovil` y `OrdenServicio` junto con `OrdenServicio.desdeDict()`, asegurando que tanto `ram` como `imei` se conserven al guardar y cargar en `ordenes_datos.txt`.
2. **Desglose y cálculo de costos en `OrdenServicio`:** Se integraron `_costoComponentes`, `_costoManoObra`, `_costoTotal`, `_estado`, `calcularCosto()`, `cambiarEstado()` y `generarResumen()` para respaldar la operación de la GUI.
3. **Persistencia de catálogos en SQLite (`GestorBaseDatos`):** Se incorporó `GestorBaseDatos` (`catalogos_sgrt.db`) para administrar de forma relacional clientes, técnicos y órdenes, con sincronización automática hacia `ordenes_datos.txt` y validación de integridad referencial antes de eliminar registros.
4. **Excepciones personalizadas:** Se añadieron `ValorFueraDeRangoError`, `RegistroDuplicadoError` y `RegistroNoEncontradoError` en `excepciones.py` para distinguir claramente las reglas de negocio en las validaciones de la interfaz.
5. **Clase de interfaz gráfica (`InterfazTaller`):** Se integró `InterfazTaller(tk.Tk)` en `interfaz.py` como capa visual conectada a `GestorBaseDatos` y a las clases del modelo.

---

## 4. Bitácora de cambios

| Cambio realizado | Clase, módulo o archivo afectado | Motivo | ¿Se reflejó en el UML? |
| :--- | :--- | :--- | :--- |
| Modularización de clases de dominio y excepciones personalizadas | `persona.py`, `dispositivo.py`, `orden_servicio.py`, `excepciones.py` | Separar responsabilidades y eliminar código duplicado | Sí |
| Soporte polimórfico completo de `Computadora` (`ram`) y `DispositivoMovil` (`imei`) en serialización | `dispositivo.py`, `orden_servicio.py` (`toDict()`, `desdeDict()`) | Preservar el tipo exacto y atributos específicos al reconstruir desde texto o SQLite | Sí |
| Desglose de costos (`costoComponentes`, `costoManoObra`, `costoTotal`) y estados (`ESTADOS_VALIDOS`) | `orden_servicio.py` (`OrdenServicio`) | Permitir cálculo en tiempo real y generación de tickets en la GUI | Sí |
| Implementación de `GestorBaseDatos` con SQLite (`catalogos_sgrt.db`) e integridad referencial | `persistencia.py` (`GestorBaseDatos`, `GestorArchivos`) | Persistir catálogos y órdenes evitando borrar clientes o técnicos con órdenes activas | Sí |
| Creación de interfaz gráfica completa con Tkinter, `Treeview`, pestañas, `messagebox` y logo | `interfaz.py` (`InterfazTaller`), `logo_sgrt.png` | Cubrir la administración visual CRUD de órdenes, clientes, técnicos y bitácora | Sí |
| Conversión de `main.py` a lanzador de la GUI y actualización de `pruebas.py` | `main.py`, `pruebas.py` | Ejecutar la aplicación desde un único punto de entrada y validar 12 casos de prueba | Sí |

---

## 5. Código y aplicación de principios POO
- **Herencia y `super().__init__()`:** `Cliente` y `Tecnico` heredan de `Persona` (`persona.py`); `Computadora` y `DispositivoMovil` heredan de `Dispositivo` (`dispositivo.py`), invocando `super().__init__(...)`.
- **Encapsulamiento:** Todos los atributos sensibles utilizan prefijo `_` (`_nombre`, `_telefono`, `_ram`, `_imei`, `_costoComponentes`, `_costoManoObra`, `_costoTotal`, `_folio`, `_estado`) protegidos mediante `@property` y setters con validación estricta.
- **Polimorfismo:** Sobrescritura de `__str__()` y `toDict()` en todas las clases base e hijas para adaptar la salida según el tipo concreto de persona o dispositivo.
- **Nomenclatura:** Uso uniforme de `camelCase` para métodos, atributos y variables, con visibilidad privada (`-`) en métodos auxiliares (`_abrirConexion`, `_sincronizarTxt`, `_filaAOrden`, `_validarMonto`).

---

## 6. Interfaz gráfica
*(Ejecuta `python3 main.py` y agrega capturas legibles con su pie explicativo):*
1. **Ventana principal y pestaña de Órdenes de Servicio:** Logo `logo_sgrt.png` visible en el encabezado, formulario de captura, botones CRUD, cálculo de total, resumen de ticket y listado `Treeview`.
2. **Pestaña Catálogo de Clientes y Catálogo de Técnicos:** Formularios CRUD y sincronización inmediata con los `Combobox` de órdenes.
3. **Pestaña Bitácora de Errores:** Visor en tiempo real de `log_errores.txt`.

---

## 7. Manejo de excepciones y validaciones
- **Campos vacíos:** Validados en setters y formularios; registran `ValueError` en `log_errores.txt` y muestran `messagebox.showwarning`.
- **Texto en lugar de número:** Al ingresar texto en RAM o montos, se captura `ValueError`, se registra en el log y se alerta al usuario con `messagebox`.
- **Valores fuera de rango:** Costos negativos o mayores al límite (`0..500,000`), RAM fuera de `1..1024`, IMEI distinto a 15 dígitos o teléfono fuera de `8..15` dígitos lanzan `ValorFueraDeRangoError`.
- **Registros duplicados, inexistentes o con dependencias:** `GestorBaseDatos` lanza `RegistroDuplicadoError` (ej. folio o nombre repetido), `RegistroNoEncontradoError` (ej. búsqueda sin coincidencias) y `ValueError` al intentar eliminar un cliente o técnico con órdenes asociadas, mostrando `messagebox.showerror`.
- **Archivos:** `GestorArchivos` captura `FileNotFoundError`, `PermissionError` y `json.JSONDecodeError`.

*(Insertar captura de `log_errores.txt` y captura de `messagebox` en pantalla).*

---

## 8. Pruebas realizadas (`pruebas.py`)
Ejecución verificada mediante `python3 pruebas.py` (12 de 12 pruebas aprobadas):

| N.º | Funcionalidad probada | Datos de entrada | Resultado esperado | Resultado obtenido | ¿Pasó? | Captura |
| :---: | :--- | :--- | :--- | :--- | :---: | :--- |
| 1 | Alta de orden (Computadora) y cálculo | Folio `ORD-201`, HP Pavilion 15, RAM `16`, Refacciones `800`, Mano de obra `1200` | Registro guardado y total `$2000.00` | Orden guardada con total `$2000.00` | Sí | *(Agregar)* |
| 2 | Alta de orden (DispositivoMovil) y polimorfismo | Folio `ORD-202`, Samsung Galaxy S23, IMEI `123456789012345`, Refacciones `500`, Mano de obra `900` | Registro con etiqueta `[Móvil]`, IMEI visible y total `$1400.00` | `[Móvil]`, IMEI y total verificados en `__str__()` | Sí | *(Agregar)* |
| 3 | Consulta por folio y cliente | Criterio `"ORD-100"` y `"Santiago"` | Retorna órdenes coincidentes | Coincidencias recuperadas correctamente | Sí | *(Agregar)* |
| 4 | Modificación de orden y recálculo | `ORD-100`: Refacciones `1800`, Mano de obra `1200`, Estado `Entregado` | Total actualizado a `$3000.00` y estado `Entregado` | Actualización persistida y verificada | Sí | *(Agregar)* |
| 5 | Baja de orden e integridad referencial | Intentar borrar cliente con `ORD-100` activa; luego borrar `ORD-100` y el cliente | Bloquea borrado con orden activa; tras borrar orden, permite eliminar | Integridad referencial y baja verificadas | Sí | *(Agregar)* |
| 6 | Persistencia al reabrir aplicación | Alta de cliente `Carlos Sandoval`, reinicio de `GestorBaseDatos` | Los registros permanecen en SQLite y `ordenes_datos.txt` | Cliente y órdenes intactos al reabrir | Sí | *(Agregar)* |
| 7 | Error: campos vacíos | Cliente con nombre `""` | Lanza `ValueError` | `ValueError` capturado correctamente | Sí | *(Agregar)* |
| 8 | Error: texto en lugar de número | Computadora con RAM `"dieciseis"` | Lanza `ValueError` | `ValueError` capturado correctamente | Sí | *(Agregar)* |
| 9 | Error: valor fuera de rango | `costoTotal = -50.0` y RAM `4096` | Lanza `ValorFueraDeRangoError` | `ValorFueraDeRangoError` capturado | Sí | *(Agregar)* |
| 10 | Error: registro duplicado | Registrar folio existente `ORD-100` | Lanza `RegistroDuplicadoError` | `RegistroDuplicadoError` capturado | Sí | *(Agregar)* |
| 11 | Error: registro inexistente | Buscar o eliminar folio `ORD-999` | Lanza `RegistroNoEncontradoError` | `RegistroNoEncontradoError` capturado | Sí | *(Agregar)* |
| 12 | Bitácora de errores | `registrarError("ValueError: Prueba unitaria de bitácora")` | Se guarda línea con fecha, hora y mensaje | Línea escrita y leída desde `log_errores.txt` | Sí | *(Agregar)* |

---

## 9. Errores encontrados y cómo se resolvieron
1. **Desincronización de importaciones y métodos en la suite de pruebas (`pruebas.py`):**
   - *Problema:* Tras modularizar las clases en `persona.py`, `dispositivo.py`, `orden_servicio.py` y `excepciones.py`, el archivo `pruebas.py` seguía importando un módulo antiguo y llamando a `leerBitacora()` en lugar de `leerLog()`.
   - *Solución:* Se actualizaron las importaciones y llamadas en `pruebas.py` para usar los módulos reales, `leerLog()` y `GestorArchivos.cargarOrdenes()`, logrando ejecutar los 12 casos de prueba sin errores.
2. **Integridad referencial al eliminar clientes o técnicos con órdenes activas (`persistencia.py`):**
   - *Problema:* Al borrar un cliente o técnico desde su catálogo mientras tenía órdenes registradas, la tabla `ordenes` conservaba referencias huérfanas que en la interfaz aparentaban reasignarse al primer elemento del `Combobox`.
   - *Solución:* Se agregó validación previa con `SELECT COUNT(*)` en `eliminarCliente()` y `eliminarTecnico()` para lanzar `ValueError` cuando existen órdenes vinculadas, además de actualizar en cascada los datos de contacto si el registro se modifica.
3. **Cierre seguro de conexiones SQLite (`persistencia.py`):**
   - *Problema:* Las consultas repetidas podían dejar conexiones abiertas ante excepciones de integridad o búsqueda.
   - *Solución:* Se encapsuló cada operación de `GestorBaseDatos` en bloques `try / except / finally` garantizando `conexion.close()` en todos los escenarios.

---

## 10. Repositorio en GitHub
- **URL del repositorio:** https://github.com/luis007alv/Proyecto-lenguaje-orientado-a-objetos
- **Colaboradora invitada:** `amkaguilar@gmail.com` *(Verificar en Settings → Collaborators → Add people en GitHub).*

---

## 11. Conclusiones
- Se integró exitosamente una interfaz gráfica completa en Tkinter (`InterfazTaller`) con los modelos POO, persistencia dual (SQLite + JSON en texto), integridad referencial y manejo robusto de excepciones con `messagebox` y bitácora en `log_errores.txt`.
- Como mejora futura se plantea generar recibos imprimibles en PDF por orden y añadir filtros por rango de fechas o técnico asignado.
