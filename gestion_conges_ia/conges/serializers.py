from rest_framework import serializers
from .models import *

class UserSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = ['id','email','password','first_name','last_name','role']
        extra_kwargs = {
            'role': {'required': True}
        }
    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
    
    
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    

# serializers.py
from rest_framework import serializers
from .models import Employe

class EmployeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employe
        fields = ['id','nom', 'prenom', 'departement', 'poste', 'solde_de_conge']
        extra_kwargs = {
            'solde_de_conge': {'required': True}
        }

#####################

class DemandeCongeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DemandeConge
        fields = ['id', 'employe', 'date_debut', 'date_fin', 'type_conge', 'statut']





#class VerifyAccountSerializer(serializers.Serializer):
#    email = serializers.EmailField()
#    otp = serializers.CharField()