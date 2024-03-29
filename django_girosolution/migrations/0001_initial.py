# -*- coding: utf-8 -*-
# Generated by Django 1.11.21 on 2019-07-23 13:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='GirosolutionTransaction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created_at')),
                ('reference', models.TextField(null=True, verbose_name='reference')),
                ('backend_tx_id', models.TextField(null=True, verbose_name='backend tx id')),
                ('merchant_tx_id', models.CharField(max_length=255, unique=True, verbose_name='merchant tx id')),
                ('merchant_id', models.IntegerField(verbose_name='amount in Cents')),
                ('project_id', models.IntegerField(verbose_name='amount in Cents')),
                ('amount', models.PositiveIntegerField(verbose_name='amount in Cents')),
                ('currency', models.CharField(default='EUR', max_length=3, verbose_name='Currency Code (3 Chars)')),
                ('purpose', models.CharField(max_length=27, verbose_name='purpose')),
                ('redirect_url', models.TextField(verbose_name='redirect url')),
                ('notify_url', models.TextField(verbose_name='notify url')),
                ('success_url', models.TextField(verbose_name='success url')),
                ('error_url', models.TextField(verbose_name='error url')),
                ('payment_type', models.CharField(max_length=128, verbose_name='paymentname')),
                ('result_payment', models.IntegerField(null=True, verbose_name='return code from girosolution transaction')),
                ('result_avs', models.IntegerField(blank=True, null=True, verbose_name='return code of girosolution age verification')),
                ('obv_name', models.TextField(blank=True, null=True, verbose_name='obv name')),
                ('latest_response_code', models.IntegerField(null=True, verbose_name='rc field from girosolution response')),
                ('latest_response_msg', models.TextField(blank=True, null=True, verbose_name='msg field from girosolution response')),
            ],
            options={
                'verbose_name': 'Girosolution Transaction',
                'verbose_name_plural': 'Girosolution Transaction',
            },
        ),
    ]
