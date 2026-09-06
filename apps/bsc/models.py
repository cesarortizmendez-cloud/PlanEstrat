"""Persistencia del mapa estratégico.

Como la construcción del mapa es un proceso largo y colaborativo, se guarda en la
base de datos: cualquiera con el nombre + clave (o el enlace de edición) puede
abrirlo y seguir trabajándolo. Usa Postgres en producción (misma BD que decisiones).
"""
from django.contrib.auth.hashers import check_password, make_password
from django.db import models


class MapaEstrategico(models.Model):
    nombre = models.CharField(max_length=160)
    clave_hash = models.CharField(max_length=128)
    edit_token = models.CharField(max_length=48, unique=True)
    datos = models.JSONField(default=dict)          # {fases, objetivos, relaciones}
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    def set_clave(self, raw):
        self.clave_hash = make_password(raw)

    def check_clave(self, raw):
        return check_password(raw, self.clave_hash)

    def __str__(self):
        return self.nombre
