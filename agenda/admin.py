from django.contrib import admin
from .models import Cliente,Gasto,TipoGasto,Retiro,Asignacion



@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombre','telefono','direccion',)

@admin.register(Asignacion)
class AsignacionAdmin(admin.ModelAdmin):
    list_display = ('usuario','caja',)
        
@admin.register(Retiro)
class RetiroAdmin(admin.ModelAdmin):
    list_display = ('fecha','descripcion','total')

@admin.register(Gasto)
class GastoAdmin(admin.ModelAdmin):
    list_display = ('categoria','descripcion','total')

@admin.register(TipoGasto)
class TipoGastoAdmin(admin.ModelAdmin):
    list_display = ('descripcion',)