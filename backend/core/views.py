from django.shortcuts import render
from rest_framework import viewsets

from .models import Categoria, Producto, Orden, ProductoOrden
from .serializers import CategoriaSerializer, ProductoSerializer, OrdenSerializer, ProductoOrdenSerializer

class CategoriaViewSet(viewsets.ModelViewSet):
    #permission_classes = [IsAuthenticated]
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    
class ProductoViewSet(viewsets.ModelViewSet):
    #permission_classes = [IsAuthenticated]
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer
    
class OrdenViewSet(viewsets.ModelViewSet):
    #permission_classes = [IsAuthenticated]
    queryset = Orden.objects.all()
    serializer_class = OrdenSerializer
    
class ProductoOrdenViewSet(viewsets.ModelViewSet):
    #permission_classes = [IsAuthenticated]
    queryset = ProductoOrden.objects.all()
    serializer_class = ProductoOrdenSerializer

# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Orden, ProductoOrden
from django.db.models import Sum, Count
from django.utils import timezone

class VentasPorHora(APIView):
    def get(self, request):
        # Obtener todas las ordenes junto con las ventas de productos
        ventas = (
            ProductoOrden.objects
            .values('orden__hora_orden', 'producto__categoria__nombre')
            .annotate(cantidad_vendida=Sum('cantidad'))
            .order_by('orden__hora_orden')
        )

        # Formatear los datos para enviar
        data = {
            'x': [],  # horas
            'y': [],  # categorías
            'z': [],  # cantidades de ventas
        }

        for venta in ventas:
            data['x'].append(venta['orden__hora_orden'].strftime('%H:%M'))
            data['y'].append(venta['producto__categoria__nombre'])
            data['z'].append(venta['cantidad_vendida'])

        return Response(data)

