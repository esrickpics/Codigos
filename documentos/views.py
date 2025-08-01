from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from django.core.mail import send_mail, BadHeaderError
from .forms import CodigoForm, BusquedaCodigoForm
from .models import CodigoGenerado, Empresa
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
from django.utils.timezone import now

def home(request): 
    return render(request, 'home.html')

def signup(request):
    
    if request.method == 'GET':
        return render(request, 'signup.html', { 
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
                return render(request, 'signup.html', { 
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
        return render(request, 'login.html', { 
            'form': AuthenticationForm() 
        })
    else:
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'login.html', {
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
                )
                codigo_generado = codigo

                # Enviar correo
                usuario = request.user.username
                fecha = now().strftime('%d/%m/%Y %H:%M')
                #destino = 'ricardogoitia108@gmail.com'  # Cambiar por la dirección de correo de la empresa
                destino = empresa.correo_notificacion
                asunto = 'Nuevo código generado'
                mensaje = f"""
                    Se ha generado un nuevo código:
                    Usuario: {usuario}
                    Fecha: {fecha}
                    Código: {codigo}
                """
                try:
                    send_mail(asunto, mensaje, 'admin@cpaldaca.com', [destino], fail_silently=False)
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
    if mostrar_todos:
        codigos = CodigoGenerado.objects.select_related('usuario').order_by('-fecha_creacion')
    else:
        codigos = CodigoGenerado.objects.select_related('usuario').order_by('-fecha_creacion')[:15]
    return render(request, 'lista_codigos.html', {'codigos': codigos, 'mostrar_todos': mostrar_todos})


@login_required
def anular_codigo(request, codigo_id):
    if request.method == 'POST':
        try:
            codigo = CodigoGenerado.objects.get(id=codigo_id)
            if request.user == codigo.usuario or request.user.is_staff:
                if not codigo.anulado:
                    codigo.anulado = True
                    codigo.usuario_anulacion = request.user  
                    codigo.fecha_anulacion = now()
                    codigo.save()
                    return JsonResponse({'success': True})
                else:
                    return JsonResponse({'success': False, 'error': 'Ya está anulado'}, status=400)
            else:
                return JsonResponse({'success': False, 'error': 'No autorizado'}, status=403)
        except CodigoGenerado.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Código no encontrado'}, status=404)
    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)

@login_required
def historial_anulaciones(request):
    anulaciones = CodigoGenerado.objects.filter(anulado=True).order_by('-fecha_anulacion')
    return render(request, 'historial_anulaciones.html', {'anulaciones': anulaciones})