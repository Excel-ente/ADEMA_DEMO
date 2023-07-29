from django.contrib import admin
from .models import Cliente,Vendedor,Viaje
# Register your models here.
admin.site.register(Cliente)
admin.site.register(Vendedor)


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