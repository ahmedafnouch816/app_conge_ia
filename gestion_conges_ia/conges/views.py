from rest_framework.views import APIView 
from rest_framework.generics import RetrieveUpdateAPIView,CreateAPIView
from rest_framework.response import Response
from .serializers import   EmployeSerializer, User,UserSerializer,LoginSerializer
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
            
            

#partie employee



class AddEmployeeView(CreateAPIView):
    # permission_classes = [IsAuthenticated]  # Supprimé
    authentication_classes = [TokenAuthentication]
    queryset = Employe.objects.all()
    serializer_class = EmployeSerializer

    def post(self, request, *args, **kwargs):
        user = request.user

        if not user.is_authenticated:
            return Response({
                'status': 401,
                'message': 'Vous devez être connecté pour créer un employé.',
            }, status=status.HTTP_401_UNAUTHORIZED)

        request.data['user'] = user.id

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
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
    queryset = Employe.objects.all()
    serializer_class = EmployeSerializer

    def get_object(self):
        """ Retrieve the employee instance by ID """
        return self.get_queryset().get(id=self.kwargs['pk'])

    def put(self, request, *args, **kwargs):
        """ Handle the PUT request to update the employee """
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



class DeleteEmployeeView(DestroyAPIView):
    queryset = Employe.objects.all()
    serializer_class = EmployeSerializer

    def get_object(self):
        """ Retrieve the employee instance by ID """
        return self.get_queryset().get(id=self.kwargs['pk'])

    def delete(self, request, *args, **kwargs):
        """ Handle the DELETE request to remove the employee """
        employee = self.get_object()
        employee.delete()
        return Response({
            'status': 200,
            'message': 'Employee deleted successfully',
        }, status=status.HTTP_200_OK)
        
        
        
class EmployeeDetailView(RetrieveAPIView):
    queryset = Employe.objects.all()
    serializer_class = EmployeSerializer

    def get_object(self):
        """ Retrieve the employee instance by ID """
        return self.get_queryset().get(id=self.kwargs['pk'])
    
#################
