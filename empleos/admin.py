from django.contrib import admin
from .models import CustomUser, CandidatoProfile, EmpresaProfile, OfertaEmpleo, Postulacion, CodigoAcceso

# Registramos los modelos para que aparezcan en el panel visual
admin.site.register(CustomUser)
admin.site.register(CandidatoProfile)
admin.site.register(EmpresaProfile)
admin.site.register(OfertaEmpleo)
admin.site.register(Postulacion)
admin.site.register(CodigoAcceso)