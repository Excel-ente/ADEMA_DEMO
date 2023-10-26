from django.db import models
from django.contrib.auth.models import User

CAJA = [
        ('caja_1', 'caja_1'),
        ('caja_2', 'caja_2'),
    ]
class Asignacion(models.Model):

    usuario = models.ForeignKey(User,on_delete=models.CASCADE)
    caja = models.CharField(max_length=10, choices=CAJA, default='caja_1')
    
    def __str__(self):
        return self.usuario.first_name


# Definir un diccionario con el nombre de los meses en español
meses = {
    1: "ENERO",
    2: "FEBRERO",
    3: "MARZO",
    4: "ABRIL",
    5: "MAYO",
    6: "JUNIO",
    7: "JULIO",
    8: "AGOSTO",
    9: "SEPTIEMBRE",
    10: "OCTUBRE",
    11: "NOVIEMBRE",
    12: "DICIEMBRE",
}

def formatear_fecha(fecha):
    dia = fecha.day
    mes_numero = fecha.month
    mes_nombre = meses[mes_numero]
    return f"{dia} De {mes_nombre}"

# Create your models here.
class Cliente(models.Model):
    codigo = models.CharField(unique=True,max_length=200, null=True, blank=True)
    nombre = models.CharField(unique=True,verbose_name='Vendedor',max_length=200, null=True, blank=True)
    telefono = models.CharField(max_length=20,default=1,blank=True,null=True)
    direccion = models.CharField(max_length=200,blank=True,null=True)

    
    def __str__(self):
        return self.nombre

class TipoGasto(models.Model):
    descripcion = models.CharField(max_length=255,unique=True,blank=False,null=False)

    def __str__(self):
        return self.descripcion
    
class Gasto(models.Model):
    fecha = models.DateField(blank=False,null=True)
    categoria = models.ForeignKey(TipoGasto,on_delete=models.SET_NULL,blank=False,null=True)
    descripcion = models.CharField(max_length=255, null=False, blank=False)
    total = models.DecimalField(max_digits=20,decimal_places=2,blank=False,null=False)

    def __str__(self):
        msg = f'{self.categoria} | {self.descripcion} | ${self.total}'
        return msg
    
class Retiro(models.Model):
    fecha = models.DateField(blank=False,null=True)
    descripcion = models.CharField(max_length=255, null=False, blank=False)
    total = models.DecimalField(max_digits=20,decimal_places=2,blank=False,null=False)

    def __str__(self):
        msg = f'{self.fecha} | {self.descripcion} | ${self.total}'
        return msg