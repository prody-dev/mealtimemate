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
