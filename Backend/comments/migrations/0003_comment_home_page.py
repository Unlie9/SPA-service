# Generated by Django 5.1.1 on 2024-09-30 09:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('comments', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='home_page',
            field=models.URLField(blank=True, null=True),
        ),
    ]
