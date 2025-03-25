from rest_framework import serializers
from .models import Categoria, Producto, Orden, ProductoOrden

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = '__all__'
        
class ProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = '__all__'
        
class OrdenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Orden
        fields = '__all__'
        
class ProductoOrdenSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductoOrden
        fields = '__all__'