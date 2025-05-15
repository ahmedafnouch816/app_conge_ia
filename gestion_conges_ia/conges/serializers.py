from rest_framework import serializers
from .models import *

class EmployeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employe
        fields = ['nom', 'prenom', 'departement', 'poste', 'solde_de_conge']



# User Serializer
class UserSerializer(serializers.ModelSerializer):
    departement = serializers.CharField(write_only=True, required=False)  
    poste = serializers.CharField(write_only=True, required=False)  
    solde_de_conge = serializers.IntegerField(write_only=True, required=False, default=0)  

    class Meta:
        model = User
        fields = ['id','email','password','first_name','last_name','role']
        fields = ['email', 'password', 'first_name', 'last_name', 'role', 'departement', 'poste', 'solde_de_conge']
        extra_kwargs = {
            'password': {'write_only': True},  # Ensure password is write-only
            'role': {'required': True}
        }

    def create(self, validated_data):
        departement = validated_data.pop('departement', "")
        poste = validated_data.pop('poste', "")
        solde_de_conge = validated_data.pop('solde_de_conge', 0)

        # ✅ Correctly hash the password
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)  # Hash password before saving
        user.save()

        # ✅ Ensure Employe object is created only once
        Employe.objects.create(
            user=user,
            nom=user.first_name,
            prenom=user.last_name,
            departement=departement,
            poste=poste,
            solde_de_conge=solde_de_conge
        )

        return user

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
#class EmployeSerializer(serializers.ModelSerializer):
#    class Meta:
#        model = Employe
#        fields = ['nom', 'prenom', 'departement', 'poste', 'solde_de_conge']
#        extra_kwargs = {
#            'solde_de_conge': {'required': True}
#        }

#####################

class DemandeCongeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DemandeConge
        fields = ['id', 'employe', 'date_debut', 'date_fin', 'type_conge', 'statut']

class LeaveAccrualRecordSerializer(serializers.ModelSerializer):
    month_name = serializers.SerializerMethodField()
    employe_name = serializers.SerializerMethodField()
    
    class Meta:
        model = LeaveAccrualRecord
        fields = ['id', 'employe', 'employe_name', 'month', 'month_name', 'year', 
                 'workable_days', 'days_worked', 'leave_accrued', 'is_finalized', 
                 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_month_name(self, obj):
        import calendar
        return calendar.month_name[obj.month]
    
    def get_employe_name(self, obj):
        return f"{obj.employe.prenom} {obj.employe.nom}"

#class VerifyAccountSerializer(serializers.Serializer):
#    email = serializers.EmailField()
#    otp = serializers.CharField()