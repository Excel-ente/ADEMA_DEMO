from django.db import models


# Create your models here.
class Categoria(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=200)
    imagen = models.ImageField(upload_to ='img/',blank=True,null=True)
    precio = models.DecimalField(verbose_name="Pesos",default=0,max_digits=25, decimal_places=2)
    precio_usd = models.DecimalField(verbose_name="Dolares",default=0,max_digits=25, decimal_places=2)
    precio_bs = models.DecimalField(verbose_name="Bolivianos",default=0,max_digits=25, decimal_places=2)
    en_stock = models.DecimalField(max_digits=25, decimal_places=2)
    costo = models.DecimalField(max_digits=25, decimal_places=2,default=0 ,blank=True,null=True)

    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.nombre + " " + self.descripcion

    def save(self, *args, **kwargs):
        if self.en_stock:
            pass
        else:
            self.en_stock = 0
        
        super(Producto, self).save(*args, **kwargs)
