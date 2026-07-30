import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from .models import (CustomUser, EmpresaProfile ,CodigoAcceso, 
                    CandidatoProfile, OfertaEmpleo, EmpresaProfile,
                    OfertaEmpleo, CandidatoProfile, Postulacion)

@csrf_exempt  # Temporalmente eximimos de CSRF para que React pueda enviar datos sin problemas
def registrar_empresa(request):
    # Solo permitimos peticiones de tipo POST (para enviar datos)
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido. Usa POST.'}, status=405)
    
    try:
        # 1. Leer los datos que vienen desde el frontend (React)
        datos = json.loads(request.body)
        
        email = datos.get('email')
        password = datos.get('password')
        nombre_empresa = datos.get('nombre_empresa')
        identificacion_fiscal = datos.get('identificacion_fiscal')
        web_o_redes = datos.get('web_o_redes') 
        is_approved = datos.get('is_approved', False)

        # 2. Validaciones básicas
        if not email or not password or not nombre_empresa or not identificacion_fiscal:
            return JsonResponse({'error': 'Faltan campos obligatorios'}, status=400)

        if CustomUser.objects.filter(email=email).exists():
            return JsonResponse({'error': 'Este correo ya está registrado'}, status=400)

        # 3. Crear el Usuario Principal (CustomUser) con el rol de empresa
        # Usamos make_password para que la contraseña se guarde encriptada y segura
        nuevo_usuario = CustomUser.objects.create(
            username=email,  # Django exige un username, usamos el email
            email=email,
            password=make_password(password),
            role='empresa'
        )

        # 4. Crear el perfil específico de la Empresa amarrado a ese usuario
        perfil_empresa = EmpresaProfile.objects.create(
            user=nuevo_usuario,
            nombre_empresa=nombre_empresa,
            identificacion_fiscal=identificacion_fiscal,
            web_o_redes=web_o_redes,
            is_approved=is_approved
        )

        # 5. Responder al frontend que todo salió perfecto
        return JsonResponse({
            'mensaje': 'Empresa registrada con éxito',
            'usuario_id': nuevo_usuario.id,
            'empresa_nombre': perfil_empresa.nombre_empresa
        }, status=201)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Datos JSON inválidos'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'Error en el servidor: {str(e)}'}, status=500)

