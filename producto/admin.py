from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

# Register your models here.
from producto.models import Producto, Categoria


@admin.register(Categoria)
class CategoriaAdmin(ImportExportModelAdmin):
    list_display = ('nombre',)

@admin.register(Producto)
class ProductoAdmin(ImportExportModelAdmin):
    list_display = ('categoria','nombre','descripcion','costo','pesos','dolar','boliviano','en_stock')
    list_filter = ('categoria','nombre','descripcion')
    search_fields = ('nombre',)
    list_display_links = ('categoria','nombre',)
    #exclude = ('imagen',)

    def pesos(self, obj):
        return "💲{:,.2f}".format(obj.precio)    

    def dolar(self, obj):
        return "💲{:,.2f}".format(obj.precio_usd)
        
    def boliviano(self, obj):
        return "💲{:,.2f}".format(obj.precio_bs)    