from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoriaViewSet, ProductoViewSet, OrdenViewSet, ProductoOrdenViewSet, VentasPorHora


router = DefaultRouter()
router.register(r'categorias', CategoriaViewSet)
router.register(r'productos', ProductoViewSet)
router.register(r'ordenes', OrdenViewSet)
router.register(r'productosorden', ProductoOrdenViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('ventas-por-hora/', VentasPorHora.as_view(), name='ventas_por_hora'),
]