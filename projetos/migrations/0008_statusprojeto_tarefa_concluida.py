from django.db import migrations, models


def criar_status_iniciais(apps, schema_editor):
    StatusProjeto = apps.get_model('projetos', 'StatusProjeto')
    Projeto = apps.get_model('projetos', 'Projeto')

    iniciais = [
        {'nome': 'Em Planejamento', 'cor': 'info', 'ordem': 1, 'eh_concluido': False},
        {'nome': 'Em Execução', 'cor': 'primary', 'ordem': 2, 'eh_concluido': False},
        {'nome': 'Aguardando Cliente', 'cor': 'danger', 'ordem': 3, 'eh_concluido': False},
        {'nome': 'Concluído', 'cor': 'success', 'ordem': 4, 'eh_concluido': True},
        {'nome': 'Cancelado', 'cor': 'secondary', 'ordem': 5, 'eh_concluido': False},
    ]

    for item in iniciais:
        StatusProjeto.objects.get_or_create(nome=item['nome'], defaults=item)

    mapa_legado = {
        'planejamento': 'Em Planejamento',
        'em_andamento': 'Em Execução',
        'bloqueado': 'Aguardando Cliente',
        'concluido': 'Concluído',
        'cancelado': 'Cancelado',
    }
    for cod, novo_nome in mapa_legado.items():
        Projeto.objects.filter(status=cod).update(status=novo_nome)


class Migration(migrations.Migration):

    dependencies = [
        ('projetos', '0007_tecnico_usuario'),
    ]

    operations = [
        migrations.CreateModel(
            name='StatusProjeto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=60, unique=True, verbose_name='Nome do Estado / Status')),
                ('cor', models.CharField(choices=[('info', 'Azul Claro (Planejamento)'), ('primary', 'Azul Escuro (Em Execução)'), ('warning', 'Amarelo (Alerta / Pendência)'), ('danger', 'Vermelho (Bloqueado / Cancelado)'), ('success', 'Verde (Concluído)'), ('secondary', 'Cinza (Padrão)'), ('dark', 'Preto')], default='primary', max_length=20, verbose_name='Cor da Etiqueta')),
                ('ordem', models.PositiveIntegerField(default=1, verbose_name='Ordem de Exibição')),
                ('eh_concluido', models.BooleanField(default=False, help_text='Marque se este estado representa que o projeto foi concluído', verbose_name='Status de Conclusão?')),
                ('ativo', models.BooleanField(default=True, verbose_name='Ativo')),
            ],
            options={
                'verbose_name': 'Estado do Projeto',
                'verbose_name_plural': 'Estados do Projeto',
                'ordering': ['ordem', 'nome'],
            },
        ),
        migrations.AlterField(
            model_name='projeto',
            name='status',
            field=models.CharField(default='Em Planejamento', max_length=60, verbose_name='Status'),
        ),
        migrations.AddField(
            model_name='tarefa',
            name='concluida',
            field=models.BooleanField(default=False, verbose_name='Concluída?'),
        ),
        migrations.RunPython(criar_status_iniciais, migrations.RunPython.noop),
    ]
