from django.contrib.auth.models import AbstractUser
from django.db import models
from .manager import UserManager


    
class User(AbstractUser):
    username = None
    class Role(models.TextChoices):
        RH = 'RH', 'RH'
        MANAGER = 'MANAGER', 'Manager'
        EMPLOYEE = 'EMPLOYEE', 'Employee'

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=25)
    last_name = models.CharField(max_length=25)
    phone = models.CharField(blank=True, null=True, max_length=25)
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.EMPLOYEE)  # Add role field

    
    

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    objects = UserManager()
    def name(self):
        return self.first_name + ' ' + self.last_name

    def __str__(self):
        return self.email


# Employe model
class Employe(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profil_employe")
    nom = models.CharField(max_length=100, verbose_name="Nom")
    prenom = models.CharField(max_length=100, verbose_name="Prénom")
    departement = models.CharField(max_length=100, verbose_name="Département")
    poste = models.CharField(max_length=100, verbose_name="Poste")
    solde_de_conge = models.IntegerField(verbose_name="Solde de Congé", default=0)

    def soumettre_demande(self):
        # Logic for submitting leave request
        pass

    def consulter_solde(self):
        return self.solde_de_conge

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.poste}"



# Responsable model    
class Responsable(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profil_responsable")
    nom = models.CharField(max_length=100, primary_key=True)  # or any other unique field
    prenom = models.CharField(max_length=100)
    def approuver_demande(self, demande):
        demande.statut = "approuve"
        demande.save()

    def consulter_recommandation(self, demande):
        return demande.recommandations.all()

    def __str__(self):
        return self.user.get_full_name()


# DemandeDeCongé model
class DemandeConge(models.Model):
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('approuve', 'Approuvé'),
        ('rejete', 'Rejeté'),
    ]

    employe = models.ForeignKey(Employe, on_delete=models.CASCADE, related_name="demandes")
    responsable = models.ForeignKey(Responsable, on_delete=models.CASCADE)
    date_debut = models.DateField()
    date_fin = models.DateField()
    motif = models.TextField()
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')

    def valider(self):
        self.statut = "approuve"
        self.save()

    def refuser(self):
        self.statut = "rejete"
        self.save()

    def __str__(self):
        return f"{self.employe} - {self.date_debut} à {self.date_fin}"



# Recommandation model
class Recommandation(models.Model):
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('approuve', 'Approuvé'),
        ('rejete', 'Rejeté'),
    ]

    demande = models.ForeignKey(DemandeConge, on_delete=models.CASCADE, related_name="recommandations")
    score = models.FloatField()  # Recommendation score
    commentaire = models.TextField(blank=True, null=True)  # Additional recommendation details
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')

    def __str__(self):
        return f"Recommandation for {self.demande}"



# SystèmeIA model
class SystemeIA(models.Model):
    historique_demandes = models.ManyToManyField(DemandeConge, related_name="systeme_ia_histories")

    def analyser_charge_travail(self):
        # Analyze workload based on historique_demandes
        pass

    def donner_recommandation(self, demande):
        # Generate a recommendation based on demande details
        pass
