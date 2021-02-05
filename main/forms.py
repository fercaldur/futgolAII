#encoding:utf-8
from django import forms
from main.models import Partido, Equipo

class PartidoPorJornadaWhooshForm(forms.Form):
    jornadas= []
    for partido in Partido.objects.all():
        j = "Jornada"+str(partido.jornada)
        if not [j,j] in jornadas:
            jornadas.append([j, j])
    jornada = forms.CharField(label="Jornada", widget=forms.Select(choices=jornadas), required=True)

class NoticiaPorEquipoWhooshForm(forms.Form):
    equipos=[(e.nombreEquipo,e.nombreEquipo) for e in Equipo.objects.all()]
    nombreEquipo = forms.CharField(label="Nombre del equipo", widget=forms.Select(choices=equipos), required=True)


    