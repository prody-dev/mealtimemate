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

from datetime import time, datetime
from django.db.models import Avg
from django.http import JsonResponse
from .models import ProductoOrden, Orden, Producto, Categoria

def api_pronostico_lunes_24(request):
    # Fecha del pronóstico
    fecha_pronostico = datetime.strptime("2025-03-24", "%Y-%m-%d").date()

    # Filtrar solo los lunes antes del 24 de marzo
    lunes_pasados = Orden.objects.filter(
        fecha_orden__lt=fecha_pronostico,
        fecha_orden__week_day=2  # 2 = Lunes
    ).filter(
        hora_orden__gte=time(9, 0),
        hora_orden__lt=time(10, 0)
    )

    # Productos de la categoría con ID 1
    productos_categoria = Producto.objects.filter(categoria_id=1)

    # Ventas en esas órdenes y esa categoría
    ventas = ProductoOrden.objects.filter(
        orden__in=lunes_pasados,
        producto__in=productos_categoria
    ).aggregate(
        promedio_ventas=Avg('cantidad')
    )

    pronostico = ventas['promedio_ventas'] or 0

    return JsonResponse({
        'fecha_pronostico': fecha_pronostico.strftime("%Y-%m-%d"),
        'categoria_id': 1,
        'categoria_nombre': Categoria.objects.get(id=1).nombre,
        'hora_inicio': "09:00",
        'hora_fin': "10:00",
        'ventas_pronosticadas': round(pronostico, 2)
    })

from datetime import datetime, time
from django.http import JsonResponse
from django.db.models import Avg, Sum, Count
from .models import ProductoOrden, Orden, Producto, Categoria
import math

BLOQUES_HORARIOS = {
    1: (time(8, 0), time(9, 0)),
    2: (time(9, 0), time(10, 0)),
    3: (time(10, 0), time(11, 0)),
    4: (time(11, 0), time(12, 0)),
    5: (time(12, 0), time(13, 0)),
}

def api_pronostico_dinamico(request):
    # Obtener parámetros
    categoria_id = request.GET.get('categoria_id')
    bloque = int(request.GET.get('bloque_horario', 1))
    fecha_pronostico = datetime.strptime("2025-03-24", "%Y-%m-%d").date()

    if not categoria_id:
        return JsonResponse({"error": "Se requiere categoria_id"}, status=400)
    
    if bloque not in BLOQUES_HORARIOS:
        return JsonResponse({"error": "bloque_horario debe estar entre 1 y 5"}, status=400)

    try:
        categoria = Categoria.objects.get(id=categoria_id)
    except Categoria.DoesNotExist:
        return JsonResponse({"error": "Categoría no encontrada"}, status=404)

    hora_inicio, hora_fin = BLOQUES_HORARIOS[bloque]

    # Obtener órdenes de lunes anteriores
    lunes_pasados = Orden.objects.filter(
        fecha_orden__lt=fecha_pronostico,
        fecha_orden__week_day=2,  # Lunes
        hora_orden__gte=hora_inicio,
        hora_orden__lt=hora_fin
    )

    productos_categoria = Producto.objects.filter(categoria=categoria)

    # Obtener las instancias de ProductoOrden que están dentro del filtro
    producto_ordenes = ProductoOrden.objects.filter(
        orden__in=lunes_pasados,
        producto__in=productos_categoria
    )

    # Obtener el promedio de la cantidad vendida de esos productos
    ventas = producto_ordenes.aggregate(
        promedio_ventas=Avg('cantidad'),
        cantidad_total=Sum('cantidad'),
        productoorden_count=Count('id')
    )

    pronostico = ventas['promedio_ventas'] or 0
    cantidad_total = ventas['cantidad_total'] or 0
    productoorden_count = ventas['productoorden_count'] or 0

    # Redondeo hacia arriba o hacia abajo de acuerdo a las reglas solicitadas
    ventas_pronosticadas_redondeadas = math.floor(pronostico) if pronostico % 1 <= 0.50 else math.ceil(pronostico)

    # Preparar la respuesta con detalle de órdenes y productoordenes
    ordenes_info = [
        {
            "orden_id": producto_orden.orden.id,
            "productoorden_id": producto_orden.id,
            "fecha_orden": producto_orden.orden.fecha_orden,
            "hora_orden": producto_orden.orden.hora_orden.strftime("%H:%M"),
            "producto_id": producto_orden.producto.id,
            "producto_nombre": producto_orden.producto.nombre,
            "cantidad_vendida": producto_orden.cantidad,
            "total_venta": producto_orden.total
        }
        for producto_orden in producto_ordenes
    ]

    return JsonResponse({
        "fecha_pronostico": fecha_pronostico.strftime("%Y-%m-%d"),
        "categoria_id": categoria.id,
        "categoria_nombre": categoria.nombre,
        "bloque_horario": bloque,
        "hora_inicio": hora_inicio.strftime("%H:%M"),
        "hora_fin": hora_fin.strftime("%H:%M"),
        "ventas_pronosticadas": round(pronostico, 2),
        "ventas_pronosticadas_redondeadas": ventas_pronosticadas_redondeadas,
        "productoorden_count": productoorden_count,
        "cantidad_total": cantidad_total,
        "ordenes_involucradas": ordenes_info
    })

