from rest_framework.views import APIView
from rest_framework.generics import RetrieveUpdateAPIView, CreateAPIView, ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from .serializers import (
    DemandeCongeSerializer,
    EmployeSerializer,
    User,
    UserSerializer,
    LoginSerializer,
    LeaveAccrualRecordSerializer,
)
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.permissions import AllowAny
from .models import DemandeConge, Employe, Recommandation, LeaveAccrualRecord
from rest_framework.generics import DestroyAPIView, RetrieveAPIView, ListAPIView
from rest_framework.authtoken.models import Token  # Add this import
from django.contrib.auth.models import User  # Import the User model
from django.contrib.auth import get_user_model
from rest_framework.authentication import TokenAuthentication

#
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
import pickle
from django.shortcuts import get_object_or_404, render
from .models import EmployeeWorkloadFile
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import os

#

from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils.http import urlsafe_base64_decode

from rest_framework import generics
from rest_framework.serializers import ModelSerializer
from django.db import transaction, IntegrityError

from .models import LeaveAccrualRecord
from .serializers import LeaveAccrualRecordSerializer
from .utils.leave_accrual import update_or_create_accrual_record
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from dateutil.relativedelta import relativedelta

something_went_wrong = ("something went wrong",)
User = get_user_model()


class LoginApi(CreateAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                email = serializer.validated_data["email"]
                password = serializer.validated_data["password"]

                # Check if the email exists
                if not User.objects.filter(email=email).exists():
                    return Response(
                        {"status": 404, "message": "Email not found", "data": {}},
                        status=status.HTTP_404_NOT_FOUND,
                    )

                user = authenticate(email=email, password=password)
                if user is None:
                    return Response(
                        {
                            "status": 400,
                            "message": "Invalid email or password",
                            "data": {},
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                # Generate or get the token for the user
                token, created = Token.objects.get_or_create(user=user)

                user_data = {
                    "id": user.id,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "role": user.role,
                }

                return Response(
                    {"token": token.key, "user": user_data}, status=status.HTTP_200_OK
                )

            # Handle invalid serializer
            return Response(
                {"status": 400, "message": "Invalid data", "data": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        except Exception as e:
            return Response(
                {"status": 500, "message": "Something went wrong", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
class RegisterApi(APIView):
    serializer_class = UserSerializer

    def post(self, request):
        try:
            serializer = self.serializer_class(data=request.data)

            if serializer.is_valid():
                user = serializer.save()

                return Response(
                    {
                        "status": 200,
                        "message": "Inscription réussie.",
                        "data": {
                            "user": serializer.data,
                            "employe": EmployeSerializer(user.profil_employe).data  # Get related Employe data
                        },
                    },
                    status=status.HTTP_201_CREATED,  # Use 201 for resource creation
                )

            return Response(
                {
                    "status": 400,
                    "message": "Erreur lors de l'inscription.",
                    "errors": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        except Exception as e:
            return Response(
                {
                    "status": 500,
                    "message": "Une erreur est survenue.",
                    "error": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


#class RegisterApi(APIView):
#    serializer_class = UserSerializer
#
#    def post(self, request):
#        try:
#            data = request.data
#            serializer = self.serializer_class(data=data)
#
#            if serializer.is_valid():
#                serializer.save()
#                return Response(
#                    {
#                        "status": 200,
#                        "message": "Registration successful, check your email.",
#                        "data": serializer.data,
#                    },
#                    status=status.HTTP_200_OK,
#                )
#
#            return Response(
#                {
#                    "status": 400,
#                    "message": "Something went wrong.",
#                    "data": serializer.errors,
#                },
#                status=status.HTTP_400_BAD_REQUEST,
#            )
#
#        except Exception as e:
#            # Log the exception or handle it
#            return Response(
#                {
#                    "status": 500,
#                    "message": "An error occurred while processing your request.",
#                    "error": str(e),
#                },
#                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
#            )
#

# rest password
class PasswordResetRequestView(APIView):
    def post(self, request):
        email = request.data.get("email")
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"message": "User with this email does not exist."},
                status=status.HTTP_404_NOT_FOUND,
            )

        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        reset_url = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}/"

        # Send email
        send_mail(
            subject="Password Reset Request",
            message=f"Click the link to reset your password: {reset_url}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
        )

        return Response(
            {"message": "Password reset email sent."}, status=status.HTTP_200_OK
        )


class PasswordResetConfirmView(APIView):
    def post(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError):
            return Response(
                {"message": "Invalid token or user does not exist."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not default_token_generator.check_token(user, token):
            return Response(
                {"message": "Invalid or expired token."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        new_password = request.data.get("password")
        user.set_password(new_password)
        user.save()

        return Response(
            {"message": "Password reset successful."}, status=status.HTTP_200_OK
        )


##################################################################################


# partie employee
class AddEmployeeView(CreateAPIView):
    authentication_classes = [TokenAuthentication]  # Authentification via Token
    queryset = Employe.objects.all()
    serializer_class = EmployeSerializer

    def post(self, request, *args, **kwargs):
        # Récupérer le token depuis l'en-tête Authorization
        auth_header = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Token "):
            return Response(
                {
                    "status": 401,
                    "message": "Token non fourni ou format invalide.",
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        token_key = auth_header.split(" ")[1]  # Extraire la clé du token

        try:
            token = Token.objects.get(key=token_key)
            user = token.user  # Récupérer l'utilisateur lié au token
        except Token.DoesNotExist:
            return Response(
                {
                    "status": 401,
                    "message": "Token invalide.",
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Ajouter l'utilisateur authentifié aux données reçues
        data = request.data.copy()
        data["user"] = user.id  # Associer le user

        serializer = self.get_serializer(data=data)

        if serializer.is_valid():
            serializer.save(user=user)
            return Response(
                {
                    "status": 201,
                    "message": "Employé créé avec succès.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {
                "status": 400,
                "message": "Les données envoyées sont invalides.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


# update empolyee
class UpdateEmployeeView(RetrieveUpdateAPIView):
    authentication_classes = [TokenAuthentication]  # Authentification par token
    queryset = Employe.objects.all()
    serializer_class = EmployeSerializer

    def get_object(self):
        """Retrieve the employee instance by ID"""
        return self.get_queryset().get(id=self.kwargs["pk"])

    def put(self, request, *args, **kwargs):
        """Handle the PUT request to update the employee"""
        # Vérifier l'authentification
        if not request.user.is_authenticated:
            return Response(
                {
                    "status": 401,
                    "message": "Authentification requise.",
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        employee = self.get_object()
        serializer = self.serializer_class(employee, data=request.data, partial=False)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "status": 200,
                    "message": "Employee updated successfully",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {"status": 400, "message": "Invalid data", "data": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def patch(self, request, *args, **kwargs):
        """Partially update the employee (fields like name, email, etc.)"""
        # Vérifier l'authentification
        if not request.user.is_authenticated:
            return Response(
                {
                    "status": 401,
                    "message": "Authentification requise.",
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        employee = self.get_object()
        serializer = self.serializer_class(employee, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "status": 200,
                    "message": "Employee updated successfully",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {"status": 400, "message": "Invalid data", "data": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )


# delete employee
class DeleteEmployeeView(DestroyAPIView):
    authentication_classes = [TokenAuthentication]
    queryset = Employe.objects.all()
    serializer_class = EmployeSerializer

    def get_object(self):
        pk = self.kwargs.get("pk")
        try:
            return self.get_queryset().get(id=pk)
        except (Employe.DoesNotExist, ValueError, TypeError):
            return None

    def delete(self, request, *args, **kwargs):
        if not request.user or not request.user.is_authenticated:
            return Response(
                {
                    "status": 401,
                    "message": "Authentification requise.",
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )
        employee = self.get_object()
        if not employee:
            return Response(
                {
                    "status": 404,
                    "message": "Employé non trouvé.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        employee.delete()
        return Response(
            {
                "status": 200,
                "message": "Employee deleted successfully",
            },
            status=status.HTTP_200_OK,
        )

# liste employee
class EmployeeDetailView(RetrieveAPIView):
    authentication_classes = [TokenAuthentication]  # Authentification par token
    queryset = Employe.objects.all()
    serializer_class = EmployeSerializer

    def get_object(self):
        """Retrieve the employee instance by ID"""
        return self.get_queryset().get(id=self.kwargs["pk"])


# get all employees
class EmployeListAPIView(ListAPIView):
    authentication_classes = [TokenAuthentication]  # Authentification par token
    queryset = Employe.objects.all()
    serializer_class = EmployeSerializer


##################################################################################


class UpdateDemandeCongeView(APIView):
    authentication_classes = [TokenAuthentication]

    def get_object(self, pk):
        try:
            return DemandeConge.objects.get(id=pk)
        except DemandeConge.DoesNotExist:
            return None

    def put(self, request, pk):
        """Handle the PUT request to update an existing leave request"""
        # Check if user is authenticated
        if not request.user or not request.user.is_authenticated:
            return Response(
                {
                    "status": 401,
                    "message": "Authentification requise.",
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )
            
        demande_conge = self.get_object(pk)
        if not demande_conge:
            return Response(
                {
                    "status": 404,
                    "message": "Demande de congé non trouvée.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )


        if demande_conge.employe.user != request.user:
            return Response(
                {
                    "status": 403,
                    "message": "Vous ne pouvez pas modifier cette demande de congé.",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        # Prepare the fields to be updated
        updated_data = {
            "date_debut": request.data.get("date_debut", demande_conge.date_debut),
            "date_fin": request.data.get("date_fin", demande_conge.date_fin),
            "type_conge": request.data.get("type_conge", demande_conge.type_conge),
            "statut": request.data.get("statut", demande_conge.statut),
        }

        # Validate and update only those fields
        serializer = DemandeCongeSerializer(
            demande_conge, data=updated_data, partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "status": 200,
                    "message": "Demande de congé mise à jour avec succès.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "status": 400,
                "message": "Données invalides.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class DeleteDemandeCongeView(APIView):
    authentication_classes = [TokenAuthentication]  # Authentication via Token
    # permission_classes = [IsAuthenticated]  # Only authenticated users can delete

    def get_object(self, pk):
        """Retrieve the DemandeConge instance by ID"""
        try:
            return DemandeConge.objects.get(id=pk)
        except DemandeConge.DoesNotExist:
            return None

    def delete(self, request, pk):
        """Handle the DELETE request to remove a leave request"""
        demande_conge = self.get_object(pk)

        if not demande_conge:
            return Response(
                {
                    "status": 404,
                    "message": "Demande de congé non trouvée.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # Check if the authenticated user is the one who created the leave request
        if demande_conge.employe.user != request.user:
            return Response(
                {
                    "status": 403,
                    "message": "Vous ne pouvez pas supprimer cette demande de congé.",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        # Delete the leave request
        demande_conge.delete()
        return Response(
            {
                "status": 200,
                "message": "Demande de congé supprimée avec succès.",
            },
            status=status.HTTP_200_OK,
        )


class DemandeCongeDetailView(APIView):
    authentication_classes = [TokenAuthentication]  # Authentication via Token
    # permission_classes = [IsAuthenticated]  # Only authenticated users can access the details

    def get_object(self, pk):
        """Retrieve the DemandeConge instance by ID"""
        try:
            return DemandeConge.objects.get(id=pk)
        except DemandeConge.DoesNotExist:
            return None

    def get(self, request, pk):
        """Handle the GET request to retrieve a specific leave request details"""
        demande_conge = self.get_object(pk)

        if not demande_conge:
            return Response(
                {
                    "status": 404,
                    "message": "Demande de congé non trouvée.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # Check if the authenticated user is the one who created the leave request
        if demande_conge.employe.user != request.user:
            return Response(
                {
                    "status": 403,
                    "message": "Vous ne pouvez pas accéder à cette demande de congé.",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        # Serialize the leave request data
        serializer = DemandeCongeSerializer(demande_conge)

        return Response(
            {
                "status": 200,
                "message": "Détails de la demande de congé récupérés avec succès.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    # Charger les données depuis un fichier Excel


###################################################################################

# Fonction pour charger les données depuis un fichier Excel
def load_data(filepath):
    data = pd.read_excel(filepath)
    required_columns = [
        "Période_analyse", "Solde_restant_de_conges", "Charge_de_travail", "priorite_de_conge", "Taux_d_absenteisme"
    ]

    if not all(col in data.columns for col in required_columns):
        raise ValueError(
            f"Le fichier Excel doit contenir les colonnes suivantes : {required_columns}"
        )

    if data["Charge_de_travail"].isna().any():
        raise ValueError(
            "La colonne 'Charge_de_travail' contient des valeurs manquantes."
        )

    months_map = {
        "Janvier": 1, "Février": 2, "Mars": 3, "Avril": 4, "Mai": 5, "Juin": 6,
        "Juillet": 7, "Août": 8, "Septembre": 9, "Octobre": 10, "Novembre": 11, "Décembre": 12,
    }

    data["Période_analyse"] = data["Période_analyse"].map(months_map)
    return data



# Fonction pour entraîner le modèle et sauvegarder le fichier
def train_workload_model():
    # Récupérer le dernier fichier uploadé
    last_file = EmployeeWorkloadFile.objects.last()
    if not last_file:
        return None, "Aucun fichier de données disponible."

    filepath = last_file.file.path

    try:
        data = load_data(filepath)
    except Exception as e:
        return None, f"Erreur lors de la lecture du fichier : {str(e)}"

    # Ajouter les nouvelles caractéristiques (features)
    X = data[["Solde_restant_de_conges", "Période_analyse", "priorite_de_conge", "Taux_d_absenteisme"]]
    y = data["Charge_de_travail"]

    # Diviser en train et test
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Entraîner le modèle avec les nouvelles caractéristiques
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    

    # Sauvegarde du modèle
    model_path = "workload_model.pkl"
    with open(model_path, "wb") as f:
        pickle.dump(model, f)

    return model, f"Modèle entraîné avec succès. RMSE: {rmse:.2f}"


# Fonction pour prédire la charge de travail (Modèle de Prédiction)
def predict_workload(annee, periode, taux_d_absenteisme):
    model_path = "workload_model.pkl"

    if not os.path.exists(model_path):
        model, message = train_workload_model()
        if not model:
            return None, message
    else:
        with open(model_path, "rb") as f:
            model = pickle.load(f)

    # Assurez-vous de ne passer que les 2 caractéristiques attendues par le modèle
    prediction = model.predict([[taux_d_absenteisme, periode]])[0]  # 2 caractéristiques : taux_d_absenteisme et periode

    return prediction  # Retournons juste la prédiction, pas un tuple



# Fonction pour scorer la charge de travail (Modèle de Scoring)
def score_workload(prediction):
    # Déterminer la recommandation en fonction de la prédiction
    if prediction > 75:
        statut_recommande = "approuve"  # Accepté
    elif 50 <= prediction <= 75:
        statut_recommande = "en_attente"  # En attente
    else:
        statut_recommande = "rejete"  # Refusé

    return statut_recommande


# Fonction combinée pour prédiction et scoring
def predict_and_score_workload(annee, periode, taux_d_absenteisme):
    prediction = predict_workload(annee, periode, taux_d_absenteisme)
    if prediction is not None:
        statut_recommande = score_workload(prediction)
        return prediction, statut_recommande
    else:
        return None, "Erreur lors de la prédiction"



class AddDemandeCongeView(APIView):
    authentication_classes = [TokenAuthentication]

    def post(self, request):
        try:
            # Étape 1: Récupérer l'employé
            employe = Employe.objects.get(user=request.user)
            data = request.data.copy()
            data["employe"] = employe.id

            # Étape 2: Valider les données de la demande de congé
            serializer = DemandeCongeSerializer(data=data)
            if serializer.is_valid():
                demande = serializer.save()

                # Étape 3: Prédire la charge de travail
                annee = demande.date_debut.year
                periode = demande.date_debut.month

                # Utilisation du solde de congé comme taux d'absentéisme
                taux_d_absenteisme = employe.solde_de_conge / 100  # Exemple de taux d'absentéisme basé sur le solde de congé

                # Appeler la fonction combinée pour obtenir la prédiction et le statut recommandé
                prediction, statut_recommande = predict_and_score_workload(annee, periode, taux_d_absenteisme)

                # Si la prédiction échoue
                if prediction is None:
                    return Response(
                        {"error": statut_recommande}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # Étape 4: Sauvegarder la recommandation
                Recommandation.objects.create(
                    demande=demande, 
                    employe=employe,
                    score=prediction,  # Nous avons la prédiction
                    statut=statut_recommande  # Et le statut recommandé
                )

                return Response(
                    {
                        "status": 201,
                        "message": "Demande de congé soumise avec succès.",
                        "data": serializer.data,
                        "prediction": prediction,
                        "statut_recommande": statut_recommande,
                    },
                    status=status.HTTP_201_CREATED,
                )

            return Response(
                {
                    "status": 400,
                    "message": "Données invalides.",
                    "errors": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        except Employe.DoesNotExist:
            return Response(
                {"status": 403, "message": "Employé non autorisé."},
                status=status.HTTP_403_FORBIDDEN,
            )



# end pont de recuperes data de recommendations
class GetRecommandationView(APIView):
    authentication_classes = [
        TokenAuthentication
    ]  # ✅ Utilisation de TokenAuthentication
    # permission_classes = [IsAuthenticated]  # 🔒 Seuls les utilisateurs authentifiés peuvent accéder

    def get(self, request, demande_id):
        try:
            recommandation = Recommandation.objects.select_related("demande").get(
                demande_id=demande_id
            )
            return Response(
                {
                    "demande": {
                        "id": recommandation.demande.id,
                        "date_debut": recommandation.demande.date_debut,
                        "date_fin": recommandation.demande.date_fin,
                    },
                    "score": recommandation.score,
                    "statut": recommandation.statut,
                },
                status=status.HTTP_200_OK,
            )
        except Recommandation.DoesNotExist:
            return Response(
                {"error": "Aucune recommandation trouvée pour cette demande."},
                status=status.HTTP_404_NOT_FOUND,
            )




class GetRecommandationsByEmployeView(APIView):
    authentication_classes = [TokenAuthentication]

    def get(self, request, employe_id):
        """Récupérer toutes les recommandations pour un employé donné."""
        employe = get_object_or_404(Employe, id=employe_id)

        # Récupérer toutes les recommandations liées aux demandes de congé de cet employé
        recommandations = Recommandation.objects.filter(demande__employe=employe).select_related("demande")

        if not recommandations.exists():
            return Response(
                {
                    "message": "Aucune recommandation trouvée pour cet employé.",
                    "nombre_demandes": 0,
                    "recommandations": []
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # Organiser les recommandations par demande de congé
        recommandations_data = {}
        for recommandation in recommandations:
            demande_id = recommandation.demande.id
            if demande_id not in recommandations_data:
                recommandations_data[demande_id] = {
                    "demande": {
                        "id": recommandation.demande.id,
                        "date_debut": recommandation.demande.date_debut,
                        "date_fin": recommandation.demande.date_fin,
                        "type_conge": recommandation.demande.type_conge,
                        "statut": recommandation.demande.statut,
                    },
                    "recommandations": []
                }
            recommandations_data[demande_id]["recommandations"].append({
                "score": recommandation.score,
                "statut": recommandation.statut,
            })

        return Response(
            {
                "message": "Recommandations récupérées avec succès.",
                "nombre_demandes": len(recommandations_data),
                "recommandations": list(recommandations_data.values()),
            },
            status=status.HTTP_200_OK,
        )




class DemandesCongeParEmployeView(APIView):
    authentication_classes = [TokenAuthentication]
    #permission_classes = [IsAuthenticated]

    def get(self, request, employe_id):
        """Récupérer toutes les demandes de congé d'un employé spécifique"""
        try:
            employe = Employe.objects.get(id=employe_id)
        except Employe.DoesNotExist:
            return Response(
                {"status": 404, "message": "Employé non trouvé."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Vérifier si l'utilisateur connecté est bien l'employé en question
        if request.user != employe.user:
            return Response(
                {"status": 403, "message": "Accès refusé."},
                status=status.HTTP_403_FORBIDDEN,
            )

        demandes = DemandeConge.objects.filter(employe=employe)
        serializer = DemandeCongeSerializer(demandes, many=True)

        return Response(
            {
                "status": 200,
                "message": "Liste des demandes de congé récupérée avec succès.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )



############

class ListDemandeCongeView(ListAPIView):
    authentication_classes = [TokenAuthentication]  # Add token authentication
    queryset = DemandeConge.objects.all()
    serializer_class = DemandeCongeSerializer
    
    
    
    


class ProfileApi(APIView):
    permission_classes = [IsAuthenticated]  # Ensure the user is authenticated

    def get(self, request):
        try:
            # Get the authenticated user
            user = request.user

            # Serialize the user data
            serializer = UserSerializer(user)

            return Response(
                {
                    "status": 200,
                    "message": "User profile retrieved successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"status": 500, "message": "Something went wrong", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

# Leave Accrual Views
class LeaveAccrualListView(ListAPIView):
    """
    API view to list all leave accrual records.
    Can be filtered by employee, month, and year.
    """
    serializer_class = LeaveAccrualRecordSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        queryset = LeaveAccrualRecord.objects.all()
        
        # Filter by employee if specified
        employee_id = self.request.query_params.get('employee_id')
        if employee_id:
            queryset = queryset.filter(employe_id=employee_id)
        
        # Filter by month if specified
        month = self.request.query_params.get('month')
        if month:
            queryset = queryset.filter(month=month)
        
        # Filter by year if specified
        year = self.request.query_params.get('year')
        if year:
            queryset = queryset.filter(year=year)
            
        # Filter by is_finalized if specified
        is_finalized = self.request.query_params.get('is_finalized')
        if is_finalized is not None and is_finalized != '':
            # Convert string value to boolean
            if is_finalized.lower() == 'true':
                queryset = queryset.filter(is_finalized=True)
            elif is_finalized.lower() == 'false':
                queryset = queryset.filter(is_finalized=False)
        
        return queryset


class LeaveAccrualDetailView(RetrieveAPIView):
    """
    API view to retrieve a specific leave accrual record.
    """
    queryset = LeaveAccrualRecord.objects.all()
    serializer_class = LeaveAccrualRecordSerializer
    permission_classes = [IsAuthenticated]


class CalculateLeaveAccrualView(APIView):
    """
    API view to calculate leave accrual for an employee for a specific month.
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        from conges.utils.leave_accrual import update_or_create_accrual_record
        
        employee_id = request.data.get('employee_id')
        month = request.data.get('month')
        year = request.data.get('year')
        days_worked = request.data.get('days_worked')  # Optional
        finalize = request.data.get('finalize', False)
        
        # Validate required fields
        if not all([employee_id, month, year]):
            return Response(
                {"error": "employee_id, month, and year are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Get the employee
            employe = Employe.objects.get(pk=employee_id)
            
            # Calculate and save accrual
            record = update_or_create_accrual_record(
                employe=employe,
                year=year,
                month=month,
                days_worked=days_worked,
                is_finalized=finalize
            )
            
            # Serialize and return the record
            serializer = LeaveAccrualRecordSerializer(record)
            
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Employe.DoesNotExist:
            return Response(
                {"error": f"Employee with ID {employee_id} does not exist"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class FinalizeLeaveAccrualView(APIView):
    """
    API view to finalize leave accrual records and add them to employee balances.
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        from django.db import transaction
        
        accrual_id = request.data.get('accrual_id')
        
        try:
            # Get the accrual record
            record = LeaveAccrualRecord.objects.get(pk=accrual_id)
            
            # Check if already finalized
            if record.is_finalized:
                return Response(
                    {"error": "Accrual record already finalized"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Finalize the record
            with transaction.atomic():
                # Update employee's leave balance
                record.employe.solde_de_conge += record.leave_accrued
                record.employe.save()
                
                # Mark as finalized
                record.is_finalized = True
                record.save()
            
            # Serialize and return the record
            serializer = LeaveAccrualRecordSerializer(record)
            
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except LeaveAccrualRecord.DoesNotExist:
            return Response(
                {"error": f"Accrual record with ID {accrual_id} does not exist"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )