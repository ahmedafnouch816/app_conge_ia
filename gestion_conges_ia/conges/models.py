from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

from .ml_utils import MODEL_PATH
from .manager import UserManager

# SystèmeIA 
import numpy as np



    
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


# DemandeDeCongé model

class DemandeConge(models.Model):
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('approuve', 'Approuvé'),
        ('rejete', 'Rejeté'),
    ]

    TYPE_CONGE_CHOICES = [
        ('maternite', 'Congé de maternité'),
        ('maladie', 'Congé de maladie'),
        ('paye', 'Congé payé'),
        ('paternite', 'Congé de paternité'),
        ('occasionnel', 'Congé occasionnel'),
    ]
    
    employe = models.ForeignKey('Employe', on_delete=models.CASCADE, related_name="demandes")
    #responsable = models.ForeignKey('Responsable', on_delete=models.CASCADE)
    date_debut = models.DateField()
    date_fin = models.DateField()
    type_conge = models.CharField(max_length=20, choices=TYPE_CONGE_CHOICES)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    #employe = models.OneToOneField('SystemeIA', on_delete=models.CASCADE, related_name="employe")

    def valider(self):
        self.statut = "approuve"
        self.save()

    def refuser(self):
        self.statut = "rejete"
        self.save()

    def __str__(self):
        return f"{self.employe} - {self.date_debut} à {self.date_fin} ({dict(self.TYPE_CONGE_CHOICES).get(self.type_conge)})"


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




class EmployeeWorkloadFile(models.Model):
    """
    Modèle pour stocker les fichiers Excel uploadés.
    """
    file = models.FileField(upload_to='workload_files/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Workload file uploaded at {self.uploaded_at}"




# Responsable model    
#class Responsable(models.Model):
#    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profil_responsable")
#    nom = models.CharField(max_length=100, primary_key=True)  # or any other unique field
#    prenom = models.CharField(max_length=100)
#    def approuver_demande(self, demande):
#        demande.statut = "approuve"
#        demande.save()
#
#    def consulter_recommandation(self, demande):
#        return demande.recommandations.all()
#
#    def __str__(self):
#        return self.user.get_full_name()



#class SystemeIA(models.Model):
#    historique_demandes = models.ManyToManyField(DemandeConge, related_name="systeme_ia_histories")
#
#    def predire_charge_travail(self, annee, periode_analyse):
#        """
#        Prédit la charge de travail en fonction de l'année et de la période.
#        """
#        MODEL_PATH = os.path.join(settings.BASE_DIR, "workload_model.pkl")
#
#        if not os.path.exists(MODEL_PATH):
#            print("Erreur : Modèle non trouvé !")
#            return None  
#
#        try:
#            with open(MODEL_PATH, 'rb') as f:
#                model = pickle.load(f)
#
#            X_input = np.array([[annee, periode_analyse]])
#            prediction = model.predict(X_input)[0]  
#            print(f"Charge prédite : {prediction}")  # Debug
#            return prediction
#
#        except Exception as e:
#            print(f"Erreur lors de la prédiction : {str(e)}")
#            return None
