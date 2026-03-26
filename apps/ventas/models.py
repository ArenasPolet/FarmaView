
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from apps.clientes.models import Contacto, Institucion
from apps.productos.models import Producto
from apps.visitas.models import Visita # Opcional, pero muy pro
from django.conf import settings

class MetaMensual(models.Model):
    # Conectamos la meta al usuario (representante)
    representante = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='metas')
    
    # Para saber de qué mes y año es esta meta
    mes = models.PositiveIntegerField(help_text="Número del mes (1-12)")
    anio = models.PositiveIntegerField(help_text="Año (Ej: 2026)")
    
    # El monto en dinero de la meta (Ej: 72210000)
    monto_meta = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    
    # El monto real de ventas alcanzadas en ese mes
    ventas_actuales = models.DecimalField(max_digits=12, decimal_places=0, default=0)

    class Meta:
        # Un representante solo puede tener una meta por mes y año
        unique_together = ('representante', 'mes', 'anio')
        verbose_name = 'Meta Mensual'
        verbose_name_plural = 'Metas Mensuales'

    def __str__(self):
        return f"Meta de {self.representante.first_name} - {self.mes}/{self.anio}"
    
    # Una pequeña función de ayuda para sacar el porcentaje rápidamente
    def porcentaje_cumplimiento(self):
        if self.monto_meta > 0:
            return int((self.ventas_actuales / self.monto_meta) * 100)
        return 0
    


#---MODELO DE PEDIDOS ----

class Pedido(models.Model):
    ESTADOS_PEDIDO = [
        ('Borrador', 'Borrador'),
        ('Ingresado', 'Ingresado'),
        ('Facturado', 'Facturado'),
        ('Cancelado', 'Cancelado'),
    ]

    representante = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='pedidos')
    institucion = models.ForeignKey(Institucion, on_delete=models.PROTECT, related_name='pedidos')
    # Campo oculto para saber si esta venta la hizo el sistema leyendo un Excel
    origen_excel = models.BooleanField(default=False)
    # =========================================================
    # ¡NUEVO CAMPO! Guardamos quién solicitó la orden
    # Usamos SET_NULL por si en el futuro borran al contacto, la orden no se borra.
    # =========================================================
    contacto = models.ForeignKey(Contacto, on_delete=models.SET_NULL, null=True, blank=True, related_name='pedidos')
    
    visita = models.ForeignKey(Visita, on_delete=models.SET_NULL, null=True, blank=True, related_name='pedidos_generados')

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    estado = models.CharField(max_length=20, choices=ESTADOS_PEDIDO, default='Borrador')
    notas_internas = models.TextField(blank=True)
    
    total_neto = models.IntegerField(default=0)
    total_iva = models.IntegerField(default=0)
    total_final = models.IntegerField(default=0)

    class Meta:
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"Pedido #{self.id} - {self.institucion.nombre} ({self.estado})"

    def calcular_totales(self):
        detalles = self.detalles.all()
        total = sum(item.subtotal for item in detalles)
        self.total_neto = int(total / 1.19)
        self.total_iva = total - self.total_neto
        self.total_final = total
        self.save()

# ... (El resto de la clase DetallePedido queda igual) ...
    """
    Cabecera del Pedido: Representa la Orden de Transferencia B2B.
    """
    ESTADOS_PEDIDO = [
        ('Borrador', 'Borrador'),       # El rep lo está armando
        ('Ingresado', 'Ingresado'),     # Enviado a la droguería (Suma a Proyección)
        ('Facturado', 'Facturado'),     # Confirmado por gerencia (Suma a Meta Real)
        ('Cancelado', 'Cancelado'),     # No se concretó
    ]

    # Relaciones principales
    representante = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='pedidos')
    institucion = models.ForeignKey(Institucion, on_delete=models.PROTECT, related_name='pedidos')
    
    # ¡Nivel Senior! Vincular el pedido a la visita exacta donde se generó
    visita = models.ForeignKey(Visita, on_delete=models.SET_NULL, null=True, blank=True, related_name='pedidos_generados')

    # Datos del documento
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    estado = models.CharField(max_length=20, choices=ESTADOS_PEDIDO, default='Borrador')
    notas_internas = models.TextField(blank=True, help_text="Comentarios para la droguería o gerencia")
    
    # Totales (En Chile normalmente se usa IntegerField para CLP)
    total_neto = models.IntegerField(default=0)
    total_iva = models.IntegerField(default=0)
    total_final = models.IntegerField(default=0)

    class Meta:
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"Pedido #{self.id} - {self.institucion.nombre} ({self.estado})"

    def calcular_totales(self):
        """
        Método profesional para recalcular el total sumando los detalles.
        Se llama cada vez que se agrega o quita un producto.
        """
        detalles = self.detalles.all()
        total = sum(item.subtotal for item in detalles)
        self.total_neto = int(total / 1.19) # Asumiendo IVA 19% en Chile
        self.total_iva = total - self.total_neto
        self.total_final = total
        self.save()


class DetallePedido(models.Model):
    """
    Las "Líneas" del carrito: Qué producto y cuántos.
    """
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    
    cantidad = models.PositiveIntegerField(default=1)
    
    # ¡Regla de Oro en E-commerce/SaaS! Guardar el precio histórico.
    # Si el producto cambia de precio mañana, el pedido de ayer no debe alterarse.
    precio_unitario_historico = models.IntegerField(help_text="Precio del producto al momento de la venta")
    descuento_aplicado = models.PositiveIntegerField(default=0, help_text="Porcentaje de descuento (0-100)")
    
    subtotal = models.IntegerField(default=0)

    class Meta:
        verbose_name = "Detalle de Pedido"
        verbose_name_plural = "Detalles de Pedido"

    def __str__(self):
        return f"{self.cantidad}x {self.producto.nombre} (Pedido #{self.pedido.id})"

    def save(self, *args, **kwargs):
        """
        Calcula el subtotal de esta línea automáticamente antes de guardar en BD.
        """
        # 1. Si es nuevo, copiamos el precio actual del producto al precio histórico
        if not self.id and not self.precio_unitario_historico:
            self.precio_unitario_historico = self.producto.precio # Asumiendo que tu modelo Producto tiene campo 'precio'
            
        # 2. Calculamos el subtotal con el descuento aplicado
        precio_con_descuento = self.precio_unitario_historico * (1 - (self.descuento_aplicado / 100.0))
        self.subtotal = int(precio_con_descuento * self.cantidad)
        
        super().save(*args, **kwargs)
        
        # 3. Le avisamos a la cabecera que actualice su total general
        self.pedido.calcular_totales()


class MetaInstitucion(models.Model):
    # Conectamos con la institución (Cliente)
    institucion = models.ForeignKey('clientes.Institucion', on_delete=models.CASCADE, related_name='metas_mensuales')
    # Conectamos con el vendedor responsable
    representante = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    # Fecha
    mes = models.PositiveIntegerField(help_text="Número del mes (1-12)")
    anio = models.PositiveIntegerField(help_text="Año (Ej: 2026)")
    
    # Dinero
    monto_meta = models.DecimalField(max_digits=12, decimal_places=0, default=0)

    class Meta:
        # Evita que subas dos metas distintas para la misma clínica en el mismo mes
        unique_together = ('institucion', 'representante', 'mes', 'anio')
        verbose_name = 'Meta por Institución'
        verbose_name_plural = 'Metas por Instituciones'

    def __str__(self):
        return f"{self.institucion.nombre} - {self.mes}/{self.anio} (${self.monto_meta})"