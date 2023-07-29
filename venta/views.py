import datetime
import time
import calendar

from django.db.models import Sum, Q,F, ExpressionWrapper, DecimalField
from datetime import date, datetime, time,timedelta
from django.http import HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404
from decimal import Decimal
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.views.generic import ListView, UpdateView, DetailView
from django.utils.decorators import method_decorator


from venta.forms import VentaForm, VentaFacturaForm

from venta.models import Venta, DetalleVenta
from compra.models import Compra
from producto.models import Producto
from agenda.models import Cliente
from django.utils import timezone



@method_decorator(login_required, name='dispatch')
class VentaList(ListView):
    model = Venta
    queryset = Venta.objects.all().order_by('-fecha')
    template_name = 'ruta_del_template/venta_list.html'  # Reemplaza 'ruta_del_template' con la ruta a tu plantilla

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Obtener el total de ventas del día actual
        total_hoy = Venta.objects.filter(
            Q(fecha__date=timezone.now().date()) & (Q(estado=1) | Q(estado=2) | Q(estado=3))
        ).aggregate(Sum('total'))['total__sum'] or 0

        context['total_hoy'] = total_hoy

        # Obtener el total de ventas del mes actual
        mes_actual = timezone.now().month

        total_mes = Venta.objects.filter(
            Q(fecha__month=mes_actual) &  (Q(estado=1) | Q(estado=2) | Q(estado=3))
        ).aggregate(Sum('total'))['total__sum'] or 0
        
        context['total_mes'] = total_mes

        # Obtener el nombre del mes actual
        mes = calendar.month_name[mes_actual]
        context['mes'] = mes

        # Agregar cualquier otro contexto adicional que necesites aquí
        return context


class VentaDetail(DetailView):
    model = Venta


