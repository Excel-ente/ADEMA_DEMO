
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
from django.views import View
from django.views.generic import ListView, UpdateView, DetailView
from django.utils.decorators import method_decorator
from venta.forms import VentaForm, VentaFacturaForm
from venta.models import Venta, DetalleVenta
from agenda.models import Gasto,Retiro
from compra.models import Compra
from producto.models import Producto
from agenda.models import Cliente,Asignacion
from django.core.paginator import Paginator
from django.shortcuts import render
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from reportlab.lib.pagesizes import letter
from pytz import timezone

class PrintTicketPDFView(View):
    def get(self, request, venta_id):
        venta = Venta.objects.get(id=venta_id)
        template_path = 'ticket.html'
        context = {'venta': venta}
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'filename="ticket_venta_{venta_id}.pdf"'
        template = get_template(template_path)
        html = template.render(context)

        pisa_status = pisa.CreatePDF(html, dest=response)

        if pisa_status.err:
            return HttpResponse('Error al generar el PDF', status=500)

        return response
    
def imprimir_ticket(request, venta_id):

    usuario_actual = request.user
    asignacion_usuario = Asignacion.objects.filter(usuario=usuario_actual).first()

    if asignacion_usuario:
        caja_usuario = asignacion_usuario.caja
    else:
        # Maneja el caso en el que el usuario no tenga asignada una caja
        caja_usuario = 'caja_1'  # Puedes definir una caja predeterminada o manejarlo de otra manera


    # Obtén la venta actual
    venta = obtener_venta_actual(caja_usuario)

    # Cargar la plantilla HTML del ticket
    template = get_template('ticket.html')

    # Contexto para la plantilla
    context = {
        'venta': venta,
    }

    # Renderizar la plantilla con el contexto
    rendered_template = template.render(context)

    # Crear un objeto de respuesta HTTP con el tipo MIME adecuado para PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename=ticket_venta_{venta_id}.pdf'

    # Convertir la plantilla HTML a PDF y guardar en el objeto de respuesta
    pisa_status = pisa.CreatePDF(
        rendered_template, dest=response, encoding='utf-8',
        link_callback=fetch_resources,
        pagesize=letter,
    )

    # Si la conversión fue exitosa, enviar el PDF como respuesta; de lo contrario, devolver un error
    if pisa_status.err:
        return HttpResponse('Error al generar el PDF', status=500)

    return response

@method_decorator(login_required, name='dispatch')
class VentaList(ListView):
    model = Venta
    template_name = 'tu_template.html'  # Reemplaza 'tu_template.html' por el nombre de tu plantilla
    context_object_name = 'venta_list'  # Nombre del objeto en el contexto

    def get_queryset(self):
        # Obtener la fecha actual
        fecha_actual = date.today()

        # Filtrar las ventas del día actual por defecto
        queryset = Venta.objects.filter(fecha__date=fecha_actual).order_by('-fecha')

        desde = self.request.GET.get('desde')
        hasta = self.request.GET.get('hasta')

        if desde and hasta:
            # Filtrar las ventas dentro del rango de fechas especificado
            queryset = Venta.objects.filter(
                fecha__date__range=[desde, hasta],  # Utilizar el rango de fechas
                estado__in=[1, 2, 3, 5]  # Filtrar por estados específicos
            ).order_by('-fecha')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        desde = self.request.GET.get('desde')
        hasta = self.request.GET.get('hasta')

        # Obtener la fecha actual
        fecha_actual = date.today()

        # Filtrar las ventas del día actual por defecto
        lista_ventas = DetalleVenta.objects.filter(venta__fecha__date=fecha_actual).order_by('-id')

        # Resto de tu código de context

        context['lista_ventas'] = lista_ventas

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
            obtener_venta_actual(self.caja_usuario)  # Usar la caja del usuario
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

    # Obtener la fecha actual
    fecha_actual = date.today()

    # Filtrar las ventas del día actual por defecto
    lista_ventas = DetalleVenta.objects.filter(venta__fecha__date=fecha_actual).order_by('-id')

    desde = request.GET.get('desde')  # Obtener el valor desde el parámetro GET
    hasta = request.GET.get('hasta')  # Obtener el valor hasta el parámetro GET
    moneda = request.GET.get('moneda')


    if desde and hasta:
        # Filtrar las ventas dentro del rango de fechas especificado
        ventas_filtradas = Venta.objects.filter(
            fecha__date__range=[desde, hasta],  # Utilizar el rango de fechas
            estado__in=[ 2, 3]  # Filtrar por estados específicos
        ).order_by('-fecha')

        if moneda and moneda != "Todas":
            lista_ventas = DetalleVenta.objects.filter(venta__in=ventas_filtradas,moneda=moneda)
        else:
            lista_ventas = DetalleVenta.objects.filter(venta__in=ventas_filtradas)

    else:
        
        ventas_filtradas = Venta.objects.all().order_by('-fecha')
    
    page_size = 50  # Define la cantidad de elementos por página
    paginator = Paginator(lista_ventas, page_size)
    page_number = request.GET.get('page')  # Obtener el número de página de la solicitud GET
    page = paginator.get_page(page_number)  # Obtener la página actual

    # Calcular el total de ventas filtrado por moneda="Pesos"
    total_ars = sum(item.get_total for item in lista_ventas if item.moneda == 'Pesos')
    # Calcular el total de ventas filtrado por moneda="Dolares"
    total_usd = sum(item.get_total for item in lista_ventas if item.moneda == 'Dolares')
    # Calcular el total de ventas filtrado por moneda="Bolivianos"
    total_bs = sum(item.get_total for item in lista_ventas if item.moneda == 'Bolivianos')

    # Obtener la fecha actual en Argentina
    argentina_timezone = timezone('America/Argentina/Buenos_Aires')
    fecha_actual = datetime.now(argentina_timezone)

    # Obtener el mes actual
    mes_actual = fecha_actual.month

    # Obtener el nombre del mes actual
    mes = calendar.month_name[mes_actual]

    context = {
        'lista_ventas': lista_ventas, 
        'page': page,
        'mes':mes,
        'total_ars':total_ars,
        'total_usd':total_usd,
        'total_bs':total_bs,
        }
    return render(request, 'home.html', context)

