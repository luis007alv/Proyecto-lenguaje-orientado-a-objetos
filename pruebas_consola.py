"""Script auxiliar para probar por consola las clases, persistencia y errores."""

from pathlib import Path

from dispositivo import Computadora, DispositivoMovil
from excepciones import (
    RegistroDuplicadoError,
    RegistroNoEncontradoError,
    ValorFueraDeRangoError,
)
from orden_servicio import OrdenServicio
from persistencia import GestorArchivos, GestorBaseDatos, registrarError
from persona import Cliente, Tecnico


def main():
    print("=== PRUEBAS DEL SISTEMA SGRT ===\n")

    # 1. Creación de objetos de todas las clases (incluidas hijas)
    cliente1 = Cliente("Santiago Alarcón", "4421112233", "Centro Histórico")
    cliente2 = Cliente("Sofía Hernández", "4423456789", "Juriquilla 45")
    tecnico1 = Tecnico("Luis Álvarez", "4429998877", "Microelectrónica")
    tecnico2 = Tecnico("Valeria Domínguez", "4425551122", "Dispositivos Móviles")

    pc1 = Computadora("Dell", "XPS 13", "Pantalla rota", 16)
    movil1 = DispositivoMovil("Samsung", "Galaxy S23", "Batería inflada", "356789012345678")

    orden1 = OrdenServicio("ORD-200", cliente1, tecnico1, pc1, 1500.0, 1000.0, "Reparación")
    orden2 = OrdenServicio("ORD-201", cliente2, tecnico2, movil1, 850.0, 500.0, "En diagnóstico")

    # 2. Métodos del negocio
    orden1.calcularCosto()
    orden2.calcularCosto()
    print(orden1.generarResumen())
    print(orden2.generarResumen())

    # 3. Persistencia en archivo de texto y reconstrucción (incluyendo DispositivoMovil)
    GestorArchivos.guardarOrdenes([orden1, orden2])
    reconstruidas = GestorArchivos.cargarOrdenes()
    print(f"\nÓrdenes reconstruidas desde TXT: {len(reconstruidas)}")
    for o in reconstruidas:
        print(
            f" -> {o.folio} | {o.cliente.nombre} | {o.tecnico.nombre} | "
            f"{type(o.dispositivo).__name__}: {o.dispositivo} | Estado: {o.estado} | Total: ${o.costoTotal}"
        )

    # 4. Provocar errores reales para log_errores.txt
    rutaInexistente = Path(__file__).resolve().parent / "temporal_inexistente.txt"
    if rutaInexistente.exists():
        rutaInexistente.unlink()
    GestorArchivos.cargarOrdenes(rutaInexistente)
    if rutaInexistente.exists():
        rutaInexistente.unlink()

    try:
        orden1.costoTotal = -100.0
    except ValorFueraDeRangoError as e:
        registrarError(f"ValorFueraDeRangoError: {e}")

    try:
        Computadora("HP", "Pavilion", "No enciende", "dieciseis")
    except ValueError as e:
        registrarError(f"ValueError: {e}")

    gestorBd = GestorBaseDatos()
    try:
        gestorBd.buscarOrdenes("ORD-999")
    except RegistroNoEncontradoError as e:
        pass

    try:
        gestorBd.registrarCliente(cliente1)
    except RegistroDuplicadoError as e:
        pass

    print("\nPruebas completadas. Revisa 'ordenes_datos.txt', 'catalogos_sgrt.db' y 'log_errores.txt'.")


if __name__ == "__main__":
    main()
