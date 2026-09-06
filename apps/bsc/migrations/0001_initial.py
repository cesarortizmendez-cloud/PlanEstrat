from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='MapaEstrategico',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=160)),
                ('clave_hash', models.CharField(max_length=128)),
                ('edit_token', models.CharField(max_length=48, unique=True)),
                ('datos', models.JSONField(default=dict)),
                ('creado', models.DateTimeField(auto_now_add=True)),
                ('actualizado', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
