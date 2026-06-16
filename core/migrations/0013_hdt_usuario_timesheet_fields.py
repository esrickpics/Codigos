from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0012_alter_usuariopaldaca_telefono"),
    ]

    operations = [
        migrations.AddField(
            model_name="usuariopaldaca",
            name="auto_timesheet_generation_suspended",
            field=models.BooleanField(
                default=False,
                verbose_name="Generacion automatica suspendida",
            ),
        ),
        migrations.AddField(
            model_name="usuariopaldaca",
            name="auto_timesheet_generation_suspended_at",
            field=models.DateTimeField(
                blank=True,
                null=True,
                verbose_name="Fecha de suspension automatica",
            ),
        ),
        migrations.AddField(
            model_name="usuariopaldaca",
            name="date_last_hour_entry",
            field=models.DateTimeField(
                blank=True,
                null=True,
                verbose_name="Ultimo registro de horas",
            ),
        ),
    ]
