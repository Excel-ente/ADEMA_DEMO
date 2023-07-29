from datetime import datetime


class CompraRepository:
    @staticmethod
    def pagar(compra):
        compra.fecha = datetime.now()
        compra.total = compra.get_cart_total

    @staticmethod
    def facturar(compra, nombre, nit):
        compra.nombre_factura = nombre
        compra.nit = nit

    @staticmethod
    def cancelar(compra, motivo):
        compra.razon_cancelacion = motivo

    @staticmethod
    def anular(compra, motivo):
        compra.razon_cancelacion = motivo

    @staticmethod
    def finalizar(compra):
        pass


