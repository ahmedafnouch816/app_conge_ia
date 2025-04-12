from django.urls import path
from .views import   AddDemandeCongeView, DeleteDemandeCongeView, DemandeCongeDetailView, DemandesCongeParEmployeView, EmployeListAPIView, GetRecommandationView, GetRecommandationsByEmployeView, ListDemandeCongeView, LoginApi, PasswordResetConfirmView, PasswordResetRequestView, RegisterApi, UpdateDemandeCongeView,UpdateEmployeeView,DeleteEmployeeView,EmployeeDetailView
#from rest_framework_simplejwt import views as jwt_views  # Ajout de cet import


urlpatterns = [
    path('api/register', RegisterApi.as_view(), name='auth_register'),
    path('api/login', LoginApi.as_view(), name="login"),
    path('api/password-reset/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('reset-password/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    
    # api de employee 
    
    #path('api/employees/add/', AddEmployeeView.as_view(), name='add_employee'),
    path('api/employees/update/<int:pk>/', UpdateEmployeeView.as_view(), name='update_employee'),
    path('api/employees/delete/<int:pk>/', DeleteEmployeeView.as_view(), name='delete_employee'),
    path('api/employees/details/<int:pk>/', EmployeeDetailView.as_view(), name='employee_details'),
    path('api/employes/', EmployeListAPIView.as_view(), name='employe-list'),
    path("api/demandes-conge/employe/<int:employe_id>/", DemandesCongeParEmployeView.as_view(), name="demandes-conge-par-employe"),


    # api de demande de conge 
    
    path('api/demande-conge/add/', AddDemandeCongeView.as_view(), name='add-demande-conge'),
    path('api/update-conge/update/<int:pk>/', UpdateDemandeCongeView.as_view(), name='update-demande-conge'),
    path('api/demande-conge/delete/<int:pk>/', DeleteDemandeCongeView.as_view(), name='delete_demande_conge'),
    path('api/demande-conge/detail/<int:pk>/', DemandeCongeDetailView.as_view(), name='demande_conge_detail'),
    path('api/demandes_conge/', ListDemandeCongeView.as_view(), name='list-demande-conge'),



    # api get recommendations 
    path('api/demande-conge/recommandation/<int:demande_id>/', GetRecommandationView.as_view(), name='get_recommandation'), # demande seul
    path('api/recommandations/employe/<int:employe_id>/', GetRecommandationsByEmployeView.as_view(), name='get_recommandations_by_employe'), # all recomnadations 
 




]