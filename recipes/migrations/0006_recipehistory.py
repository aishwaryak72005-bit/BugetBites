from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0005_macrolog_userprofile'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='RecipeHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True)),
                ('ingredients_used', models.TextField(blank=True)),
                ('budget', models.CharField(blank=True, max_length=50)),
                ('cuisine', models.CharField(blank=True, max_length=100)),
                ('calories', models.CharField(blank=True, max_length=50)),
                ('protein', models.CharField(blank=True, max_length=50)),
                ('carbs', models.CharField(blank=True, max_length=50)),
                ('fat', models.CharField(blank=True, max_length=50)),
                ('cost', models.CharField(blank=True, max_length=50)),
                ('ai_response', models.TextField(blank=True)),
                ('generated_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='recipe_history',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={
                'ordering': ['-generated_at'],
            },
        ),
    ]
