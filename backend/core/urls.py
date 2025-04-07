from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoriaViewSet, ProductoViewSet, OrdenViewSet, ProductoOrdenViewSet, VentasPorHora
from .views import api_pronostico_lunes_24, api_pronostico_dinamico, api_pronostico_dinamico2

router = DefaultRouter()
router.register(r'categorias', CategoriaViewSet)
router.register(r'productos', ProductoViewSet)
router.register(r'ordenes', OrdenViewSet)
router.register(r'productosorden', ProductoOrdenViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('ventas-por-hora/', VentasPorHora.as_view(), name='ventas_por_hora'),
    path('pronostico_lunes_24/', api_pronostico_lunes_24, name='pronostico_lunes_24'),
    path('pronostico/', api_pronostico_dinamico, name='pronostico_dinamico'),
    path('pronostico2/', api_pronostico_dinamico2, name='pronostico_dinamico2'),
]