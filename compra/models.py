from django.db import models
from producto.models import Producto
from agenda.models import Viaje
from django.core.exceptions import ValidationError
          
class Compra(models.Model):
    fecha = models.DateField()
    viaje = models.ForeignKey(Viaje,on_delete=models.DO_NOTHING,blank=False, null=False)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.DecimalField(max_digits=25, decimal_places=2)
    costo = models.DecimalField(max_digits=25,decimal_places=2,blank=False,null=False)
    total = models.DecimalField(max_digits=25,decimal_places=2,blank=True,null=True,default=0)
    estado = models.BooleanField(default=False)
    
    def clean(self):
        if self.estado == True:
            raise ValidationError("Este producto ya fué controlado. No se puede modificar.")
        super().clean()
    
    def save(self, *args, **kwargs):

        self.total = self.cantidad * self.costo
        if self.estado == True:
            if self.costo > 0:
                self.total = self.cantidad * self.costo
            else:
                self.total = 0

            producto = self.producto
            producto.en_stock += self.cantidad
    
            producto.save()

            self.estado == True

        super(Compra, self).save(*args, **kwargs)
    
