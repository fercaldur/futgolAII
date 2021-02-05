from django.contrib import admin
from django.urls import path
from main import views

urlpatterns = [
    path('', views.inicio),
    path('equipos/',views.equipos),
    path('clasificacion/',views.clasificacion),
    path('calendario/',views.partidos),
    path('noticias/',views.noticias),
    path('cargaBD/',views.carga),
    path('cargaWhoosh/',views.cargaWhoosh),
    path('sobrenosotros/',views.sobreNosotros),
    path('partidosPorJornada/',views.partidosPorJornadaWhoosh),
    path('noticiasPorEquipo/',views.noticiasPorEquipoWhoosh),
    path('loginDjango/',views.loginDjango),
    path('loginWhoosh/',views.loginWhoosh),

    

    ]
