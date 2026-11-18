"""Archivo principal de inicio para el Sistema de Gestión de Reparaciones Tecnológicas."""

from tkinter import messagebox

from interfaz import InterfazTaller
from persistencia import registrarError


def main():
    """Inicia la interfaz gráfica principal del taller."""
    try:
        app = InterfazTaller()
        app.mainloop()
    except Exception as e:
        registrarError(f"{type(e).__name__}: Error al iniciar la aplicación. {e}")
        messagebox.showerror("Error", f"Ocurrió un problema al iniciar el sistema:\n{e}")


if __name__ == "__main__":
    main()
