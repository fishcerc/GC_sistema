import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projetos', '0008_statusprojeto_tarefa_concluida'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='DiarioProjeto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('texto', models.TextField(verbose_name='Anotação do Diário')),
                ('criado_em', models.DateTimeField(auto_now_add=True, verbose_name='Criado em')),
                ('autor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Autor')),
                ('projeto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='diarios', to='projetos.projeto')),
            ],
            options={
                'verbose_name': 'Diário do Projeto',
                'verbose_name_plural': 'Diários do Projeto',
                'ordering': ['-criado_em', '-id'],
            },
        ),
    ]
