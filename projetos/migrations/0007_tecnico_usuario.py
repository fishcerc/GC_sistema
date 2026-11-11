from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('projetos', '0006_remove_tecnico_area'),
    ]

    operations = [
        migrations.AddField(
            model_name='tecnico',
            name='usuario',
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='tecnico',
                to=settings.AUTH_USER_MODEL,
                verbose_name='Usuário do Sistema',
            ),
        ),
    ]
