from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoriaViewSet, ProductoViewSet, OrdenViewSet, ProductoOrdenViewSet


router = DefaultRouter()
router.register(r'categorias', CategoriaViewSet)
router.register(r'productos', ProductoViewSet)
router.register(r'ordenes', OrdenViewSet)
router.register(r'productosorden', ProductoOrdenViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
