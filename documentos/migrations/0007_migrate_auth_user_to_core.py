import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def migrate_auth_user_to_core(apps, schema_editor):
    connection = schema_editor.connection
    if "auth_user" not in connection.introspection.table_names():
        return

    AuthUser = apps.get_model("auth", "User")
    UsuarioPaldaca = apps.get_model("core", "UsuarioPaldaca")
    CodigoGenerado = apps.get_model("documentos", "CodigoGenerado")
    SolicitudAnulacion = apps.get_model("documentos", "SolicitudAnulacion")

    id_map = {}
    for legacy in AuthUser.objects.all().iterator():
        user = UsuarioPaldaca.objects.filter(username=legacy.username).first()
        if not user:
            user = UsuarioPaldaca(
                username=legacy.username,
                email=legacy.email or "",
                first_name=legacy.first_name,
                last_name=legacy.last_name,
                is_active=legacy.is_active,
                is_staff=legacy.is_staff,
            )
            user.password = legacy.password
            user.save()
        id_map[legacy.pk] = user.pk

    for codigo in CodigoGenerado.objects.exclude(usuario_id__isnull=True).iterator():
        new_id = id_map.get(codigo.usuario_id)
        if new_id and new_id != codigo.usuario_id:
            CodigoGenerado.objects.filter(pk=codigo.pk).update(usuario_id=new_id)

    for codigo in CodigoGenerado.objects.exclude(usuario_anulacion_id__isnull=True).iterator():
        new_id = id_map.get(codigo.usuario_anulacion_id)
        if new_id and new_id != codigo.usuario_anulacion_id:
            CodigoGenerado.objects.filter(pk=codigo.pk).update(usuario_anulacion_id=new_id)

    for solicitud in SolicitudAnulacion.objects.exclude(solicitante_id__isnull=True).iterator():
        new_id = id_map.get(solicitud.solicitante_id)
        if new_id and new_id != solicitud.solicitante_id:
            SolicitudAnulacion.objects.filter(pk=solicitud.pk).update(solicitante_id=new_id)


class Migration(migrations.Migration):

    dependencies = [
        ("documentos", "0006_codigos_prefijo_tablas"),
        ("core", "0010_alter_usuariopaldaca_options"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RunPython(migrate_auth_user_to_core, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="codigogenerado",
            name="usuario",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="codigos_generados",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="codigogenerado",
            name="usuario_anulacion",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="codigos_anulados",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="solicitudanulacion",
            name="solicitante",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="solicitudes_anulacion_codigo",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
