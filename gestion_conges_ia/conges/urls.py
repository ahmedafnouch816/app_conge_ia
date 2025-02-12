from django.urls import path
from .views import   AddDemandeCongeView, DeleteDemandeCongeView, DemandeCongeDetailView, LoginApi, RegisterApi,AddEmployeeView, UpdateDemandeCongeView,UpdateEmployeeView,DeleteEmployeeView,EmployeeDetailView
#from rest_framework_simplejwt import views as jwt_views  # Ajout de cet import


urlpatterns = [
    path('api/register', RegisterApi.as_view(), name='auth_register'),
    path('api/login', LoginApi.as_view(), name="login"),
  
    
    # api de employee 
    
    path('api/employees/add/', AddEmployeeView.as_view(), name='add_employee'),
    path('api/employees/update/<int:pk>/', UpdateEmployeeView.as_view(), name='update_employee'),
    path('api/employees/delete/<int:pk>/', DeleteEmployeeView.as_view(), name='delete_employee'),
    path('api/employees/details/<int:pk>/', EmployeeDetailView.as_view(), name='employee_details'),
    
    # api de demande de conge 
    
    path('api/demande-conge/add/', AddDemandeCongeView.as_view(), name='add-demande-conge'),
    path('api/update-conge/update/<int:pk>/', UpdateDemandeCongeView.as_view(), name='update-demande-conge'),
    path('api/demande_conge/delete/<int:pk>/', DeleteDemandeCongeView.as_view(), name='delete_demande_conge'),
    path('api/demande_conge/detail/<int:pk>/', DemandeCongeDetailView.as_view(), name='demande_conge_detail'),



]