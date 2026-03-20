from django.db import migrations, models

class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    # icono = models.CharField(max_length=50, blank=True) # Opcional para FontAwesome

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name_plural = "Categorías"

class Producto(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    precio_lista = models.IntegerField()
    # NUEVO CAMPO DE STOCK
    stock = models.IntegerField(default=0, verbose_name="Stock disponible")
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='productos', null=True, blank=True)
    imagen = models.ImageField(upload_to='productos/', null=True, blank=True)
    codigo_sku = models.CharField(max_length=50, unique=True, null=True, blank=True)

    def __str__(self):
        return self.nombre