from django.urls import path
from . import views
from compra.views import *

venta_patterns = ([ 
                      path('', views.product_list, name='product_list'),
                      path('ventas/', views.VentaList.as_view(), name='ventas'),
                      path('compras/', views.compra, name='compra'), 
                      path('balance/', views.balance, name='balance'),   
                      path('ventasPorProducto/', views.dashboard, name='ventasPorProducto'),
                      path('ventas/detail/<int:pk>/', views.VentaDetail.as_view(), name='detail'),
                      path('ventas/anular/<int:pk>/', views.VentaUpdate.as_view(), name='anular'),
                      path('ventas/facturar/<int:pk>/', views.VentaFactura.as_view(), name='facturar'),
                      path('carrito/', views.carrito, name='carrito'),
                  ], 'venta')
