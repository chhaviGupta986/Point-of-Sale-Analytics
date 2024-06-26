# Generated by Django 5.0 on 2024-04-17 10:43

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0002_test'),
    ]

    operations = [
        migrations.CreateModel(
            name='DemandForecasting',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('actuals', models.CharField(max_length=300)),
                ('predictions', models.CharField(max_length=300)),
                ('dates', models.CharField(max_length=300)),
                ('top_products', models.CharField(max_length=300)),
                ('rsquare', models.CharField(max_length=300)),
                ('companyname', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
