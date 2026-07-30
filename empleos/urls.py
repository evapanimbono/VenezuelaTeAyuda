from django.urls import path
from . import views

urlpatterns = [
    path('api/registrar-empresa/', views.registrar_empresa, name='registrar_empresa'),
    path('api/registrar-candidato/', views.registrar_candidato, name='registrar_candidato'),
    
    path('api/login/', views.iniciar_sesion, name='login'),
    path('api/logout/', views.cerrar_sesion, name='logout'),
    path('api/candidato/perfil/', views.perfil_candidato, name='perfil_candidato'), #Vista para ver y actualizar perfil candidato
    path('api/empresa/perfil/', views.perfil_empresa, name='perfil_empresa'), #Vista para ver y actualizar perfil empresa

    path('api/ofertas/crear/', views.registrar_oferta, name='crear_oferta'), #Vista para registrar oferta
    path('api/ofertas/', views.listar_ofertas, name='listar_ofertas'), #Vista para listar todas las ofertas disponibles
    path('api/empresa/postulaciones/', views.ver_postulaciones_recibidas, name='empresa_postulaciones'), #Vista para mostrar a una empresa las postulaciones recibidas
    path('api/postulaciones/<int:postulacion_id>/estatus/', views.cambiar_estatus_postulacion, name='cambiar_estatus'), #Vista para que una empresa pueda aceptar o rechazar una postulacion

    path('api/ofertas/<int:oferta_id>/postularse/', views.postularse_a_oferta, name='postularse'), #Vista para que un candidato se postule a una oferta
    path('api/mis-postulaciones/', views.ver_mis_postulaciones, name='mis_postulaciones'), #Vista para que un candidato vea la lista de sus postulaciones
]