from django.db import models
from django.contrib.auth.models import AbstractUser

# 1. Modelo de Usuario Personalizado (Maneja el rol)
class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('candidato', 'Candidato'),
        ('empresa', 'Empresa / Empleador'),
        ('admin', 'Administrador'),
    )
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='candidato')

    # Usamos el email para iniciar sesión en lugar del username nativo
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    groups = models.ManyToManyField('auth.Group', related_name='custom_user_set', blank=True)
    user_permissions = models.ManyToManyField('auth.Permission', related_name='custom_user_permissions_set', blank=True)

    def __str__(self):
        return f"{self.email} ({self.get_role_display()})"

# 2. Control de Códigos de Acceso (ONGs)
class CodigoAcceso(models.Model):
    codigo = models.CharField(max_length=50, unique=True)
    nombre_ong = models.CharField(max_length=150)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.codigo} - {self.nombre_ong}"

# 3. Perfil del Candidato (Datos protegidos)
class CandidatoProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='candidato_profile')
    documento_identidad = models.CharField(max_length=30, unique=True)
    telefono = models.CharField(max_length=30)
    estado = models.CharField(max_length=100, default='Distrito Capital')
    municipio_parroquia = models.CharField(max_length=150)
    descripcion_habilidades = models.TextField(help_text="CV sencillo o resumen de lo que sabes hacer")
    codigo_ong = models.ForeignKey(CodigoAcceso, on_delete=models.SET_NULL, null=True, blank=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"Candidato: {self.user.first_name} {self.user.last_name}"

# 4. Perfil de la Empresa
class EmpresaProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='empresa_profile')
    nombre_empresa = models.CharField(max_length=150)
    identificacion_fiscal = models.CharField(max_length=50, help_text="RIF, NIT, NIF o número de registro legal de la empresa")
    web_o_redes = models.URLField(max_length=200, blank=True, null=True)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return self.nombre_empresa

# 5. Tabla de Ofertas de Empleo (Lo que publican las empresas)
class OfertaEmpleo(models.Model):
    MODALIDAD_CHOICES = (
        ('Presencial', 'Presencial'),
        ('Remoto', 'Remoto'),
    )
    
    empresa = models.ForeignKey(EmpresaProfile, on_delete=models.CASCADE, related_name='ofertas')
    titulo = models.CharField(max_length=150)
    descripcion = models.TextField()
    area_trabajo = models.CharField(max_length=100, help_text="Ej. Atención al cliente, Administración, Oficios")
    
    estado = models.CharField(max_length=100, help_text="Estado de Venezuela donde se ubica el empleo", blank=True, null=True)
    municipio = models.CharField(max_length=100, help_text="Municipio donde se ubica el empleo", blank=True, null=True)
    
    salario = models.CharField(max_length=50, blank=True, null=True)
    modalidad = models.CharField(max_length=20, choices=MODALIDAD_CHOICES, default='Presencial')
    requisitos = models.TextField(help_text="Separados por comas o líneas")
    fecha_publicacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.titulo} - {self.empresa.nombre_empresa}"

# 6. Tabla de Postulaciones (Une candidatos con ofertas y maneja los estados)
class Postulacion(models.Model):
    STATUS_CHOICES = (
        ('pendiente', 'Pendiente'),
        ('aceptada', 'Aceptada'),
        ('rechazada', 'Rechazada'),
    )
    oferta = models.ForeignKey(OfertaEmpleo, on_delete=models.CASCADE, related_name='postulaciones')
    candidato = models.ForeignKey(CandidatoProfile, on_delete=models.CASCADE, related_name='postulaciones')
    fecha_postulacion = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendiente')

    class Meta:
        # Evita que un mismo candidato postule dos veces a la misma oferta
        unique_together = ('oferta', 'candidato')

    def __str__(self):
        nombre_usuario = f"{self.candidato.user.first_name} {self.candidato.user.last_name}".strip()
        identificador = nombre_usuario if nombre_usuario else self.candidato.user.email
        return f"{identificador} -> {self.oferta.titulo} ({self.status})"

