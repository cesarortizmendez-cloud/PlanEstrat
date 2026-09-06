"""Modelos de la decisión colaborativa multiusuario.

Es la ÚNICA app con base de datos: en producción usa Postgres (Neon/Supabase) vía
DATABASE_URL; en local funciona con SQLite. El resto del sistema sigue siendo stateless.
"""
from django.contrib.auth.hashers import check_password, make_password
from django.db import models


class Decision(models.Model):
    PRIVACIDAD = [('privada', 'Privada (Delphi)'), ('grupal', 'Grupal visible'), ('anonima', 'Anónima')]
    ESTADO = [('abierta', 'Abierta'), ('cerrada', 'Cerrada')]

    nombre = models.CharField(max_length=140)
    metodo = models.CharField(max_length=20, default='ahp')
    criterios = models.JSONField(default=list)          # lista de nombres de criterio
    clave_hash = models.CharField(max_length=128)        # clave de participante (hash)
    admin_token = models.CharField(max_length=48, unique=True)
    privacidad = models.CharField(max_length=12, choices=PRIVACIDAD, default='privada')
    estado = models.CharField(max_length=8, choices=ESTADO, default='abierta')
    creado = models.DateTimeField(auto_now_add=True)

    def set_clave(self, raw):
        self.clave_hash = make_password(raw)

    def check_clave(self, raw):
        return check_password(raw, self.clave_hash)

    def __str__(self):
        return self.nombre


class Participacion(models.Model):
    decision = models.ForeignKey(Decision, related_name='participaciones', on_delete=models.CASCADE)
    participante = models.CharField(max_length=120, blank=True)
    juicios = models.JSONField(default=list)             # matriz de comparación n x n
    consistencia = models.FloatField(null=True, blank=True)
    enviado = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '%s · %s' % (self.decision.nombre, self.participante or 'anónimo')