class VentaFactura(UpdateView):
    """
    Facturación de la venta, la venta no puede ser facturada si no se encuentra en estado pagada
    """
    model = Venta
    form_class = VentaFacturaForm
    template_name_suffix = '_facturar_form'
    success_url = reverse_lazy('venta:carrito')

    def dispatch(self, request, *args, **kwargs):
        # La venta no puede entrar a esta vista si se encuentra en estado pagada
        venta = Venta.objects.get(id=self.kwargs['pk'])

        if not venta.estado == venta.ESTADO_PAGADA:
            return HttpResponseBadRequest()

        return super(VentaFactura, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        venta = get_object_or_404(Venta, id=self.kwargs['pk'])
        redirect_url = super(VentaFactura, self).form_valid(form)
        cliente = form.cleaned_data['cliente']
        vendedor = form.cleaned_data['vendedor']
        venta.cliente = cliente
        venta.vendedor = vendedor
        venta.save()
        return redirect_url


class VentaUpdate(UpdateView):
    """
    Actualización de la venta (cambiar de estado a anulada o cancelada), ningún otro cambio puede ser actualizado
    """
    model = Venta
    form_class = VentaForm
    template_name_suffix = '_update_form'
    success_url = reverse_lazy('venta:ventas')

    def dispatch(self, request, *args, **kwargs):
        # La venta no puede entrar a esta vista si se encuentra en estado cancelada o anulada
        venta = Venta.objects.get(id=self.kwargs['pk'])
        if venta.estado == venta.ESTADO_ANULADA or venta.estado == venta.ESTADO_CANCELADA:
            return HttpResponseBadRequest()

        return super(VentaUpdate, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(VentaUpdate, self).get_context_data(**kwargs)
        venta = get_object_or_404(Venta, id=self.kwargs['pk'])
        context['venta'] = venta
        return context

    def form_valid(self, form):
        venta = get_object_or_404(Venta, id=self.kwargs['pk'])
        redirect_url = super(VentaUpdate, self).form_valid(form)
        motivo = form.cleaned_data['razon_cancelacion']

        if venta.estado == venta.ESTADO_CREADA:
            venta.cancelar(motivo)
            obtener_venta_actual()
        else:
            venta.anular(motivo)

        devolver_productos_a_stock(venta.id)
        venta.save()
        return redirect_url

def login(request):

    context = {'hola': 'hola', }
    return render(request, 'login.html', context)

@login_required(login_url='/admin/login/')
def dashboard(request):

    lista_ventas = DetalleVenta.objects.all().order_by('-id')


    # Obtener el total de ventas del día actual
    total_hoy = Venta.objects.filter(
        Q(fecha__date=timezone.now().date()) & (Q(estado=1) | Q(estado=2) | Q(estado=3))
    ).aggregate(Sum('total'))['total__sum'] or 0



    # Obtener el total de ventas del mes actual
    mes_actual = timezone.now().month

    total_mes = Venta.objects.filter(
        Q(fecha__month=mes_actual) &  (Q(estado=1) | Q(estado=2) | Q(estado=3))
    ).aggregate(Sum('total'))['total__sum'] or 0
    
    # Obtener el nombre del mes actual
    mes = calendar.month_name[mes_actual]

    context = {
        'lista_ventas': lista_ventas, 
        'mes':mes,
        'total_hoy':total_hoy,
        'total_mes':total_mes,
        }
    return render(request, 'home.html', context)



@login_required(login_url='/admin/login/')
def compra(request):

    compra_list = Compra.objects.all().order_by('-fecha')

    context = {'compra_list': compra_list}

    return render(request, 'compra_list.html', context)


@login_required(login_url='/admin/login/')
def product_list(request):
    """
    Vista de lista de productos, en esta vista se encuentra también la lógica de añadir producto al carrito
    :param request:
    :return:
    """
    venta = obtener_venta_actual()
    data = {}
    lista_productos = Producto.objects.order_by('nombre')

    if request.method == 'POST':
        if 'btnsearch' in request.POST:
            search = request.POST['search']
            if not search == '':
                lista_productos = Producto.objects.filter(
                    Q(nombre__contains=search) | Q(categoria__nombre__contains=search)).distinct()
            else:
                lista_productos = Producto.objects.order_by('nombre')
            if not lista_productos:
                data['status'] = 'Sin resultados'
        else:
            producto = get_object_or_404(Producto, id=request.POST['id_producto'])
            cantidad = Decimal(request.POST['cantidad'])

            data['status'] = agregar_producto_a_carrito(venta, cantidad, producto)

    context = {'producto_list': lista_productos, 'data': data, 'venta': venta}

    return render(request, 'venta/producto_list.html', context)

@login_required(login_url='/admin/login/')
def carrito(request):
    """
    Vista de carrito, en esta vista se muestran los productos añadidos a la venta actual además de podes cambiar de estado
    a la venta y remover productos del 'carrito'

    :param request:
    :return:
    """

    venta = obtener_venta_actual()
    lista_detalle = DetalleVenta.objects.filter(venta=venta)
    lista_clientes = Cliente.objects.all()
    data = {}
    # Si es post es para eliminar el detalle de la venta
    if request.method == 'POST':
        if 'pagar' in request.POST:
            venta.pagar()
            venta.save()

        elif 'facturar' in request.POST:
            pass

        elif 'finalizar' in request.POST:
            venta.finalizar()
            venta.save()
            new_venta = obtener_venta_actual()
            lista_detalle = DetalleVenta.objects.filter(venta=new_venta)
            return render(request, 'venta/carrito.html',
                          {'lista_detalle': lista_detalle, 'venta': new_venta, 'data': data})

        elif request.POST['detalle_id']:
            nombre_producto_eliminado = eliminar_de_carrito(request.POST['detalle_id'])
            data['eliminado'] = 'Se ha eliminado del carrito: ' + nombre_producto_eliminado + ' de manera exitosa'
       
    return render(request, 'venta/carrito.html',
                  {'lista_detalle': lista_detalle, 'venta': venta, 'data': data,'lista_clientes':lista_clientes,})


@login_required(login_url='/admin/login/')
def balance(request):


    ventas = Venta.objects.all().order_by('-fecha')
    compras = Compra.objects.all().order_by('-fecha')
    productos = Producto.objects.all()

    # Obtener la fecha actual sin la hora
    fecha_actual = date.today()
    hora_inicio_dia = datetime.combine(fecha_actual, time.min)
    hora_fin_dia = datetime.combine(fecha_actual, time.max)

    valuacion_inventario = Producto.objects.annotate(
        valuacion=ExpressionWrapper(F('en_stock') * F('costo'), output_field=DecimalField())
    ).aggregate(total_valuacion=Sum('valuacion'))['total_valuacion']

    # Obtener el total de ventas del día actual desde las 00:00 hasta las 23:59
    ventas_hoy = Venta.objects.filter(
        fecha__range=(hora_inicio_dia, hora_fin_dia)
    ).aggregate(ventas_hoy=Sum('total'))['ventas_hoy']

    # Obtener el total de ventas del mes actual
    ventas_mes_actual = Venta.objects.filter(
        fecha__year=fecha_actual.year, fecha__month=fecha_actual.month
    ).aggregate(total_ventas_mes_actual=Sum('total'))['total_ventas_mes_actual']

    # Obtener el total de compras del mes actual (asumiendo que también tienes un modelo 'Compra' similar a 'Venta')
    compras_mes_actual = Compra.objects.filter(
        fecha__year=fecha_actual.year, fecha__month=fecha_actual.month
    ).aggregate(total_compras_mes_actual=Sum('total'))['total_compras_mes_actual']


    # Obtener el top 10 de productos más vendidos
    top_ventas = DetalleVenta.objects.values('producto__descripcion', 'producto__nombre').annotate(
        total_ventas=Sum('cantidad'), nombre_largo=F('producto__nombre') + ' ' + F('producto__descripcion')
    ).order_by('-total_ventas')[:10]

    fecha_actual = date.today()
        # Obtener la fecha actual menos 30 días
    fecha_30_dias_atras = fecha_actual - timedelta(days=30)

    # Inicializar el diccionario de ventas en los últimos 30 días
    ventas_30_dias = {}
  
    ventas_por_dia = DetalleVenta.objects.filter(fecha__range=(fecha_30_dias_atras, fecha_actual)).values('fecha__day').annotate(
        total_ventas=Sum(ExpressionWrapper(F('cantidad') * F('precio'), output_field=DecimalField()))
    )
    # Llenar el diccionario con las sumatorias de ventas por día
    for venta in ventas_por_dia:
        dia = venta['fecha__day']
        total_ventas = venta['total_ventas'] or 0
        ventas_30_dias[dia] = total_ventas

    context = {
        'ventas': ventas,
        'compras': compras,
        'valuacion_inventario': valuacion_inventario,
        'ventas_hoy': ventas_hoy or 0,
        'ventas_mes_actual': ventas_mes_actual or 0,
        'compras_mes_actual': compras_mes_actual or 0,
        'top_ventas':top_ventas,
        'ventas_30_dias':ventas_30_dias,
        'ventas_por_dia':ventas_por_dia,
  
    }

    return render(request, 'balance.html', context)


def agregar_producto_a_carrito(venta, cantidad, producto):
    """
    En este método se encuentra la lógica de crear un detalle producto por
    el producto que se ha seleccionado para agregar

    :param venta:
    :param cantidad:
    :param producto:
    :return:
    """
    if venta.estado == venta.ESTADO_CREADA:
        detalle_venta = DetalleVenta()
        detalle_venta.venta = venta
        detalle_venta.producto = producto
        detalle_venta.cantidad = cantidad
        detalle_venta.precio = producto.precio
        detalle_venta.save()

        producto.en_stock = producto.en_stock - cantidad
        producto.save()

        return producto.nombre.capitalize() + ' se ha agregado al carrito de manera exitosa.'
    else:
        return 'False'


def eliminar_de_carrito(detalle_id):
    """
    En este método se encuentra la lógica de eliminar el DetalleProducto del 'Carrito'

    :param detalle_id:
    :return:
    """
    detalle_venta = DetalleVenta.objects.get(id=detalle_id)
    producto = detalle_venta.producto
    producto.en_stock = producto.en_stock + detalle_venta.cantidad
    producto.save()
    detalle_venta.delete()
    return detalle_venta.producto.nombre


def vaciar_carrito(venta_id):
    """
    Método para vaciar por completo 'el carrito' de la venta actual, este método elimina todos los detalleventa que existan
    con la venta actual y devolverá a stock de cada producto los productos retirados de la venta

    Uso actual: Sin uso

    :param venta_id:
    :return:
    """
    venta = get_object_or_404(Venta, venta_id)
    for detalleventa in venta.detalleventa_set.all():
        eliminar_de_carrito(detalleventa.id)


def obtener_venta_actual():
    """
    Método que retorna la venta actual, se pueden seguir realizando acciones en la venta hasta que la venta se encuentre
    en estado cancelada, finalizada o anulada
    :return Venta:
    """
    venta = Venta.objects.filter(estado=Venta.ESTADO_FACTURADA).first()
    if not venta:
        venta = Venta.objects.filter(estado=Venta.ESTADO_PAGADA).first()
    if not venta:
        # Si no existe una venta en estado creado, la creamos
        venta, create = Venta.objects.get_or_create(estado=Venta.ESTADO_CREADA)
        venta.save()

    if not venta.codigo:
        venta.codigo = str(venta.id)
        venta.save()

    return venta


def devolver_productos_a_stock(id_venta):
    # Obtenemos la venta que ha sido anulada/cancelada
    venta = get_object_or_404(Venta, id=id_venta)

    # Obtenemos los detalle venta en esa venta y los iteramos
    for detalleventa in venta.detalleventa_set.all():
        # Aumentamos el stock de los productos que estaban en la venta que ha sido cancelada/anulada
        detalleventa.producto.en_stock = detalleventa.producto.en_stock + detalleventa.cantidad
        detalleventa.producto.save()
