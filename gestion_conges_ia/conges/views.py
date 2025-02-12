from rest_framework.views import APIView 
from rest_framework.generics import RetrieveUpdateAPIView,CreateAPIView
from rest_framework.response import Response
from .serializers import   DemandeCongeSerializer, EmployeSerializer, User,UserSerializer,LoginSerializer
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser
from django.core import serializers
from rest_framework import status
import json
from rest_framework.permissions import AllowAny

from .models import DemandeConge, Employe
from rest_framework.generics import DestroyAPIView,RetrieveAPIView
from rest_framework import generics, permissions

from rest_framework.authtoken.models import Token  # Add this import
from django.contrib.auth.models import User  # Import the User model
from django.contrib.auth import get_user_model
from rest_framework.authentication import TokenAuthentication


something_went_wrong = "something went wrong",
User = get_user_model()

class LoginApi(CreateAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                email = serializer.validated_data['email']
                password = serializer.validated_data['password']

                # Check if the email exists
                if not User.objects.filter(email=email).exists():
                    return Response({
                        'status': 404,
                        'message': 'Email not found',
                        'data': {}
                    }, status=status.HTTP_404_NOT_FOUND)

                user = authenticate(email=email, password=password)
                if user is None:
                    return Response({
                        'status': 400,
                        'message': 'Invalid email or password',
                        'data': {}
                    }, status=status.HTTP_400_BAD_REQUEST)

                # Generate or get the token for the user
                token, created = Token.objects.get_or_create(user=user)

                user_data = {
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name
                }

                return Response({
                    'token': token.key,
                    'user': user_data
                }, status=status.HTTP_200_OK)

            # Handle invalid serializer
            return Response({
                'status': 400,
                'message': 'Invalid data',
                'data': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                'status': 500,
                'message': 'Something went wrong',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
class RegisterApi(APIView):
    serializer_class = UserSerializer

    def post(self, request):
        try:
            data = request.data
            serializer = self.serializer_class(data=data)

            if serializer.is_valid():
                serializer.save()
                return Response({
                    'status': 200,
                    'message': 'Registration successful, check your email.',
                    'data': serializer.data,
                }, status=status.HTTP_200_OK)

            return Response({
                'status': 400,
                'message': 'Something went wrong.',
                'data': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            # Log the exception or handle it
            return Response({
                'status': 500,
                'message': 'An error occurred while processing your request.',
                'error': str(e),
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
##################################################################################          

#partie employee
class AddEmployeeView(CreateAPIView):
    authentication_classes = [TokenAuthentication]  # Authentification via Token
    queryset = Employe.objects.all()
    serializer_class = EmployeSerializer

    def post(self, request, *args, **kwargs):
        # Récupérer le token depuis l'en-tête Authorization
        auth_header = request.headers.get('Authorization')
        
        if not auth_header or not auth_header.startswith("Token "):
            return Response({
                'status': 401,
                'message': 'Token non fourni ou format invalide.',
            }, status=status.HTTP_401_UNAUTHORIZED)

        token_key = auth_header.split(" ")[1]  # Extraire la clé du token

        try:
            token = Token.objects.get(key=token_key)
            user = token.user  # Récupérer l'utilisateur lié au token
        except Token.DoesNotExist:
            return Response({
                'status': 401,
                'message': 'Token invalide.',
            }, status=status.HTTP_401_UNAUTHORIZED)

        # Ajouter l'utilisateur authentifié aux données reçues
        data = request.data.copy()
        data['user'] = user.id  # Associer le user

        serializer = self.get_serializer(data=data)

        if serializer.is_valid():
            serializer.save(user=user)
            return Response({
                'status': 201,
                'message': 'Employé créé avec succès.',
                'data': serializer.data,
            }, status=status.HTTP_201_CREATED)

        return Response({
            'status': 400,
            'message': 'Les données envoyées sont invalides.',
            'errors': serializer.errors,
        }, status=status.HTTP_400_BAD_REQUEST)


#update empolyee
class UpdateEmployeeView(RetrieveUpdateAPIView):
    authentication_classes = [TokenAuthentication]  # Authentification par token
    queryset = Employe.objects.all()
    serializer_class = EmployeSerializer

    def get_object(self):
        """ Retrieve the employee instance by ID """
        return self.get_queryset().get(id=self.kwargs['pk'])

    def put(self, request, *args, **kwargs):
        """ Handle the PUT request to update the employee """
        # Vérifier l'authentification
        if not request.user.is_authenticated:
            return Response({
                'status': 401,
                'message': 'Authentification requise.',
            }, status=status.HTTP_401_UNAUTHORIZED)

        employee = self.get_object()
        serializer = self.serializer_class(employee, data=request.data, partial=False)

        if serializer.is_valid():
            serializer.save()
            return Response({
                'status': 200,
                'message': 'Employee updated successfully',
                'data': serializer.data
            }, status=status.HTTP_200_OK)

        return Response({
            'status': 400,
            'message': 'Invalid data',
            'data': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, *args, **kwargs):
        """ Partially update the employee (fields like name, email, etc.) """
        # Vérifier l'authentification
        if not request.user.is_authenticated:
            return Response({
                'status': 401,
                'message': 'Authentification requise.',
            }, status=status.HTTP_401_UNAUTHORIZED)

        employee = self.get_object()
        serializer = self.serializer_class(employee, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({
                'status': 200,
                'message': 'Employee updated successfully',
                'data': serializer.data
            }, status=status.HTTP_200_OK)

        return Response({
            'status': 400,
            'message': 'Invalid data',
            'data': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


# delete employee
class DeleteEmployeeView(DestroyAPIView):
    authentication_classes = [TokenAuthentication]  # Authentification par token
    queryset = Employe.objects.all()
    serializer_class = EmployeSerializer

    def get_object(self):
        """ Retrieve the employee instance by ID """
        return self.get_queryset().get(id=self.kwargs['pk'])

    def delete(self, request, *args, **kwargs):
        """ Handle the DELETE request to remove the employee """
        # Vérifier l'authentification
        if not request.user.is_authenticated:
            return Response({
                'status': 401,
                'message': 'Authentification requise.',
            }, status=status.HTTP_401_UNAUTHORIZED)

        employee = self.get_object()
        employee.delete()
        return Response({
            'status': 200,
            'message': 'Employee deleted successfully',
        }, status=status.HTTP_200_OK)

        
        
# liste employee     
class EmployeeDetailView(RetrieveAPIView):
    authentication_classes = [TokenAuthentication]  # Authentification par token
    queryset = Employe.objects.all()
    serializer_class = EmployeSerializer

    def get_object(self):
        """ Retrieve the employee instance by ID """
        return self.get_queryset().get(id=self.kwargs['pk'])

##################################################################################

class AddDemandeCongeView(APIView):
    authentication_classes = [TokenAuthentication]
    #permission_classes = [IsAuthenticated]  # Seuls les utilisateurs authentifiés peuvent créer une demande

    def post(self, request):
        try:
            employe = Employe.objects.get(user=request.user)  # Récupérer l'employé lié à l'utilisateur

            data = request.data.copy()
            data['employe'] = employe.id  # Associer l'employé à la demande

            serializer = DemandeCongeSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'status': 201,
                    'message': 'Demande de congé soumise avec succès.',
                    'data': serializer.data
                }, status=status.HTTP_201_CREATED)
            
            return Response({
                'status': 400,
                'message': 'Données invalides.',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except Employe.DoesNotExist:
            return Response({
                'status': 403,
                'message': 'Vous n\'êtes pas un employé autorisé à soumettre une demande de congé.'
            }, status=status.HTTP_403_FORBIDDEN)
            


class UpdateDemandeCongeView(APIView):
    authentication_classes = [TokenAuthentication]
    #permission_classes = [IsAuthenticated]  # Ensuring only authenticated users can update requests

    def get_object(self, pk):
        try:
            return DemandeConge.objects.get(id=pk)
        except DemandeConge.DoesNotExist:
            return None

    def put(self, request, pk):
        """ Handle the PUT request to update an existing leave request """
        demande_conge = self.get_object(pk)
        if not demande_conge:
            return Response({
                'status': 404,
                'message': 'Demande de congé non trouvée.',
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Check if the authenticated user is the one who created the leave request
        if demande_conge.employe.user != request.user:
            return Response({
                'status': 403,
                'message': 'Vous ne pouvez pas modifier cette demande de congé.',
            }, status=status.HTTP_403_FORBIDDEN)

        # Prepare the fields to be updated (you can restrict updates to specific fields)
        updated_data = {
            "date_debut": request.data.get("date_debut", demande_conge.date_debut),
            "date_fin": request.data.get("date_fin", demande_conge.date_fin),
            "type_conge": request.data.get("type_conge", demande_conge.type_conge),
            "statut": request.data.get("statut", demande_conge.statut),
        }

        # Validate and update only those fields
        serializer = DemandeCongeSerializer(demande_conge, data=updated_data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({
                'status': 200,
                'message': 'Demande de congé mise à jour avec succès.',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        
        return Response({
            'status': 400,
            'message': 'Données invalides.',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
        
        
        
class DeleteDemandeCongeView(APIView):
    authentication_classes = [TokenAuthentication]  # Authentication via Token
    #permission_classes = [IsAuthenticated]  # Only authenticated users can delete

    def get_object(self, pk):
        """ Retrieve the DemandeConge instance by ID """
        try:
            return DemandeConge.objects.get(id=pk)
        except DemandeConge.DoesNotExist:
            return None

    def delete(self, request, pk):
        """ Handle the DELETE request to remove a leave request """
        demande_conge = self.get_object(pk)
        
        if not demande_conge:
            return Response({
                'status': 404,
                'message': 'Demande de congé non trouvée.',
            }, status=status.HTTP_404_NOT_FOUND)

        # Check if the authenticated user is the one who created the leave request
        if demande_conge.employe.user != request.user:
            return Response({
                'status': 403,
                'message': 'Vous ne pouvez pas supprimer cette demande de congé.',
            }, status=status.HTTP_403_FORBIDDEN)

        # Delete the leave request
        demande_conge.delete()
        return Response({
            'status': 200,
            'message': 'Demande de congé supprimée avec succès.',
        }, status=status.HTTP_200_OK)
        
        
class DemandeCongeDetailView(APIView):
    authentication_classes = [TokenAuthentication]  # Authentication via Token
    #permission_classes = [IsAuthenticated]  # Only authenticated users can access the details

    def get_object(self, pk):
        """ Retrieve the DemandeConge instance by ID """
        try:
            return DemandeConge.objects.get(id=pk)
        except DemandeConge.DoesNotExist:
            return None

    def get(self, request, pk):
        """ Handle the GET request to retrieve a specific leave request details """
        demande_conge = self.get_object(pk)

        if not demande_conge:
            return Response({
                'status': 404,
                'message': 'Demande de congé non trouvée.',
            }, status=status.HTTP_404_NOT_FOUND)

        # Check if the authenticated user is the one who created the leave request
        if demande_conge.employe.user != request.user:
            return Response({
                'status': 403,
                'message': 'Vous ne pouvez pas accéder à cette demande de congé.',
            }, status=status.HTTP_403_FORBIDDEN)

        # Serialize the leave request data
        serializer = DemandeCongeSerializer(demande_conge)

        return Response({
            'status': 200,
            'message': 'Détails de la demande de congé récupérés avec succès.',
            'data': serializer.data
        }, status=status.HTTP_200_OK)