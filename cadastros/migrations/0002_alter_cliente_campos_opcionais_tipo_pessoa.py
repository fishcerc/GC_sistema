from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cadastros', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='cliente',
            options={'ordering': ['razao_social'], 'verbose_name': 'Cliente', 'verbose_name_plural': 'Clientes'},
        ),
        migrations.AddField(
            model_name='cliente',
            name='tipo_pessoa',
            field=models.CharField(
                choices=[('PJ', 'Pessoa Jurídica (CNPJ)'), ('PF', 'Pessoa Física (CPF)')],
                default='PJ',
                max_length=2,
                verbose_name='Tipo de Pessoa',
            ),
        ),
        migrations.AlterField(
            model_name='cliente',
            name='razao_social',
            field=models.CharField(max_length=200, verbose_name='Razão Social / Nome'),
        ),
        migrations.AlterField(
            model_name='cliente',
            name='nome_fantasia',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='Nome Fantasia'),
        ),
        migrations.AlterField(
            model_name='cliente',
            name='cnpj',
            field=models.CharField(blank=True, max_length=18, null=True, verbose_name='CNPJ / CPF'),
        ),
        migrations.AlterField(
            model_name='cliente',
            name='logradouro',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='Logradouro'),
        ),
        migrations.AlterField(
            model_name='cliente',
            name='numero',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='Número'),
        ),
        migrations.AlterField(
            model_name='cliente',
            name='bairro',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Bairro'),
        ),
        migrations.AlterField(
            model_name='cliente',
            name='cidade',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Cidade'),
        ),
        migrations.AlterField(
            model_name='cliente',
            name='estado',
            field=models.CharField(blank=True, default='SC', max_length=2, null=True, verbose_name='UF'),
        ),
        migrations.AlterField(
            model_name='cliente',
            name='pessoa_contato',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Pessoa de Contato'),
        ),
        migrations.AlterField(
            model_name='cliente',
            name='celular',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='Celular / WhatsApp'),
        ),
        migrations.AlterField(
            model_name='cliente',
            name='email',
            field=models.EmailField(blank=True, max_length=254, null=True, verbose_name='E-mail'),
        ),
        migrations.AlterField(
            model_name='filial',
            name='logradouro',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='Logradouro'),
        ),
        migrations.AlterField(
            model_name='filial',
            name='numero',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='Número'),
        ),
        migrations.AlterField(
            model_name='filial',
            name='bairro',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Bairro'),
        ),
        migrations.AlterField(
            model_name='filial',
            name='cidade',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Cidade'),
        ),
        migrations.AlterField(
            model_name='filial',
            name='estado',
            field=models.CharField(blank=True, default='SC', max_length=2, null=True, verbose_name='UF'),
        ),
        migrations.AlterField(
            model_name='dadosenergia',
            name='unidade_consumidora',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Unidade Consumidora (UC)'),
        ),
        migrations.AlterField(
            model_name='dadosenergia',
            name='concessionaria',
            field=models.CharField(blank=True, default='CELESC', max_length=50, null=True, verbose_name='Concessionária'),
        ),
        migrations.AlterField(
            model_name='dadosenergia',
            name='tensao_fornecimento',
            field=models.CharField(blank=True, help_text='Ex: 380/220V, 13.8 kV, 23 kV', max_length=50, null=True, verbose_name='Tensão de Atendimento'),
        ),
    ]
