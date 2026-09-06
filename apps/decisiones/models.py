"""Modelos de la decisión colaborativa multiusuario.

Es la ÚNICA app con base de datos (junto con el guardado de mapas): en producción usa
Postgres (Neon) vía DATABASE_URL; en local funciona con SQLite. El resto es stateless.

Una Decision es una "sala": el facilitador define objetivo, criterios y ALTERNATIVAS,
la comparte con nombre + código + clave, y cada participante entrega su evaluación
individual (ponderación de criterios + desempeño de las alternativas). El sistema
calcula la decisión de cada persona y luego la decisión agregada del grupo.
"""
from django.contrib.auth.hashers import check_password, make_password
from django.db import models


class Decision(models.Model):
    PRIVACIDAD = [('privada', 'Privada (Delphi)'), ('grupal', 'Grupal visible'), ('anonima', 'Anónima')]
    ESTADO = [('abierta', 'Abierta'), ('cerrada', 'Cerrada')]

    nombre = models.CharField(max_length=140)
    codigo = models.CharField(max_length=16, default='', db_index=True)   # código corto para unirse
    objetivo = models.CharField(max_length=200, default='', blank=True)
    metodo = models.CharField(max_length=20, default='ahp')
    criterios = models.JSONField(default=list)          # lista de nombres de criterio
    alternativas = models.JSONField(default=list)        # lista de nombres de alternativa
    clave_hash = models.CharField(max_length=128)        # clave de participante (hash)
    admin_token = models.CharField(max_length=48, unique=True)
    privacidad = models.CharField(max_length=12, choices=PRIVACIDAD, default='grupal')
    estado = models.CharField(max_length=8, choices=ESTADO, default='abierta')
    creado = models.DateTimeField(auto_now_add=True)

    def set_clave(self, raw):
        self.clave_hash = make_password(raw)

    def check_clave(self, raw):
        return check_password(raw, self.clave_hash)

    def __str__(self):
        return '%s (%s)' % (self.nombre, self.codigo)


class Participacion(models.Model):
    decision = models.ForeignKey(Decision, related_name='participaciones', on_delete=models.CASCADE)
    participante = models.CharField(max_length=120, blank=True)
    juicios = models.JSONField(default=list)             # criterios: matriz AHP (o influencia ANP)
    desempeno = models.JSONField(default=list)           # alternativas x criterios (valoración 1..9)
    consistencia = models.FloatField(null=True, blank=True)
    resultado = models.JSONField(default=dict, blank=True)   # su decisión individual (seleccionado, ranking)
    enviado = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '%s · %s' % (self.decision.nombre, self.participante or 'anónimo')
