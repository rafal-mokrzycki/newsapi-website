# Generated by Django 4.2.5 on 2023-09-25 07:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('newsapp', '0002_alter_author_name_surname'),
    ]

    operations = [
        migrations.AddField(
            model_name='author',
            name='image',
            field=models.ImageField(default='wallace_castillo.jpg', upload_to='images/authors/'),
        ),
        migrations.AlterField(
            model_name='article',
            name='topic',
            field=models.CharField(max_length=100),
        ),
    ]
