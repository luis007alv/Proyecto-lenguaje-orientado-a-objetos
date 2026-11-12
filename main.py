"""Punto de entrada principal del Sistema de Gestión de Reparaciones Tecnológicas (SGRT)."""

from tkinter import messagebox

from interfaz import AplicacionSGRT
from persistencia import registrarError


def main():
    """Inicializa y ejecuta la interfaz gráfica principal del SGRT."""
    try:
        aplicacion = AplicacionSGRT()
        aplicacion.mainloop()
    except Exception as exc:
        registrarError(f"{type(exc).__name__}: Error crítico al iniciar la aplicación. {exc}")
        messagebox.showerror(
            "Error crítico",
            f"No fue posible iniciar el sistema SGRT:\n{exc}",
        )


if __name__ == "__main__":
    main()
