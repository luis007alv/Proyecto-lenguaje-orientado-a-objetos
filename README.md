# Sistema de Gestión de Reparaciones Tecnológicas (SGRT)

Proyecto final de **Lenguaje Orientado a Objetos (Python)** — Universidad Anáhuac Querétaro.

## Estructura del proyecto

- [`main.py`](main.py): Punto de entrada único que inicia la aplicación gráfica (`AplicacionSGRT`).
- [`modelos.py`](modelos.py): Modelos del negocio (`Persona`, `Cliente`, `Tecnico`, `Dispositivo`, `Computadora`, `DispositivoMovil`, `OrdenServicio`) y excepciones personalizadas (`ValorFueraDeRangoError`, `RegistroDuplicadoError`, `RegistroNoEncontradoError`).
- [`persistencia.py`](persistencia.py): Persistencia en base de datos SQLite (`catalogos_sgrt.db` vía `GestorBaseDatos`), respaldo JSON en texto (`ordenes_datos.txt` vía `GestorArchivos`) y bitácora de errores (`log_errores.txt` vía `registrarError`).
- [`interfaz.py`](interfaz.py): Interfaz gráfica completa en `Tkinter` / `ttk` (`AplicacionSGRT`) con logo del negocio (`logo_sgrt.png`), pestañas para Órdenes de Servicio, Catálogo de Clientes, Catálogo de Técnicos y visor de Bitácora de Errores.
- [`pruebas.py`](pruebas.py): Suite de 12 pruebas unitarias e integración (CRUD, persistencia, cálculos y casos de error).
- [`uml_actualizado.svg`](uml_actualizado.svg): Diagrama de clases UML actualizado que refleja las clases de dominio, persistencia, excepciones e interfaz gráfica.

## Ejecución

### Iniciar la aplicación gráfica
```bash
python3 main.py
```

### Ejecutar pruebas automatizadas
```bash
python3 pruebas.py
```
