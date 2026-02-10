from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, JsonResponse, HttpResponseForbidden
from django.urls import reverse
from django.core.mail import BadHeaderError, EmailMultiAlternatives
from .forms import CodigoForm, BusquedaCodigoForm
from .models import CodigoGenerado, SolicitudAnulacion
from django.db import IntegrityError
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
from django.template.loader import render_to_string
from django.utils.timezone import now, localtime
from django.utils.encoding import force_str

@login_required
def home(request):
    nombre_usuario = request.user.get_full_name() or request.user.username
    return render(request, 'home.html', {'nombre_usuario': nombre_usuario})


def signup(request):
    
    if request.method == 'GET':
        return render(request, 'Acceso/signup.html', { 
            'form': UserCreationForm(),                            
        })
    else:
        if request.POST['password1'] == request.POST['password2']:
            #registrar usuario
            print(request.POST['username'])
            print(request.POST['password1'])
            try:
                user = User.objects.create_user(
                    username=request.POST['username'],
                    password=request.POST['password1']
                )
                user.save()
                login(request, user)  # Iniciar sesión automáticamente
                # Redirigir a la página de inicio después del registro exitoso
                return redirect('home')
            except IntegrityError:
                return render(request, 'Acceso/signup.html', { 
                    'form': UserCreationForm(),
                    'error': 'El usuario ya existe'                   
                })
        return render(request, 'signup.html', { 
                'form': UserCreationForm(),
                'error': 'Las contraseñas no coinciden.'                   
                })  

@login_required
def signout(request):
    logout(request)
    return redirect('home')

def IniciarSesion(request):
    if request.method == 'GET':
        return render(request, 'Acceso/login.html', { 
            'form': AuthenticationForm() 
        })
    else:
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'Acceso/login.html', {
                'form': AuthenticationForm(),
                'error': 'Usuario o contraseña incorrectos.'
            })
        else:
            login(request, user)
            # Redirigir a la página de inicio después del inicio de sesión exitoso
            return redirect('home')

