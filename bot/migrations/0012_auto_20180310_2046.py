# Generated by Django 2.0 on 2018-03-10 20:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0011_auto_20180310_2043'),
    ]

    operations = [
        migrations.AddField(
            model_name='coreuser',
            name='first_question_daal',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='coreuser',
            name='second_question_daal',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='coreuser',
            name='third_question_daal',
            field=models.BooleanField(default=False),
        ),
    ]
