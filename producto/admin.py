from django.contrib import admin

# Register your models here.
from producto.models import Producto, Categoria


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre',)

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('categoria','nombre','descripcion','costo','precio_venta','en_stock')
    list_filter = ('categoria','nombre','descripcion')
    search_fields = ('nombre',)
    list_display_links = ('categoria','nombre',)
    exclude = ('imagen',)
    def precio_venta(self, obj):
        return "💲{:,.2f}".format(obj.precio)    
