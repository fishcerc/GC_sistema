from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projetos', '0009_diarioprojeto'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='tarefa',
            options={'ordering': ['id'], 'verbose_name': 'Tarefa do Projeto', 'verbose_name_plural': 'Tarefas do Projeto'},
        ),
        migrations.AlterField(
            model_name='diarioprojeto',
            name='texto',
            field=models.TextField(blank=True, default='', verbose_name='Anotação do Diário'),
        ),
        migrations.AddField(
            model_name='diarioprojeto',
            name='arquivo',
            field=models.FileField(blank=True, null=True, upload_to='diario_projetos/%Y/%m/', verbose_name='Arquivo Anexo'),
        ),
    ]
