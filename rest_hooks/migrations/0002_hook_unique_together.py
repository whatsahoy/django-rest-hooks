# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rest_hooks', '0001_initial'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='Hook',
            unique_together=set([('user', 'event', 'target')]),
        ),
    ]
