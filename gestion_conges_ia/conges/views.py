from rest_framework.views import APIView
from rest_framework.generics import RetrieveUpdateAPIView, CreateAPIView
from rest_framework.response import Response
from .serializers import (
    DemandeCongeSerializer,
    EmployeSerializer,
    User,
    UserSerializer,
    LoginSerializer,
)
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.permissions import AllowAny
from .models import DemandeConge, Employe, Recommandation
from rest_framework.generics import DestroyAPIView, RetrieveAPIView , ListAPIView
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
from django.shortcuts import render
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
            data = request.data
            serializer = self.serializer_class(data=data)

            if serializer.is_valid():
                serializer.save()
                return Response(
                    {
                        "status": 200,
                        "message": "Registration successful, check your email.",
                        "data": serializer.data,
                    },
                    status=status.HTTP_200_OK,
                )

            return Response(
                {
                    "status": 400,
                    "message": "Something went wrong.",
                    "data": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        except Exception as e:
            # Log the exception or handle it
            return Response(
                {
                    "status": 500,
                    "message": "An error occurred while processing your request.",
                    "error": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


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
    authentication_classes = [TokenAuthentication]  # Authentification par token
    queryset = Employe.objects.all()
    serializer_class = EmployeSerializer

    def get_object(self):
        """Retrieve the employee instance by ID"""
        return self.get_queryset().get(id=self.kwargs["pk"])

    def delete(self, request, *args, **kwargs):
        """Handle the DELETE request to remove the employee"""
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
    # permission_classes = [IsAuthenticated]  # Ensuring only authenticated users can update requests

    def get_object(self, pk):
        try:
            return DemandeConge.objects.get(id=pk)
        except DemandeConge.DoesNotExist:
            return None

    def put(self, request, pk):
        """Handle the PUT request to update an existing leave request"""
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
                    "message": "Vous ne pouvez pas modifier cette demande de congé.",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        # Prepare the fields to be updated (you can restrict updates to specific fields)
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
    required_columns = ["Période_analyse", "solde_restant", "Charge_de_travail"]

    if not all(col in data.columns for col in required_columns):
        raise ValueError(
            f"Le fichier Excel doit contenir les colonnes suivantes : {required_columns}"
        )

    if data["Charge_de_travail"].isna().any():
        raise ValueError(
            "La colonne 'Charge_de_travail' contient des valeurs manquantes."
        )

    months_map = {
        "Janvier": 1,
        "Février": 2,
        "Mars": 3,
        "Avril": 4,
        "Mai": 5,
        "Juin": 6,
        "Juillet": 7,
        "Août": 8,
        "Septembre": 9,
        "Octobre": 10,
        "Novembre": 11,
        "Décembre": 12,
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

    X = data[["solde_restant", "Période_analyse"]]
    y = data["Charge_de_travail"]

    # Diviser en train et test
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))

    # Sauvegarde du modèle
    model_path = "workload_model.pkl"
    with open(model_path, "wb") as f:
        pickle.dump(model, f)

    return model, f"Modèle entraîné avec succès. RMSE: {rmse:.2f}"


# Fonction pour prédire la charge de travail
def predict_workload(annee, periode):
    model_path = "workload_model.pkl"

    if not os.path.exists(model_path):
        model, message = train_workload_model()
        if not model:
            return None, message
    else:
        with open(model_path, "rb") as f:
            model = pickle.load(f)

    prediction = model.predict([[annee, periode]])[0]

    # Déterminer la recommandation
    if prediction > 75:
        statut_recommande = "approuve"  # Accepté
    elif 50 <= prediction <= 75:
        statut_recommande = "en_attente"  # En attente
    else:
        statut_recommande = "rejete"  # Refusé

    return prediction, statut_recommande


# API pour soumettre une demande de congé avec prédiction de charge de travail
class AddDemandeCongeView(APIView):
    authentication_classes = [TokenAuthentication]

    def post(self, request):
        try:
            # Étape 1: Récupérer l'employé
            employe = Employe.objects.get(user=request.user)
            data = request.data.copy()
            data["employe"] = employe.id

            # Étape 2: Valider les données
            serializer = DemandeCongeSerializer(data=data)
            if serializer.is_valid():
                demande = serializer.save()

                # Étape 3: Prédire la charge de travail
                annee = demande.date_debut.year
                periode = demande.date_debut.month

                prediction, statut_recommande = predict_workload(annee, periode)

                if prediction is None:
                    return Response(
                        {"error": statut_recommande}, status=status.HTTP_400_BAD_REQUEST
                    )

                # Étape 4: Sauvegarder la recommandation
                Recommandation.objects.create(
                    demande=demande, score=prediction, statut=statut_recommande
                )

                return Response(
                    {
                        "status": 201,
                        "message": "Demande de congé soumise avec succès.",
                        "data": serializer.data,
                        "prediction": prediction,
                        "recommandation": statut_recommande,
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
