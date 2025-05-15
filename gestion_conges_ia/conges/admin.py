from django.contrib import admin
from conges.models import User, Employe, DemandeConge, Recommandation, EmployeeWorkloadFile, LeaveAccrualRecord

# Register your models here.
admin.site.register(User)
admin.site.register(Employe)
admin.site.register(DemandeConge)
admin.site.register(Recommandation)
admin.site.register(EmployeeWorkloadFile)
admin.site.register(LeaveAccrualRecord)
