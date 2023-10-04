# Generated by Django 4.2.5 on 2023-10-02 17:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Author',
            fields=[
                ('name_surname', models.CharField(choices=[('Jordan Price', 'Jordan Price'), ('Ian Alvarez', 'Ian Alvarez'), ('Wallace Castillo', 'Wallace Castillo'), ('Ken Sanders', 'Ken Sanders'), ('Bob Patel', 'Bob Patel'), ('Jaime Myers', 'Jaime Myers'), ('Ella Long', 'Ella Long'), ('Stacey Ross', 'Stacey Ross'), ('Wilma Foster', 'Wilma Foster'), ('Gina Jimenez', 'Gina Jimenez')], max_length=100, primary_key=True, serialize=False)),
                ('image', models.ImageField(upload_to='images/authors/')),
            ],
        ),
        migrations.CreateModel(
            name='Topic',
            fields=[
                ('name', models.CharField(choices=[('politics', 'politics'), ('business', 'business'), ('economy', 'economy')], max_length=100, primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('headline', models.CharField(max_length=200)),
                ('article_text', models.CharField(max_length=8000)),
                ('image', models.ImageField(upload_to='images/')),
                ('pub_date', models.DateTimeField(auto_now_add=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='newsapp.author')),
                ('topic', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='newsapp.topic')),
            ],
        ),
    ]
