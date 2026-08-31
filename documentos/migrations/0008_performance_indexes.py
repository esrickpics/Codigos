from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("documentos", "0007_migrate_auth_user_to_core"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="codigogenerado",
            index=models.Index(
                fields=["-fecha_creacion"],
                name="codigos_fecha_creacion_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="codigogenerado",
            index=models.Index(
                fields=["anulado", "-fecha_anulacion"],
                name="codigos_anulado_fecha_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="codigogenerado",
            index=models.Index(
                fields=[
                    "empresa",
                    "año",
                    "numero_proyecto",
                    "subproyecto",
                    "departamento",
                    "disciplina",
                    "tipo_documento",
                ],
                name="codigos_consecutivo_lookup_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="solicitudanulacion",
            index=models.Index(
                fields=["solicitante", "procesada"],
                name="codigos_sol_pendiente_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="solicitudanulacion",
            index=models.Index(
                fields=["procesada", "-fecha_solicitud"],
                name="codigos_sol_fecha_idx",
            ),
        ),
    ]
