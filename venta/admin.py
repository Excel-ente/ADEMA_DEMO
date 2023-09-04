from django.contrib import admin

# Register your models here.
from venta.models import Venta, DetalleVenta
from import_export.admin import ImportExportModelAdmin

@admin.register(DetalleVenta)
class DetalleVentaAdmin(ImportExportModelAdmin):
    list_display = ('fecha','venta','producto','cantidad','moneda','precio_unitario','total')
    list_filter = ('fecha','venta','producto',)
    exclude =('precio',)
    readonly_fields =  ('fecha','venta','producto','cantidad','moneda','precio_unitario','total',)

    def precio_unitario(self, obj):
        return "💲{:,.2f}".format(obj.precio)

    def dolar_unitario(self, obj):
        return "💲{:,.2f}".format(obj.precio_usd)

    def boliviano_unitario(self, obj):
        return "💲{:,.2f}".format(obj.precio_bs)


    def total(self, obj):
        return "💲{:,.2f}".format(obj.get_total)


@admin.register(Venta)
class VentaAdmin(ImportExportModelAdmin):
    list_display = ('codigo','fecha','cajero','cliente','total_factura','ESTADO')
    exclude = ('nit','nombre_factura','total')
   # readonly_fields =  ('codigo','cliente','fecha','total_factura','razon_cancelacion','estado')
   # list_display_links = ('codigo','fecha','cliente',)
    
    def ESTADO(self,obj):

        if obj.estado == 0:
            msj = f'🟡creada'
        elif obj.estado == 1:
            msj = f'💲pagada'
        elif obj.estado == 2:
            msj = f'💳pagada'
        elif obj.estado == 3:
            msj = f'🟢finalizada'
        elif obj.estado == 4:
            msj = f'🔴cancelada'
        else:
            msj = f'🔴anulada'

        return msj
    
    def cajero(self, obj):

        return obj.nombre_factura

    
    def total_factura(self, obj):
        if obj.total is not None:
            return "💲{:,.2f}".format(obj.total)
        else:
            return "N/A"
        

