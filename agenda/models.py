from django.db import models

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
    nit = models.CharField(max_length=20,default=1,blank=True,null=True)
    direccion = models.CharField(max_length=200,blank=True,null=True)

    
    def __str__(self):
        return self.nombre
    
class Vendedor(models.Model):
    codigo = models.CharField(max_length=200, null=True, blank=True)
    nombre = models.CharField(unique=True,max_length=200, null=True, blank=True)

    def __str__(self):
        return self.nombre
    

class Viaje(models.Model):
    estado = models.BooleanField(default=False)
    chofer = models.CharField(max_length=120, null=False, blank=False)
    patente_camion = models.CharField(max_length=120, null=False, blank=False)
    patente_semi = models.CharField(max_length=120, null=True, blank=True)
    fecha_salida = models.DateField(auto_now=True, null=False, blank=False)
    fecha_llegada = models.DateField(null=False, blank=False)
    costo_total_trasnlado = models.DecimalField(verbose_name="Costo de Translado",max_digits=15, decimal_places=2, null=False, blank=False)

    def __str__(self):
        
        if self.estado == True:
            return f'{self.chofer} | llega: 📆 {formatear_fecha(self.fecha_llegada)}'
        else:
            return f'{self.chofer} | llegó: 📆 {formatear_fecha(self.fecha_llegada)}'