@login_required(login_url='/admin/login/')
def compra(request):

    compra_list = Compra.objects.all().order_by('fecha')

    context = {'compra_list': compra_list}

    return render(request, 'compra_list.html', context)

@login_required(login_url='/admin/login/')
def product_list(request):
    """
    Vista de lista de productos, en esta vista se encuentra también la lógica de añadir producto al carrito
    :param request:
    :return:
    """

    usuario_actual = request.user
    asignacion_usuario = Asignacion.objects.filter(usuario=usuario_actual).first()

    if asignacion_usuario:
        caja_usuario = asignacion_usuario.caja
    else:
        # Maneja el caso en el que el usuario no tenga asignada una caja
        caja_usuario = 'caja_1'  # Puedes definir una caja predeterminada o manejarlo de otra manera

    venta = obtener_venta_actual(caja_usuario)
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
            moneda = request.POST['moneda']

            data['status'] = agregar_producto_a_carrito(venta, cantidad, producto, moneda)

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

    usuario_actual = request.user
    asignacion_usuario = Asignacion.objects.filter(usuario=usuario_actual).first()

    if asignacion_usuario:
        caja_usuario = asignacion_usuario.caja
    else:
        # Maneja el caso en el que el usuario no tenga asignada una caja
        caja_usuario = 'caja_1'  # Puedes definir una caja predeterminada o manejarlo de otra manera

    venta = obtener_venta_actual(caja_usuario)  # Pasa la caja del usuario a la función obtener_venta_actual()

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
            new_venta = obtener_venta_actual(caja_usuario)
            lista_detalle = DetalleVenta.objects.filter(venta=new_venta)
            return render(request, 'venta/carrito.html',
                          {'lista_detalle': lista_detalle, 'venta': new_venta, 'data': data})
    
        elif 'detalle_id' in request.POST:
            nueva_cantidad = request.POST['nueva_cantidad']
            nuevo_precio = request.POST['nuevo_precio']
            detalle_id = request.POST['detalle_id']
            detalle_venta = DetalleVenta.objects.get(id=detalle_id)
            detalle_venta.cantidad = nueva_cantidad
            detalle_venta.precio = nuevo_precio
            #detalle_venta.total = nuevo_precio * nueva_cantidad
            detalle_venta.save()

        elif 'id_cliente' in request.POST:
            
            selected_cliente_id = request.POST['id_cliente']
            selected_cliente = Cliente.objects.get(id=selected_cliente_id)
            venta.cliente = selected_cliente  # Update the sale's client
            venta.save()

        elif request.POST['detalle_id_delete']:
            nombre_producto_eliminado = eliminar_de_carrito(request.POST['detalle_id_delete'])
            data['eliminado'] = 'Se ha eliminado del carrito: ' + nombre_producto_eliminado + ' de manera exitosa'
       
    return render(request, 'venta/carrito.html',
                  {'lista_detalle': lista_detalle, 'venta': venta, 'data': data,'lista_clientes':lista_clientes,})


