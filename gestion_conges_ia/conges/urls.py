from django.urls import path
from .views import   LoginApi, RegisterApi,AddEmployeeView,UpdateEmployeeView,DeleteEmployeeView,EmployeeDetailView
#from rest_framework_simplejwt import views as jwt_views  # Ajout de cet import


urlpatterns = [
    path('api/register', RegisterApi.as_view(), name='auth_register'),
    path('api/login', LoginApi.as_view(), name="login"),
  
    
    # add employee 
    
    path('api/employees/add/', AddEmployeeView.as_view(), name='add_employee'),
    path('api/employees/update/<int:pk>/', UpdateEmployeeView.as_view(), name='update_employee'),
    path('api/employees/delete/<int:pk>/', DeleteEmployeeView.as_view(), name='delete_employee'),
    path('api/employees/details/<int:pk>/', EmployeeDetailView.as_view(), name='employee_details'),
    



]