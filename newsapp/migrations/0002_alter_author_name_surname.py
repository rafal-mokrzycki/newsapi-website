# Generated by Django 4.2.5 on 2023-09-19 12:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('newsapp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='author',
            name='name_surname',
            field=models.CharField(choices=[('Jordan Price', 'Jordan'), ('Ian Alvarez', 'Ian'), ('Wallace Castillo', 'Wallace'), ('Ken Sanders', 'Ken'), ('Bob Patel', 'Bob'), ('Jaime Myers', 'Jaime'), ('Ella Long', 'Ella'), ('Stacey Ross', 'Stacey'), ('Wilma Foster', 'Wilma'), ('Gina Jimenez', 'Gina')], default='Jordan Price', max_length=100, primary_key=True, serialize=False),
        ),
    ]
