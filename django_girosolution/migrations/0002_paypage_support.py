from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_girosolution', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='girosolutiontransaction',
            name='paypage_url',
            field=models.TextField(blank=True, null=True, verbose_name='paypage url'),
        ),
    ]
