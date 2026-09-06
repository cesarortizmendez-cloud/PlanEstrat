import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Decision',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=140)),
                ('metodo', models.CharField(default='ahp', max_length=20)),
                ('criterios', models.JSONField(default=list)),
                ('clave_hash', models.CharField(max_length=128)),
                ('admin_token', models.CharField(max_length=48, unique=True)),
                ('privacidad', models.CharField(default='privada', max_length=12)),
                ('estado', models.CharField(default='abierta', max_length=8)),
                ('creado', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Participacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('participante', models.CharField(blank=True, max_length=120)),
                ('juicios', models.JSONField(default=list)),
                ('consistencia', models.FloatField(blank=True, null=True)),
                ('enviado', models.DateTimeField(auto_now=True)),
                ('decision', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='participaciones', to='decisiones.decision')),
            ],
        ),
    ]
