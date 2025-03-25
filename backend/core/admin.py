from django.contrib import admin

from .models import Categoria, Producto, Orden, ProductoOrden

admin.site.register(Categoria)
admin.site.register(Producto)
admin.site.register(Orden)
admin.site.register(ProductoOrden)
# Compare this snippet from backend/urls.py: