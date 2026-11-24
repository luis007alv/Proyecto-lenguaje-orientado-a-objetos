"""Suite de pruebas unitarias e integración para el proyecto SGRT (12 casos)."""

import tempfile
import unittest
from pathlib import Path

from dispositivo import Computadora, DispositivoMovil
from excepciones import (
    RegistroDuplicadoError,
    RegistroNoEncontradoError,
    ValorFueraDeRangoError,
)
from orden_servicio import OrdenServicio
import persistencia
from persistencia import GestorArchivos, GestorBaseDatos, leerLog, registrarError
from persona import Cliente, Tecnico


class PruebasSistemaSGRT(unittest.TestCase):
    """Valida modelos POO, persistencia SQLite/TXT, cálculos, integridad y excepciones."""

    def setUp(self):
        self.tempDir = tempfile.TemporaryDirectory()
        self.rutaTemp = Path(self.tempDir.name)
        self.rutaBd = self.rutaTemp / "test_catalogos.db"
        self.rutaTxt = self.rutaTemp / "test_ordenes.txt"
        self.rutaLog = self.rutaTemp / "test_log.txt"

        self.logOriginal = persistencia.rutaLog
        persistencia.rutaLog = self.rutaLog
        self.gestor = GestorBaseDatos(self.rutaBd, self.rutaTxt)

    def tearDown(self):
        persistencia.rutaLog = self.logOriginal
        self.tempDir.cleanup()

    def test01AltaOrdenComputadora(self):
        """Caso 1 (Alta): Registrar una nueva orden con Computadora y verificar cálculo."""
        cliente = Cliente("María López", "4421234567", "Calle Reforma 10")
        tecnico = Tecnico("Samuel Isaza", "4429998877", "Microelectrónica")
        equipo = Computadora("HP", "Pavilion 15", "No enciende", "16")
        orden = OrdenServicio(
            "ORD-201",
            cliente,
            tecnico,
            equipo,
            costoComponentes="800",
            costoManoObra="1200",
        )
        orden.calcularCosto()
        self.gestor.registrarOrden(orden)

        encontradas = self.gestor.buscarOrdenes("ORD-201")
        self.assertEqual(len(encontradas), 1)
        self.assertEqual(encontradas[0].costoTotal, 2000.0)

    def test02AltaOrdenDispositivoMovilYPolimorfismo(self):
        """Caso 2 (Alta + Polimorfismo): Registrar orden con DispositivoMovil."""
        cliente = Cliente("Andrés Martínez", "4429876543", "Álamos 88")
        tecnico = Tecnico("Valeria Domínguez", "4425551122", "Dispositivos Móviles")
        movil = DispositivoMovil("Samsung", "Galaxy S23", "Batería inflada", "123456789012345")
        orden = OrdenServicio(
            "ORD-202",
            cliente,
            tecnico,
            movil,
            costoComponentes=500,
            costoManoObra=900,
        )
        orden.calcularCosto()
        self.gestor.registrarOrden(orden)

        self.assertIn("[Móvil]", str(orden))
        self.assertIn("123456789012345", str(orden))
        self.assertEqual(orden.costoTotal, 1400.0)

    def test03ConsultaPorFolioYCliente(self):
        """Caso 3 (Consulta): Buscar órdenes existentes por folio y nombre de cliente."""
        resultados = self.gestor.buscarOrdenes("ORD-100")
        self.assertEqual(resultados[0].folio, "ORD-100")

        resultadosCliente = self.gestor.buscarOrdenes("Santiago")
        self.assertGreaterEqual(len(resultadosCliente), 1)

    def test04ModificacionOrdenYCalculo(self):
        """Caso 4 (Modificación + Cálculo): Actualizar costos y estado de una orden."""
        orden = self.gestor.buscarOrdenes("ORD-100")[0]
        orden.costoComponentes = 1800
        orden.costoManoObra = 1200
        orden.cambiarEstado("Entregado")
        orden.calcularCosto()
        self.gestor.modificarOrden(orden)

        actualizada = self.gestor.buscarOrdenes("ORD-100")[0]
        self.assertEqual(actualizada.costoTotal, 3000.0)
        self.assertEqual(actualizada.estado, "Entregado")

    def test05BajaOrdenYIntegridadCatalogos(self):
        """Caso 5 (Baja + Integridad): Bloquear borrado de cliente con orden y eliminar orden."""
        clientes = self.gestor.obtenerClientes()
        idSantiago = next(idC for idC, c in clientes if c.nombre == "Santiago Alarcón")

        # No debe permitir borrar un cliente con orden activa
        with self.assertRaises(ValueError):
            self.gestor.eliminarCliente(idSantiago)

        # Tras eliminar su orden, ya debe permitir eliminar el cliente
        self.gestor.eliminarOrden("ORD-100")
        with self.assertRaises(RegistroNoEncontradoError):
            self.gestor.buscarOrdenes("ORD-100")

        self.gestor.eliminarCliente(idSantiago)
        nombresRestantes = [c.nombre for _, c in self.gestor.obtenerClientes()]
        self.assertNotIn("Santiago Alarcón", nombresRestantes)

    def test06PersistenciaAlReabrir(self):
        """Caso 6 (Persistencia): Reinstanciar GestorBaseDatos y validar datos en SQLite y TXT."""
        cliente = Cliente("Carlos Sandoval", "4424445566", "Milenio III 20")
        self.gestor.registrarCliente(cliente)

        nuevoGestor = GestorBaseDatos(self.rutaBd, self.rutaTxt)
        nombresClientes = [c.nombre for _, c in nuevoGestor.obtenerClientes()]
        self.assertIn("Carlos Sandoval", nombresClientes)

        ordenesTxt = GestorArchivos.cargarOrdenes(self.rutaTxt)
        self.assertTrue(any(o.folio == "ORD-100" for o in ordenesTxt))

    def test07ErrorCamposVacios(self):
        """Caso 7 (Error): Validar campo vacío en Cliente."""
        with self.assertRaises(ValueError):
            Cliente("", "4421112233", "Centro")

    def test08ErrorTextoEnLugarDeNumero(self):
        """Caso 8 (Error): Validar texto no numérico en memoria RAM o costos."""
        with self.assertRaises(ValueError):
            Computadora("Asus", "ROG", "Falla RAM", "dieciseis")

    def test09ErrorValorFueraDeRango(self):
        """Caso 9 (Error): Validar costo negativo y RAM fuera de rango."""
        orden = self.gestor.buscarOrdenes("ORD-100")[0]
        with self.assertRaises(ValorFueraDeRangoError):
            orden.costoTotal = -50.0
        with self.assertRaises(ValorFueraDeRangoError):
            Computadora("Lenovo", "ThinkPad", "Lenta", 4096)

    def test10ErrorRegistroDuplicado(self):
        """Caso 10 (Error): Impedir registrar un folio duplicado."""
        ordenExistente = self.gestor.buscarOrdenes("ORD-100")[0]
        with self.assertRaises(RegistroDuplicadoError):
            self.gestor.registrarOrden(ordenExistente)

    def test11ErrorRegistroInexistente(self):
        """Caso 11 (Error): Consultar o eliminar un folio inexistente."""
        with self.assertRaises(RegistroNoEncontradoError):
            self.gestor.buscarOrdenes("ORD-999")
        with self.assertRaises(RegistroNoEncontradoError):
            self.gestor.eliminarOrden("ORD-999")

    def test12RegistroBitacoraErrores(self):
        """Caso 12 (Bitácora): Verificar escritura con fecha y hora en archivo log."""
        registrarError("ValueError: Prueba unitaria de bitácora", self.rutaLog)
        contenido = leerLog(self.rutaLog)
        self.assertIn("ERROR | ValueError: Prueba unitaria de bitácora", contenido)


if __name__ == "__main__":
    unittest.main(verbosity=2)
