from django.shortcuts import render

from compra.models import Compra



def compras_list(request):


    compra_list = Compra.objects.all()

    
    context = {'compra_list': compra_list}

    return render(request, 'compra/compra_list.html', context)