# Generated by Django 3.1.2 on 2021-01-13 15:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Equipo',
            fields=[
                ('idEquipo', models.TextField(primary_key=True, serialize=False)),
                ('nombreEquipo', models.TextField(unique=True, verbose_name='Equipo')),
                ('posicion', models.IntegerField(verbose_name='Posicion')),
                ('escudo', models.ImageField(upload_to='', verbose_name='Escudo')),
                ('linkEquipo', models.TextField(verbose_name='Link del equipo')),
            ],
        ),
        migrations.CreateModel(
            name='Partido',
            fields=[
                ('idPartido', models.TextField(primary_key=True, serialize=False)),
                ('golesLocal', models.TextField(verbose_name='Goles Local')),
                ('golesVisitante', models.TextField(verbose_name='Goles Visitante')),
                ('jornada', models.IntegerField(verbose_name='Jornada')),
                ('fechaPartido', models.TextField(verbose_name='Fecha Partido')),
                ('horaPartido', models.TextField(verbose_name='Hora Partido')),
                ('equipoLocal', models.ManyToManyField(related_name='equipoLocal', to='main.Equipo')),
                ('equipoVisitante', models.ManyToManyField(related_name='equipoVisitante', to='main.Equipo')),
            ],
        ),
        migrations.CreateModel(
            name='Noticia',
            fields=[
                ('idNoticia', models.TextField(primary_key=True, serialize=False)),
                ('linkNoticia', models.TextField(verbose_name='Link de la noticia')),
                ('tituloNoticia', models.TextField(verbose_name='Titulo de la noticia')),
                ('descripcionNoticia', models.TextField(verbose_name='Descripcion de la noticia')),
                ('imagenNoticia', models.ImageField(upload_to='', verbose_name='Escudo')),
                ('tiempoPublicacion', models.TextField(verbose_name='Tiempo de la publicacion')),
                ('autor', models.TextField(verbose_name='Autor')),
                ('nombreEquipo', models.ManyToManyField(related_name='equipo', to='main.Equipo')),
            ],
        ),
        migrations.CreateModel(
            name='Clasificacion',
            fields=[
                ('idClasificacion', models.TextField(primary_key=True, serialize=False)),
                ('partidosJ', models.IntegerField(verbose_name='Partidos jugados')),
                ('victorias', models.IntegerField(verbose_name='Victorias')),
                ('empates', models.IntegerField(verbose_name='Empates')),
                ('derrotas', models.IntegerField(verbose_name='Derrotas')),
                ('diferenciaG', models.IntegerField(verbose_name='Diferencia de goles')),
                ('puntos', models.IntegerField(verbose_name='Puntos')),
                ('nombreEquipo', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='main.equipo', verbose_name='Equipo')),
            ],
        ),
    ]