from datetime import datetime, time, timedelta, date
from django.http import JsonResponse
from django.db.models import Avg, Sum, Count
from .models import ProductoOrden, Orden, Producto, Categoria
import math

BLOQUES_HORARIOS = {
    1: (time(8, 0), time(9, 0)),
    2: (time(9, 0), time(10, 0)),
    3: (time(10, 0), time(11, 0)),
    4: (time(11, 0), time(12, 0)),
    5: (time(12, 0), time(13, 0)),
}

def get_next_monday(today=None):
    if today is None:
        today = date.today()
    days_ahead = 0 if today.weekday() == 0 else 7 - today.weekday()
    return today + timedelta(days=days_ahead)

def api_pronostico_dinamico2(request):
    categoria_id = request.GET.get('categoria_id')
    bloque = int(request.GET.get('bloque_horario', 1))

    if not categoria_id:
        return JsonResponse({"error": "Se requiere categoria_id"}, status=400)
    
    if bloque not in BLOQUES_HORARIOS:
        return JsonResponse({"error": "bloque_horario debe estar entre 1 y 5"}, status=400)

    try:
        categoria = Categoria.objects.get(id=categoria_id)
    except Categoria.DoesNotExist:
        return JsonResponse({"error": "Categoría no encontrada"}, status=404)

    # Calcular el próximo lunes
    proximo_lunes = get_next_monday()

    hora_inicio, hora_fin = BLOQUES_HORARIOS[bloque]

    # Obtener todas las órdenes de lunes anteriores al próximo lunes
    lunes_pasados = Orden.objects.filter(
        fecha_orden__lt=proximo_lunes,
        fecha_orden__week_day=2,  # Lunes
        hora_orden__gte=hora_inicio,
        hora_orden__lt=hora_fin
    )

    productos_categoria = Producto.objects.filter(categoria=categoria)

    producto_ordenes = ProductoOrden.objects.filter(
        orden__in=lunes_pasados,
        producto__in=productos_categoria
    )

    ventas = producto_ordenes.aggregate(
        promedio_ventas=Avg('cantidad'),
        cantidad_total=Sum('cantidad'),
        productoorden_count=Count('id')
    )

    pronostico = ventas['promedio_ventas'] or 0
    cantidad_total = ventas['cantidad_total'] or 0
    productoorden_count = ventas['productoorden_count'] or 0

    ventas_pronosticadas_redondeadas = math.floor(pronostico) if pronostico % 1 <= 0.50 else math.ceil(pronostico)

    ordenes_info = [
        {
            "orden_id": po.orden.id,
            "productoorden_id": po.id,
            "fecha_orden": po.orden.fecha_orden,
            "hora_orden": po.orden.hora_orden.strftime("%H:%M"),
            "producto_id": po.producto.id,
            "producto_nombre": po.producto.nombre,
            "cantidad_vendida": po.cantidad,
            "total_venta": po.total
        }
        for po in producto_ordenes
    ]

    return JsonResponse({
        "fecha_pronostico": proximo_lunes.strftime("%Y-%m-%d"),
        "categoria_id": categoria.id,
        "categoria_nombre": categoria.nombre,
        "bloque_horario": bloque,
        "hora_inicio": hora_inicio.strftime("%H:%M"),
        "hora_fin": hora_fin.strftime("%H:%M"),
        "ventas_pronosticadas": round(pronostico, 2),
        "ventas_pronosticadas_redondeadas": ventas_pronosticadas_redondeadas,
        "productoorden_count": productoorden_count,
        "cantidad_total": cantidad_total,
        "ordenes_involucradas": ordenes_info
    })
