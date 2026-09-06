from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('decisiones', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='decision',
            name='codigo',
            field=models.CharField(db_index=True, default='', max_length=16),
        ),
        migrations.AddField(
            model_name='decision',
            name='objetivo',
            field=models.CharField(blank=True, default='', max_length=200),
        ),
        migrations.AddField(
            model_name='decision',
            name='alternativas',
            field=models.JSONField(default=list),
        ),
        migrations.AddField(
            model_name='participacion',
            name='desempeno',
            field=models.JSONField(default=list),
        ),
        migrations.AddField(
            model_name='participacion',
            name='resultado',
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AlterField(
            model_name='decision',
            name='privacidad',
            field=models.CharField(
                choices=[('privada', 'Privada (Delphi)'), ('grupal', 'Grupal visible'), ('anonima', 'Anónima')],
                default='grupal', max_length=12),
        ),
    ]
