# Generated by Django 5.1.6 on 2025-02-14 14:30

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('first_name', models.CharField(max_length=25)),
                ('last_name', models.CharField(max_length=25)),
                ('phone', models.CharField(blank=True, max_length=25, null=True)),
                ('role', models.CharField(choices=[('RH', 'RH'), ('MANAGER', 'Manager'), ('EMPLOYEE', 'Employee')], default='EMPLOYEE', max_length=10)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Employe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=100, verbose_name='Nom')),
                ('prenom', models.CharField(max_length=100, verbose_name='Prénom')),
                ('departement', models.CharField(max_length=100, verbose_name='Département')),
                ('poste', models.CharField(max_length=100, verbose_name='Poste')),
                ('solde_de_conge', models.IntegerField(default=0, verbose_name='Solde de Congé')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profil_employe', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='DemandeConge',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_debut', models.DateField()),
                ('date_fin', models.DateField()),
                ('type_conge', models.CharField(choices=[('maternite', 'Congé de maternité'), ('maladie', 'Congé de maladie'), ('paye', 'Congé payé'), ('paternite', 'Congé de paternité'), ('occasionnel', 'Congé occasionnel')], max_length=20)),
                ('statut', models.CharField(choices=[('en_attente', 'En attente'), ('approuve', 'Approuvé'), ('rejete', 'Rejeté')], default='en_attente', max_length=20)),
                ('employe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='demandes', to='conges.employe')),
            ],
        ),
        migrations.CreateModel(
            name='Recommandation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.FloatField()),
                ('commentaire', models.TextField(blank=True, null=True)),
                ('statut', models.CharField(choices=[('en_attente', 'En attente'), ('approuve', 'Approuvé'), ('rejete', 'Rejeté')], default='en_attente', max_length=20)),
                ('demande', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recommandations', to='conges.demandeconge')),
            ],
        ),
        migrations.CreateModel(
            name='SystemeIA',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('historique_demandes', models.ManyToManyField(related_name='systeme_ia_histories', to='conges.demandeconge')),
            ],
        ),
    ]