@login_required
def generar_codigo(request):
    codigo_generado = None
    resultado_busqueda = None
    error_formulario = None
    mostrar_modal = False
    codigo_previsualizacion = None

    # Búsqueda por código (GET)
    codigo_buscado = request.GET.get('buscar_codigo')
    if codigo_buscado:
        if CodigoGenerado.objects.filter(codigo=codigo_buscado).exists():
            resultado_busqueda = codigo_buscado
        else:
            resultado_busqueda = "no_existe"

    if request.method == 'POST':
        form = CodigoForm(request.POST)

        # Si se hizo clic en "Cancelar" desde el modal
        if "cancelar" in request.POST:
            return render(request, "generador_codigo.html", {
                "form": form,
                "codigo_generado": None,
                "mostrar_modal": False,
                "codigo_previsualizacion": None,
                "error": None
            })

        if form.is_valid():
            empresa = form.cleaned_data['empresa']
            año_completo = form.cleaned_data['año']
            año_dos_digitos = año_completo[-2:]
            numero_proyecto = form.cleaned_data['numero_proyecto']
            subproyecto = form.cleaned_data['subproyecto']
            departamento = form.cleaned_data['departamento']
            disciplina = form.cleaned_data['disciplina']
            tipo_documento = form.cleaned_data['tipo_documento']

            # Filtrar para calcular el consecutivo
            filtro_existente = CodigoGenerado.objects.filter(
                empresa=empresa,
                año=año_completo,
                numero_proyecto=numero_proyecto,
                subproyecto=subproyecto,
                departamento=departamento,
                disciplina=disciplina,
                tipo_documento=tipo_documento
            )
            consecutivo = filtro_existente.count() + 1

            # Generar código completo
            codigo = f"{empresa.sigla}-{año_dos_digitos}-{numero_proyecto}-{subproyecto}-{departamento}-{disciplina}-{tipo_documento}-{consecutivo:03}"

            # Si no hay confirmación todavía, mostramos modal
            if 'confirmar' not in request.POST:
                mostrar_modal = True
                codigo_previsualizacion = codigo
                return render(request, 'generador_codigo.html', {
                    'form': form,
                    'mostrar_modal': mostrar_modal,
                    'codigo_previsualizacion': codigo_previsualizacion,
                    'codigo_generado': None,
                    'error': None
                })

            if 'confirmar' in request.POST:
                motivo = request.POST.get("motivo", "").strip()
                if not motivo:
                    # Reabrir el modal si el motivo no fue ingresado
                    mostrar_modal = True
                    codigo_previsualizacion = request.POST.get("codigo_previsualizacion", "")
                    return render(request, 'generador_codigo.html', {
                        'form': form,
                        'mostrar_modal': mostrar_modal,
                        'codigo_previsualizacion': codigo_previsualizacion,
                        'codigo_generado': None,
                        'error': "El campo de motivo es obligatorio.",
                        'motivo_guardado': motivo,
                    })
            # Si se confirmó, guardamos el código
            try:
                CodigoGenerado.objects.create(
                    empresa=empresa,
                    año=año_completo,
                    numero_proyecto=numero_proyecto,
                    subproyecto=subproyecto,
                    departamento=departamento,
                    disciplina=disciplina,
                    tipo_documento=tipo_documento,
                    consecutivo=consecutivo,
                    codigo=codigo,
                    usuario=request.user,
                    motivo=motivo
                )
                codigo_generado = codigo
                print(f"Nuevo código generado: {codigo}")

                # Normalizamos el nombre de la empresa para seleccionar el logo
                nombre_empresa = empresa.nombre.strip()

                # Asignamos logo específico según nombre
                if nombre_empresa == "SSAPI":
                    logo_empresa = "ssapi.png"
                elif nombre_empresa == "Paldaca":
                    logo_empresa = "PaldacalogoyRif.png"
                elif nombre_empresa == "Orinoco Energy":
                    logo_empresa = "orinoco.png"
                elif nombre_empresa == "Kinetic Scale Projectos":
                    logo_empresa = "ksp.png"
                else:
                    logo_empresa = "PaldacalogoyRif.png"  # Logo por defecto si no coincide ninguna

                print(f"Logo empresa: {logo_empresa}")
                logo_url = f"https://codigos.cpaldaca.com/static_codigos/img/{logo_empresa}"

                usuario = force_str(request.user.username)
                fecha = force_str(localtime(now()).strftime('%d/%m/%Y %H:%M'))
                destino = force_str(empresa.corre_notificacion)
                #destino = 'dasilvas@ssapico.com'
                asunto = force_str('Nuevo Código generado')
                print(f"Enviando correo a {destino} con asunto '{asunto}'")
                
                contexto_email = {
                    'usuario': usuario,
                    'fecha': fecha,
                    'codigo': codigo,
                    'motivo': motivo,
                    'logo_url': logo_url,
                }

                mensaje_texto = f"""
                Se ha generado un nuevo código:
                Usuario: {usuario}
                Fecha: {fecha}
                Código: {codigo}
                Motivo: {motivo}
                """

                mensaje_html = render_to_string('emails/nuevo_codigo.html', contexto_email)

                email = EmailMultiAlternatives(
                    asunto,
                    mensaje_texto,
                    'admin@sari.cpaldaca.com',
                    [destino],
                )
                email.encoding = 'utf-8'
                email.attach_alternative(mensaje_html, "text/html")
                print(f"Enviando correo a {destino} con asunto '{asunto}' en codigo {email.encoding}") 
                email.send(fail_silently=False)
            except BadHeaderError:
                error_formulario = "Error: encabezado de correo inválido."
            except Exception as e:
                error_formulario = f"El código fue generado, pero el correo no pudo enviarse: {e}"
            except Exception as e:
                error_formulario = f"Ocurrió un error al guardar el código: {e}"
        else:
            error_formulario = "Por favor, corrige los errores en el formulario."
    else:
        form = CodigoForm()

    context = {
        'form': form,
        'codigo_generado': codigo_generado,
        'error': error_formulario,
        'mostrar_modal': mostrar_modal,
        'codigo_previsualizacion': codigo_previsualizacion,
        'resultado_busqueda': resultado_busqueda,
    }
    return render(request, 'generador_codigo.html', context)

@login_required
def buscar_codigo(request):
    form = BusquedaCodigoForm(request.GET)
    resultados = CodigoGenerado.objects.none()  # No muestra nada hasta que se busque

    if request.GET and form.is_valid():
        codigo = form.cleaned_data.get('codigo')
        usuario = form.cleaned_data.get('usuario')
        fecha_inicio = form.cleaned_data.get('fecha_inicio')
        fecha_fin = form.cleaned_data.get('fecha_fin')

        resultados = CodigoGenerado.objects.all()

        if codigo:
            resultados = resultados.filter(codigo__icontains=codigo)
        if usuario:
            resultados = resultados.filter(usuario=usuario)
        if fecha_inicio:
            resultados = resultados.filter(fecha_creacion__gte=fecha_inicio)
        if fecha_fin:
            fecha_fin = datetime.combine(fecha_fin, datetime.max.time())
            resultados = resultados.filter(fecha_creacion__lte=fecha_fin)

        incluir_anulados = request.GET.get('ver_anulados') == 'on'
        if not incluir_anulados:
            resultados = resultados.filter(anulado=False)

    return render(request, 'buscar_codigo.html', {
        'form': form,
        'resultados': resultados
    })
