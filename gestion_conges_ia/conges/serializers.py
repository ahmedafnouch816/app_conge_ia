from rest_framework import serializers
from .models import *

class UserSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = ['email','password','first_name','last_name','role']
    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
    
    
class VerifyAccountSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField()

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    
    
# partie empolyee
        
# serializers.py
from rest_framework import serializers
from .models import Employe

class EmployeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employe
        fields = ['nom', 'prenom', 'departement', 'poste', 'solde_de_conge']
        extra_kwargs = {
            'solde_de_conge': {'required': True}
        }





#####################
