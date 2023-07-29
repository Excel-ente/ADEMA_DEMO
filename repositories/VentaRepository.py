from datetime import datetime


class VentaRepository:
    @staticmethod
    def pagar(venta):
        venta.fecha = datetime.now()
        venta.total = venta.get_cart_total

    @staticmethod
    def facturar(venta, vendedor, cliente):
        venta.cliente = cliente
        venta.vendedor = vendedor

    @staticmethod
    def cancelar(venta, motivo):
        venta.razon_cancelacion = motivo

    @staticmethod
    def anular(venta, motivo):
        venta.razon_cancelacion = motivo

    @staticmethod
    def finalizar(venta):
        pass