@login_required
def lista_codigos(request):
    mostrar_todos = request.GET.get('todos')

    codigos = CodigoGenerado.objects.select_related('usuario').order_by('-fecha_creacion')
    if not mostrar_todos:
        codigos = codigos[:15]

    # Obtener las solicitudes de anulación pendientes del usuario actual
    solicitudes_pendientes = SolicitudAnulacion.objects.filter(
        solicitante=request.user,
        procesada=False
    ).values_list('codigo_id', flat=True)

    return render(request, 'lista_codigos.html', {
        'codigos': codigos,
        'mostrar_todos': mostrar_todos,
        'solicitudes_pendientes': list(solicitudes_pendientes)  # Pasamos como lista para JS
    })


@login_required
def anular_codigo(request, codigo_id):
    if request.method == 'POST':
        try:
            codigo = CodigoGenerado.objects.get(id=codigo_id)

            # Solo aprobadores o el mismo usuario
            if request.user == codigo.usuario or request.user.groups.filter(name="Aprobadores").exists():
                if not codigo.anulado:
                    codigo.anulado = True
                    codigo.usuario_anulacion = request.user
                    codigo.fecha_anulacion = now()
                    codigo.save()

                    # Si existía una solicitud previa de este código, marcarla como procesada
                    SolicitudAnulacion.objects.filter(codigo=codigo, procesada=False).update(procesada=True)

                    return JsonResponse({'success': True})
                else:
                    return JsonResponse({'success': False, 'error': 'Ya está anulado'}, status=400)
            else:
                return JsonResponse({'success': False, 'error': 'No autorizado'}, status=403)
        except CodigoGenerado.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Código no encontrado'}, status=404)

    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)


@login_required
def solicitar_anulacion(request, codigo_id):
    if request.method == 'POST':
        try:
            motivo = request.POST.get('motivo', '').strip()

            if not motivo:
                return JsonResponse({'success': False, 'error': 'El motivo no puede estar vacío.'}, status=400)

            codigo = CodigoGenerado.objects.get(id=codigo_id)

            existe = SolicitudAnulacion.objects.filter(
                codigo=codigo, solicitante=request.user, procesada=False
            ).exists()

            if existe:
                return JsonResponse({'success': False, 'error': 'Ya solicitaste la anulación'}, status=400)

            # Crear la solicitud
            SolicitudAnulacion.objects.create(
                codigo=codigo,
                solicitante=request.user,
                motivo=motivo,
                fecha_solicitud=now()
            )

            return JsonResponse({'success': True})

        except CodigoGenerado.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Código no encontrado'}, status=404)

    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)

@login_required
def historial_anulaciones(request):
    anulaciones = CodigoGenerado.objects.filter(anulado=True).order_by('-fecha_anulacion')
    return render(request, 'historial_anulaciones.html', {'anulaciones': anulaciones})

@login_required
def solicitudes_anulacion_view(request):
    if not request.user.groups.filter(name='aprobadores').exists():
        return mostrar_error(request, mensaje="No tienes permiso para acceder a esta página.", codigo=403)
    
    if request.method == 'POST':
        solicitud_id = request.POST.get('solicitud_id')
        accion = request.POST.get('accion')  # anular o rechazar

        try:
            solicitud = SolicitudAnulacion.objects.select_related('codigo').get(id=solicitud_id, procesada=False)
            if accion == 'anular':
                solicitud.procesada = True
                solicitud.codigo.anulado = True
                solicitud.codigo.fecha_anulacion = now()
                solicitud.codigo.usuario_anulacion = request.user
                solicitud.codigo.save()
                solicitud.save()
                messages.success(request, f"Código {solicitud.codigo.codigo} anulado correctamente.")
            elif accion == 'rechazar':
                solicitud.procesada = True
                solicitud.save()
                messages.info(request, f"Solicitud de anulación rechazada para el código {solicitud.codigo.codigo}.")
            else:
                messages.error(request, "Acción no válida.")

        except SolicitudAnulacion.DoesNotExist:
            messages.error(request, "Solicitud no encontrada o ya procesada.")

        return redirect('solicitudes_anulacion')

    solicitudes = SolicitudAnulacion.objects.select_related('codigo', 'solicitante') \
                    .filter(procesada=False).order_by('-fecha_solicitud')

    return render(request, 'solicitudes_anulacion.html', {'solicitudes': solicitudes})

def mostrar_error(request, mensaje="Ha ocurrido un error", codigo=400):
    return render(request, 'error.html', {
        'mensaje': mensaje,
        'codigo': codigo
    }, status=codigo)