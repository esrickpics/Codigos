from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("documentos", "0005_codigogenerado_motivo"),
    ]

    operations = [
        migrations.AlterModelTable(
            name="contadorcodigo",
            table="codigos_contador_codigo",
        ),
        migrations.AlterModelTable(
            name="empresa",
            table="codigos_empresa",
        ),
        migrations.AlterModelTable(
            name="codigogenerado",
            table="codigos_codigo_generado",
        ),
        migrations.AlterModelTable(
            name="solicitudanulacion",
            table="codigos_solicitud_anulacion",
        ),
    ]
