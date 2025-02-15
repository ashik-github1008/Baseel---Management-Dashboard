# Generated by Django 5.1.6 on 2025-02-14 15:52

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0004_teammember'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='teammember',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='team_members', to='projects.project'),
        ),
        migrations.AlterUniqueTogether(
            name='teammember',
            unique_together={('project', 'user')},
        ),
    ]
