from django.contrib import admin

# Register your models here.
from venta.models import Venta, DetalleVenta



@admin.register(DetalleVenta)
class DetalleVentaAdmin(admin.ModelAdmin):
    list_display = ('fecha','venta','producto','cantidad','precio_unitario','total')
    list_filter = ('fecha','venta','producto',)
    exclude =('precio',)
    readonly_fields =  ('fecha','venta','producto','cantidad','precio_unitario','total',)

    def precio_unitario(self, obj):
        return "💲{:,.2f}".format(obj.precio)

    def total(self, obj):
        return "💲{:,.2f}".format(obj.get_total)


@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ('codigo','fecha','vendedor','cliente','total_factura','ESTADO')
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
    
    
    
    def total_factura(self, obj):
        if obj.total is not None:
            return "💲{:,.2f}".format(obj.total)
        else:
            return "N/A"
        

