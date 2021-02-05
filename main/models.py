#encoding:utf-8

from django.db import models

class Equipo(models.Model):
    idEquipo = models.TextField(primary_key=True)
    nombreEquipo = models.TextField(verbose_name='Equipo', unique=True)
    posicion = models.IntegerField(verbose_name='Posicion')
    escudo = models.ImageField(verbose_name='Escudo')
    linkEquipo = models.TextField(verbose_name='Link del equipo')
      
    
    def __str__(self):
        return self.nombreEquipo

class Partido(models.Model):
    idPartido = models.TextField(primary_key=True)
    equipoLocal = models.ManyToManyField('Equipo', related_name = "equipoLocal")
    equipoVisitante = models.ManyToManyField('Equipo', related_name = "equipoVisitante")
    golesLocal = models.TextField(verbose_name='Goles Local')
    golesVisitante = models.TextField(verbose_name='Goles Visitante')
    jornada = models.IntegerField(verbose_name='Jornada')
    fechaPartido = models.TextField(verbose_name='Fecha Partido')
    
    def __str__(self):
        return self.idPartido

class Noticia(models.Model):
    idNoticia = models.TextField(primary_key=True)
    nombreEquipo = models.ManyToManyField(Equipo, related_name = "equipo")
    linkNoticia = models.TextField(verbose_name='Link de la noticia')
    tituloNoticia = models.TextField(verbose_name='Titulo de la noticia')
    descripcionNoticia = models.TextField(verbose_name='Descripcion de la noticia')
    imagenNoticia = models.ImageField(verbose_name='Escudo')
    tiempoPublicacion = models.TextField(verbose_name='Tiempo de la publicacion')
    autor = models.TextField(verbose_name='Autor')
    
    def __str__(self):
        return self.idNoticia
    
class Clasificacion(models.Model):
    idClasificacion = models.TextField(primary_key=True)
    nombreEquipo = models.ForeignKey(Equipo, verbose_name='Equipo', on_delete=models.SET_NULL, null=True)
    partidosJ = models.IntegerField(verbose_name='Partidos jugados')
    victorias = models.IntegerField(verbose_name='Victorias')
    empates = models.IntegerField(verbose_name='Empates')
    derrotas = models.IntegerField(verbose_name='Derrotas')
    diferenciaG = models.IntegerField(verbose_name='Diferencia de goles')
    puntos = models.IntegerField(verbose_name='Puntos')
    
    def __str__(self):
        return self.idClasificacion
    