@csrf_exempt
def registrar_candidato(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido. Usa POST.'}, status=405)
    
    try:
        datos = json.loads(request.body)
        
        # 1. Capturar datos del JSON (incluyendo los de Django y los del perfil)
        email = datos.get('email')
        password = datos.get('password')
        first_name = datos.get('first_name')  # Columna nativa de Django
        last_name = datos.get('last_name')    # Columna nativa de Django
        documento_identidad = datos.get('documento_identidad')
        telefono = datos.get('telefono')
        estado = datos.get('estado')
        municipio_parroquia = datos.get('municipio_parroquia')
        descripcion_habilidades = datos.get('descripcion_habilidades')
        codigo_ong = datos.get('codigo_ong')

        # 2. Validaciones obligatorias
        if not email or not password or not first_name or not last_name or not documento_identidad or not codigo_ong:
            return JsonResponse({'error': 'Faltan campos obligatorios'}, status=400)

        if CustomUser.objects.filter(email=email).exists():
            return JsonResponse({'error': 'Este correo ya está registrado'}, status=400)

        # 3. Validar el Código de la ONG
        try:
            ong_vinculada = CodigoAcceso.objects.get(codigo=codigo_ong, is_active=True)
        except CodigoAcceso.DoesNotExist:
            return JsonResponse({'error': 'El código de acceso de la ONG no es válido o está inactivo'}, status=400)

        # 4. Crear el Usuario Principal con sus campos nativos rellenos
        nuevo_usuario = CustomUser.objects.create(
            username=email,
            email=email,
            password=make_password(password),
            first_name=first_name,  # ¡Aquí se guarda el nombre!
            last_name=last_name,    # ¡Aquí se guarda el apellido!
            role='candidato'
        )

        # 5. Crear el Perfil del Candidato amarrado a la ONG validada
        perfil_candidato = CandidatoProfile.objects.create(
            user=nuevo_usuario,
            documento_identidad=documento_identidad,
            telefono=telefono,
            estado=estado,
            municipio_parroquia=municipio_parroquia,
            descripcion_habilidades=descripcion_habilidades,
            codigo_ong=ong_vinculada
        )

        return JsonResponse({
            'mensaje': 'Candidato registrado con éxito',
            'usuario_id': nuevo_usuario.id,
            'nombre_completo': f"{nuevo_usuario.first_name} {nuevo_usuario.last_name}",
            'ong_asociada': ong_vinculada.nombre_ong
        }, status=201)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Datos JSON inválidos'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'Error en el servidor: {str(e)}'}, status=500)

@csrf_exempt
def iniciar_sesion(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido. Usa POST.'}, status=405)
    
    try:
        datos = json.loads(request.body)
        email = datos.get('email')
        password = datos.get('password')

        # 1. Validar que vengan ambos campos
        if not email or not password:
            return JsonResponse({'error': 'Email y contraseña son obligatorios'}, status=400)

        # 2. Autenticar al usuario
        # Django busca internamente por 'username', pero como guardamos el email ahí, le pasamos el email.
        usuario = authenticate(request, username=email, password=password)

        if usuario is not None:
            if usuario.is_active:
                # 3. Iniciar la sesión oficialmente en el servidor
                login(request, usuario)
                
                # 4. Responder a React con el rol para que sepa a qué pantalla mandarlo
                return JsonResponse({
                    'mensaje': 'Inicio de sesión exitoso',
                    'usuario_id': usuario.id,
                    'email': usuario.email,
                    'role': usuario.role,  # 'empresa' o 'candidato'
                    'nombre': usuario.first_name 
                }, status=200)
            else:
                return JsonResponse({'error': 'Esta cuenta está desactivada'}, status=403)
        else:
            # Por seguridad, usamos un mensaje genérico (no decimos si lo que falló fue el correo o la clave)
            return JsonResponse({'error': 'Credenciales inválidas. Revisa tu correo y contraseña.'}, status=401)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Datos JSON inválidos'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'Error en el servidor: {str(e)}'}, status=500)

@csrf_exempt
def cerrar_sesion(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido. Usa POST.'}, status=405)
    
    # Django destruye la sesión actual del usuario automáticamente
    logout(request)
    
    return JsonResponse({'mensaje': 'Sesión cerrada con éxito'}, status=200)

#Vista para registrar o crear una oferta de empleo
@csrf_exempt
def registrar_oferta(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido. Usa POST.'}, status=405)
    
    # 1. Seguridad: Verificar que el usuario esté autenticado y sea una empresa
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Debes iniciar sesión para publicar una oferta'}, status=401)
        
    if request.user.role != 'empresa':
        return JsonResponse({'error': 'Acceso denegado. Solo las empresas pueden publicar ofertas.'}, status=403)
    
    try:
        datos = json.loads(request.body)
        
        # 2. Capturar los datos del JSON (Modificado para usar estado y municipio)
        titulo = datos.get('titulo')
        descripcion = datos.get('descripcion')
        area_trabajo = datos.get('area_trabajo')
        estado = datos.get('estado') 
        municipio = datos.get('municipio')
        salario = datos.get('salario', 'A convenir')
        modalidad = datos.get('modalidad', 'Presencial')
        requisitos = datos.get('requisitos')

        # 3. Validaciones obligatorias
        if not titulo or not descripcion or not area_trabajo or not estado or not municipio or not requisitos:
            return JsonResponse({'error': 'Faltan campos obligatorios para la oferta (asegúrate de incluir estado y municipio).'}, status=400)

        # 4. Buscar el perfil de la empresa que está logueada
        try:
            perfil_empresa = request.user.empresa_profile
        except EmpresaProfile.DoesNotExist:
            return JsonResponse({'error': 'No se encontró el perfil de empresa para este usuario'}, status=404)

        # 5. Crear la Oferta de Empleo amarrada a esa empresa
        nueva_oferta = OfertaEmpleo.objects.create(
            empresa=perfil_empresa,
            titulo=titulo,
            descripcion=descripcion,
            area_trabajo=area_trabajo,
            estado=estado,
            municipio=municipio,
            salario=salario,
            modalidad=modalidad,
            requisitos=requisitos
        )

        return JsonResponse({
            'mensaje': 'Oferta de empleo publicada con éxito',
            'oferta_id': nueva_oferta.id,
            'titulo': nueva_oferta.titulo,
            'empresa': perfil_empresa.nombre_empresa
        }, status=201)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Datos JSON inválidos'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'Error en el servidor: {str(e)}'}, status=500)

#Vista para mostrar una lista de todas las ofertas disponibles
@csrf_exempt
def listar_ofertas(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Método no permitido. Usa GET.'}, status=405)
    
    try:
        ofertas = OfertaEmpleo.objects.all().order_by('-fecha_publicacion')
        
        # Conseguimos el perfil del candidato de forma ultra segura
        perfil_candidato = None
        if request.user and request.user.is_authenticated:
            if getattr(request.user, 'role', '') == 'candidato':
                try:
                    perfil_candidato = request.user.candidato_profile
                except Exception:
                    perfil_candidato = None

        lista_ofertas = []
        for o in ofertas:
            ya_postulado = False
            if perfil_candidato:
                ya_postulado = Postulacion.objects.filter(oferta=o, candidato=perfil_candidato).exists()

            # 💡 Construimos un texto de respaldo por si el front viejo aún busca 'ubicacion'
            ubicacion_fallback = f"{o.municipio}, {o.estado}" if o.estado else "No especificada"

            lista_ofertas.append({
                'id': o.id,
                'titulo': o.titulo,
                'descripcion': o.descripcion,
                'area_trabajo': o.area_trabajo,
                'estado': o.estado,          
                'municipio': o.municipio,   
                'ubicacion': ubicacion_fallback,
                'salario': o.salario,
                'modalidad': o.modalidad,
                'requisitos': o.requisitos,
                'fecha_publicacion': o.fecha_publicacion.strftime('%d/%m/%Y'),
                'empresa': {
                    'id': o.empresa.id,
                    'nombre': o.empresa.nombre_empresa,
                    'web': o.empresa.web_o_redes
                },
                'ya_postulado': ya_postulado
            })
            
        return JsonResponse(lista_ofertas, safe=False, status=200)

    except Exception as e:
        print(f"ERROR EN LISTAR_OFERTAS: {str(e)}")
        return JsonResponse({'error': f'Error en el servidor: {str(e)}'}, status=500)

#Vista para mostrar a una empresa la lista de postulaciones a ofertas de empleo recibidas
@csrf_exempt
def ver_postulaciones_recibidas(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Método no permitido. Usa GET.'}, status=405)
        
    if not request.user.is_authenticated or request.user.role != 'empresa':
        return JsonResponse({'error': 'Acceso denegado. Solo empresas autenticadas.'}, status=403)
        
    try:
        empresa_perfil = request.user.empresa_profile
        # Buscamos todas las postulaciones cuyas ofertas pertenezcan a esta empresa
        postulaciones = Postulacion.objects.filter(oferta__empresa=empresa_perfil).order_by('-fecha_postulacion')
        
        data = []
        for p in postulaciones:
            nombre_completo_django = f"{p.candidato.user.first_name} {p.candidato.user.last_name}".strip()
            
            data.append({
                'postulacion_id': p.id,
                'oferta_titulo': p.oferta.titulo,
                'candidato_nombre': nombre_completo_django if nombre_completo_django else p.candidato.user.email,
                'candidato_email': p.candidato.user.email,
                'fecha_postulacion': p.fecha_postulacion.strftime('%d/%m/%Y'),
                'status': p.status
            })
            
        return JsonResponse(data, safe=False, status=200)
    except Exception as e:
        return JsonResponse({'error': f'Error en el servidor: {str(e)}'}, status=500)

#Vista para que una empresa cambie el estatus (pendiente-> aceptar/rechazar) a una postulacion recibida
@csrf_exempt
def cambiar_estatus_postulacion(request, postulacion_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido. Usa POST.'}, status=405)
        
    if not request.user.is_authenticated or request.user.role != 'empresa':
        return JsonResponse({'error': 'Acceso denegado. Solo empresas.'}, status=403)
        
    try:
        # 1. Verificar que la postulación exista y pertenezca a las ofertas de esta empresa
        try:
            postulacion = Postulacion.objects.get(id=postulacion_id, oferta__empresa=request.user.empresa_profile)
        except Postulacion.DoesNotExist:
            return JsonResponse({'error': 'Postulación no encontrada o no tienes permisos sobre ella.'}, status=404)
            
        # 2. Leer el nuevo estado enviado (desde el botón de React)
        import json
        body = json.loads(request.body)
        nuevo_status = body.get('status')
        
        # 3. Validar que sea uno de los estados que definiste en tu modelo
        if nuevo_status not in ['aceptada', 'rechazada']:
            return JsonResponse({'error': 'Estado inválido. Usa "aceptada" o "rechazada".'}, status=400)
            
        # 4. Actualizar y guardar en Neon
        postulacion.status = nuevo_status
        postulacion.save()
        
        return JsonResponse({
            'mensaje': f'Postulación actualizada a {nuevo_status} con éxito.',
            'postulacion_id': postulacion.id,
            'status': postulacion.status
        }, status=200)
        
    except Exception as e:
        return JsonResponse({'error': f'Error en el servidor: {str(e)}'}, status=500)

#Vista para que un candidato postule a una oferta de empleo
@csrf_exempt
def postularse_a_oferta(request, oferta_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido. Usa POST.'}, status=405)
    
    # 1. Seguridad: Verificar autenticación
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Debes iniciar sesión para postularte'}, status=401)
        
    if request.user.role != 'candidato':
        return JsonResponse({'error': 'Acceso denegado. Solo los candidatos pueden postularse.'}, status=403)
    
    try:
        # 2. Verificar que la oferta de empleo exista
        try:
            oferta = OfertaEmpleo.objects.get(id=oferta_id)
        except OfertaEmpleo.DoesNotExist:
            return JsonResponse({'error': 'La oferta de empleo no existe.'}, status=404)
        
        # 3. Obtener el perfil de candidato del usuario logueado
        try:
            perfil_candidato = request.user.candidato_profile
        except CandidatoProfile.DoesNotExist:
            return JsonResponse({'error': 'No se encontró el perfil de candidato para este usuario.'}, status=404)
            
        # 4. Verificar si ya se había postulado antes (para evitar errores feos de base de datos)
        if Postulacion.objects.filter(oferta=oferta, candidato=perfil_candidato).exists():
            return JsonResponse({'error': 'Ya te has postulado a esta oferta de empleo anteriormente.'}, status=400)
            
        # 5. Crear la postulación
        nueva_postulacion = Postulacion.objects.create(
            oferta=oferta,
            candidato=perfil_candidato
        )
        
        return JsonResponse({
            'mensaje': '¡Postulación exitosa!',
            'postulacion_id': nueva_postulacion.id,
            'oferta': oferta.titulo,
            'status': nueva_postulacion.status
        }, status=201)
        
    except Exception as e:
        return JsonResponse({'error': f'Error en el servidor: {str(e)}'}, status=500)

#Vista para mostrar a un candidato la lista de sus postulaciones
@csrf_exempt
def ver_mis_postulaciones(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Método no permitido. Usa GET.'}, status=405)
        
    if not request.user.is_authenticated or request.user.role != 'candidato':
        return JsonResponse({'error': 'Acceso denegado. Solo candidatos autenticados.'}, status=403)
        
    try:
        perfil = request.user.candidato_profile
        # Buscamos todas las postulaciones de este perfil
        mis_postulaciones = Postulacion.objects.filter(candidato=perfil).order_by('-fecha_postulacion')
        
        data = []
        for p in mis_postulaciones:
            data.append({
                'postulacion_id': p.id,
                'oferta_id': p.oferta.id,
                'titulo_empleo': p.oferta.titulo,
                'empresa': p.oferta.empresa.nombre_empresa,
                'fecha_postulacion': p.fecha_postulacion.strftime('%d/%m/%Y'),
                'status': p.status
            })
            
        return JsonResponse(data, safe=False, status=200)
    except Exception as e:
        return JsonResponse({'error': f'Error en el servidor: {str(e)}'}, status=500)

#Vista para ver y actualizar datos (permitidos) del perfil del candidato
@csrf_exempt
def perfil_candidato(request):
    if not request.user.is_authenticated or request.user.role != 'candidato':
        return JsonResponse({'error': 'Acceso denegado. Solo para candidatos.'}, status=403)
        
    try:
        usuario = request.user
        perfil = request.user.candidato_profile
        
        if request.method == 'GET':
            return JsonResponse({
                'nombre': usuario.first_name,
                'apellido': usuario.last_name,
                'email': usuario.email,
                'documento_identidad': getattr(perfil, 'documento_identidad', ''), 
                'telefono': getattr(perfil, 'telefono', ''),
                'estado': getattr(perfil, 'estado', ''),
                'municipio_parroquia': getattr(perfil, 'municipio_parroquia', ''),
                'descripcion_habilidades': getattr(perfil, 'descripcion_habilidades', '')
            }, status=200)
            
        elif request.method == 'POST':
            import json
            body = json.loads(request.body)
            
            usuario.first_name = body.get('nombre', usuario.first_name)
            usuario.last_name = body.get('apellido', usuario.last_name)
            usuario.save()
            
            perfil.telefono = body.get('telefono', getattr(perfil, 'telefono', ''))
            perfil.estado = body.get('estado', getattr(perfil, 'estado', ''))
            perfil.municipio_parroquia = body.get('municipio_parroquia', getattr(perfil, 'municipio_parroquia', ''))
            perfil.descripcion_habilidades = body.get('descripcion_habilidades', getattr(perfil, 'descripcion_habilidades', ''))
            perfil.save()
            
            return JsonResponse({'mensaje': '¡Perfil de candidato actualizado con éxito!'}, status=200)
            
        else:
            return JsonResponse({'error': 'Método no permitido. Usa GET o POST.'}, status=405)
            
    except Exception as e:
        return JsonResponse({'error': f'Error en el servidor: {str(e)}'}, status=500)

#Vista para ver y actualizar datos (permitidos) del perfil de la empres
@csrf_exempt
def perfil_empresa(request):
    # Seguridad: Solo empresas autenticadas
    if not request.user.is_authenticated or request.user.role != 'empresa':
        return JsonResponse({'error': 'Acceso denegado. Solo para empresas.'}, status=403)
        
    try:
        usuario = request.user
        perfil = request.user.empresa_profile
        
        # CASO 1: LEER DATOS (GET)
        if request.method == 'GET':
            return JsonResponse({
                'nombre_usuario': usuario.first_name, # Persona de contacto
                'apellido_usuario': usuario.last_name,
                'email': usuario.email,
                'nombre_empresa': getattr(perfil, 'nombre_empresa', ''),
                'identificacion_fiscal': getattr(perfil, 'identificacion_fiscal', ''),
                'web_o_redes': getattr(perfil, 'web_o_redes', ''),
            }, status=200)
            
        # CASO 2: ACTUALIZAR DATOS (POST)
        elif request.method == 'POST':
            import json
            body = json.loads(request.body)
            
            # 1. Modificar datos del usuario (Representante de la empresa)
            usuario.first_name = body.get('nombre_usuario', usuario.first_name)
            usuario.last_name = body.get('apellido_usuario', usuario.last_name)
            usuario.save()
            
            # 2. Modificar datos de la Empresa (Usa tus nombres exactos de campos)
            perfil.nombre_empresa = body.get('nombre_empresa', getattr(perfil, 'nombre_empresa', ''))
            perfil.web_o_redes = body.get('web_o_redes', getattr(perfil, 'web_o_redes', ''))
            perfil.save()
            
            return JsonResponse({'mensaje': '¡Perfil de empresa actualizado con éxito!'}, status=200)
            
        else:
            return JsonResponse({'error': 'Método no permitido. Usa GET o POST.'}, status=405)
            
    except Exception as e:
        return JsonResponse({'error': f'Error en el servidor: {str(e)}'}, status=500)
