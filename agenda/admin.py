from django.contrib import admin
from .models import Cliente,Vendedor,Viaje,Gasto,TipoGasto,Retiro,Asignacion
# Register your models here.
admin.site.register(Cliente)
admin.site.register(Vendedor)

@admin.register(Asignacion)
class AsignacionAdmin(admin.ModelAdmin):
    list_display = ('usuario','caja',)

@admin.register(Viaje)
class ViajeAdmin(admin.ModelAdmin):
    list_display = ('status','chofer','fecha_llegada','costo_viaje')
    exclude = ('estado','fecha_salida')

    def costo_viaje(self, obj):
        return "💲{:,.2f}".format(obj.costo_total_trasnlado)
    
    def status(self, obj):
        if obj.estado == False:
            return "🛻 En viaje"
        else:
            return "🟢 Controlado"
        
@admin.register(Retiro)
class RetiroAdmin(admin.ModelAdmin):
    list_display = ('fecha','descripcion','total')

@admin.register(Gasto)
class GastoAdmin(admin.ModelAdmin):
    list_display = ('categoria','descripcion','total')

@admin.register(TipoGasto)
class TipoGastoAdmin(admin.ModelAdmin):
    list_display = ('descripcion',)