from django.contrib.auth.decorators import user_passes_test

def is_superuser(user):
    return user.is_superuser

@login_required(login_url='/admin/login/')
@user_passes_test(is_superuser, login_url='/')
def balance(request):


    ventas = Venta.objects.all().order_by('fecha')
    compras = Compra.objects.all().order_by('fecha')

    #detalleVentas = DetalleVenta.objects.all()
    
    # Obtener el top 10 de productos más vendidos
    top_ventas = DetalleVenta.objects.values('producto__descripcion', 'producto__nombre').annotate(
        total_ventas=Sum('cantidad')).order_by('-total_ventas')[:10]


    argentina_timezone = timezone('America/Argentina/Buenos_Aires')
    fecha_actual = datetime.now(argentina_timezone).date()

    # Obtener la hora de inicio y fin del día en Argentina
    hora_inicio_dia = argentina_timezone.localize(datetime.combine(fecha_actual, time.min))
    hora_fin_dia = argentina_timezone.localize(datetime.combine(fecha_actual, time.max))

    # Obtener todas las ventas del día actual
    ventas_hoy = DetalleVenta.objects.filter(fecha__range=(hora_inicio_dia, hora_fin_dia))

    ventas_hoy_caja_1 = DetalleVenta.objects.filter(fecha__range=(hora_inicio_dia, hora_fin_dia),venta__nombre_factura='caja_1')
    ventas_hoy_caja_2 = DetalleVenta.objects.filter(fecha__range=(hora_inicio_dia, hora_fin_dia),venta__nombre_factura='caja_2')

    # Calcular los totales de ventas por moneda
    ventas_hoy_pesos = sum(item.get_total for item in ventas_hoy.filter(moneda='Pesos'))
    ventas_hoy_usd = sum(item.get_total for item in ventas_hoy.filter(moneda='Dolares'))
    ventas_hoy_bs = sum(item.get_total for item in ventas_hoy.filter(moneda='Bolivianos'))

    # Calcular los totales de ventas por moneda
    ventas_hoy_pesos_c1 = sum(item.get_total for item in ventas_hoy_caja_1.filter(moneda='Pesos'))
    ventas_hoy_usd_c1 = sum(item.get_total for item in ventas_hoy_caja_1.filter(moneda='Dolares'))
    ventas_hoy_bs_c1 = sum(item.get_total for item in ventas_hoy_caja_1.filter(moneda='Bolivianos'))

    # Calcular los totales de ventas por moneda
    ventas_hoy_pesos_c2 = sum(item.get_total for item in ventas_hoy_caja_2.filter(moneda='Pesos'))
    ventas_hoy_usd_c2 = sum(item.get_total for item in ventas_hoy_caja_2.filter(moneda='Dolares'))
    ventas_hoy_bs_c2 = sum(item.get_total for item in ventas_hoy_caja_2.filter(moneda='Bolivianos'))

    # Obtener todas las ventas del día actual

    primer_dia_mes = fecha_actual.replace(day=1)
    ultimo_dia_mes = primer_dia_mes.replace(day=28) + timedelta(days=4) - timedelta(days=1)


    # Obtener todas las ventas del mes actual
    ventas_mes = DetalleVenta.objects.filter(fecha__range=(primer_dia_mes, ultimo_dia_mes))

    ventas_mes_pesos = sum(item.get_total for item in ventas_mes.filter(moneda='Pesos'))
    ventas_mes_usd = sum(item.get_total for item in ventas_mes.filter(moneda='Dolares'))
    ventas_mes_bs = sum(item.get_total for item in ventas_mes.filter(moneda='Bolivianos'))


    valuacion_inventario = Producto.objects.annotate(
        valuacion=ExpressionWrapper(F('en_stock') * F('costo'), output_field=DecimalField())
    ).aggregate(total_valuacion=Sum('valuacion'))['total_valuacion']


    # Obtener el total de ventas del mes actual
    gastos_mes_actual = Gasto.objects.filter(
        fecha__year=fecha_actual.year, fecha__month=fecha_actual.month
    ).aggregate(total_gastos_mes_actual=Sum('total'))['total_gastos_mes_actual']

    # Obtener el total de ventas del mes actual
    retiros_mes_actual = Retiro.objects.filter(
        fecha__year=fecha_actual.year, fecha__month=fecha_actual.month
    ).aggregate(total_retiros_mes_actual=Sum('total'))['total_retiros_mes_actual']

    # Obtener el total de compras del mes actual (asumiendo que también tienes un modelo 'Compra' similar a 'Venta')
    compras_mes_actual = Compra.objects.filter(
        fecha__year=fecha_actual.year, fecha__month=fecha_actual.month
    ).aggregate(total_compras_mes_actual=Sum('total'))['total_compras_mes_actual']

    fecha_actual = date.today()
        # Obtener la fecha actual menos 30 días
    fecha_30_dias_atras = fecha_actual - timedelta(days=30)

    # Inicializar el diccionario de ventas en los últimos 30 días
    ventas_30_dias = {}
  
    ventas_por_dia = DetalleVenta.objects.filter(fecha__range=(fecha_30_dias_atras, fecha_actual),moneda="Pesos").values('fecha__day').annotate(
        total_ventas=Sum(ExpressionWrapper(F('cantidad') * F('precio'), output_field=DecimalField()))
    )
    ventas_por_dia_usd = DetalleVenta.objects.filter(fecha__range=(fecha_30_dias_atras, fecha_actual),moneda="Dolares").values('fecha__day').annotate(
        total_ventas=Sum(ExpressionWrapper(F('cantidad') * F('precio'), output_field=DecimalField()))
    )
    ventas_por_dia_bs = DetalleVenta.objects.filter(fecha__range=(fecha_30_dias_atras, fecha_actual),moneda="Bolivianos").values('fecha__day').annotate(
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


        'ventas_hoy_pesos': ventas_hoy_pesos or 0,
        'ventas_hoy_usd': ventas_hoy_usd or 0,
        'ventas_hoy_bs': ventas_hoy_bs or 0,

        'ventas_hoy_pesos_c1': ventas_hoy_pesos_c1 or 0,
        'ventas_hoy_usd_c1': ventas_hoy_usd_c1 or 0,
        'ventas_hoy_bs_c1': ventas_hoy_bs_c1 or 0,

        'ventas_hoy_pesos_c2': ventas_hoy_pesos_c2 or 0,
        'ventas_hoy_usd_c2': ventas_hoy_usd_c2 or 0,
        'ventas_hoy_bs_c2': ventas_hoy_bs_c2 or 0,

        'ventas_mes_pesos': ventas_mes_pesos or 0,
        'ventas_mes_usd': ventas_mes_usd or 0,
        'ventas_mes_bs': ventas_mes_bs or 0,

        #'ventas_mes_actual': ventas_mes_actual or 0,
        'compras_mes_actual': compras_mes_actual or 0,
        'gastos_mes_actual': gastos_mes_actual or 0,
        'retiros_mes_actual': retiros_mes_actual or 0,

        'top_ventas':top_ventas,
        'ventas_30_dias':ventas_30_dias,
        'ventas_por_dia':ventas_por_dia,
        'ventas_por_dia_usd':ventas_por_dia_usd,       
        'ventas_por_dia_bs':ventas_por_dia_bs, 
    }

    return render(request, 'balance.html', context)


def agregar_producto_a_carrito(venta, cantidad, producto, moneda):
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
        detalle_venta.moneda = moneda

        if moneda == "Pesos":
            detalle_venta.precio = producto.precio
        elif moneda == "Dolares":
            detalle_venta.precio = producto.precio_usd
        else:
            detalle_venta.precio = producto.precio_bs
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


def obtener_venta_actual(caja_usuario):
    """
    Método que retorna la venta actual, se pueden seguir realizando acciones en la venta hasta que la venta se encuentre
    en estado cancelada, finalizada o anulada
    :return Venta:
    """
    venta = Venta.objects.filter(estado=Venta.ESTADO_FACTURADA, nombre_factura=caja_usuario).first()
    if not venta:
        venta = Venta.objects.filter(estado=Venta.ESTADO_PAGADA, nombre_factura=caja_usuario).first()
    if not venta:
        # Si no existe una venta en estado creado, la creamos
        venta, create = Venta.objects.get_or_create(estado=Venta.ESTADO_CREADA, nombre_factura=caja_usuario)
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






