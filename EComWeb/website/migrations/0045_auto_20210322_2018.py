# Generated by Django 3.1.5 on 2021-03-22 14:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0044_auto_20210322_1458'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='description',
            field=models.TextField(default=' Please enter the description about the product. It should give an overview about the product, how popular the product is and so on..'),
        ),
    ]