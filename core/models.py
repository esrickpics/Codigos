import hashlib

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class Disciplina(models.Model):
    """Catalogo de disciplinas; se amplia desde /admin sin categorias fijas."""

    nombre = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = "core_disciplina"
        ordering = ("nombre",)
        verbose_name = "Disciplina"
        verbose_name_plural = "Disciplinas"

    def __str__(self):
        return self.nombre


class Perfil(models.Model):
    """Catalogo de perfiles; asignacion opcional por usuario en cada programa."""

    nombre = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = "core_perfil"
        ordering = ("nombre",)
        verbose_name = "Perfil"
        verbose_name_plural = "Perfiles"

    def __str__(self):
        return self.nombre


class Modulo(models.Model):
    """Programa o aplicacion del ecosistema Paldaca."""

    codigo = models.SlugField(
        max_length=32,
        unique=True,
        help_text="Identificador estable del programa (ej. portal, hdt).",
    )
    nombre = models.CharField(max_length=80)
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = "core_modulo"
        ordering = ("nombre",)
        verbose_name = "Modulo"
        verbose_name_plural = "Modulos"

    def __str__(self):
        return f"{self.nombre} ({self.codigo})"


class UsuarioModulo(models.Model):
    """Acceso de un usuario a un programa concreto."""

    usuario = models.ForeignKey(
        "UsuarioPaldaca",
        on_delete=models.CASCADE,
        related_name="accesos_modulo",
    )
    modulo = models.ForeignKey(
        Modulo,
        on_delete=models.CASCADE,
        related_name="accesos_usuario",
    )
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "core_usuario_modulo"
        constraints = [
            models.UniqueConstraint(
                fields=("usuario", "modulo"),
                name="core_usuario_modulo_unique",
            )
        ]
        verbose_name = "Acceso a modulo"
        verbose_name_plural = "Accesos a modulos"

    def __str__(self):
        return f"{self.usuario_id} -> {self.modulo.codigo}"


class UsuarioPaldaca(AbstractUser):
    ROL_USUARIO = "usuario"
    ROL_ADMINISTRADOR = "administrador"

    ROL_CHOICES = (
        (ROL_USUARIO, "Usuario"),
        (ROL_ADMINISTRADOR, "Administrador"),
    )

    telefono = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Teléfono del usuario",
        verbose_name="Teléfono",
    )

    disciplina = models.ForeignKey(
        Disciplina,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="usuarios",
        help_text="Disciplina del usuario",
    )
    perfil = models.ForeignKey(
        Perfil,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="usuarios",
        verbose_name="perfil",
        help_text="Opcional. No es obligatorio asignarlo a todos los usuarios.",
    )
    rol = models.CharField(
        max_length=20,
        choices=ROL_CHOICES,
        default=ROL_USUARIO,
    )
    modulos = models.ManyToManyField(
        Modulo,
        through=UsuarioModulo,
        related_name="usuarios",
        blank=True,
    )
    date_last_hour_entry = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Ultimo registro de horas",
    )
    auto_timesheet_generation_suspended = models.BooleanField(
        default=False,
        verbose_name="Generacion automatica suspendida",
    )
    auto_timesheet_generation_suspended_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Fecha de suspension automatica",
    )

    class Meta:
        db_table = "core_usuario"

    @property
    def es_administrador(self):
        """Rol administrador (permisos elevados dentro de cada modulo asignado)."""
        return self.rol == self.ROL_ADMINISTRADOR

    @property
    def es_superadmin(self):
        """Acceso a todos los modulos activos sin filas en core_usuario_modulo."""
        return self.is_superuser

    def _codigos_modulos_asignados(self):
        return list(
            self.accesos_modulo.filter(modulo__activo=True)
            .order_by("modulo__codigo")
            .values_list("modulo__codigo", flat=True)
        )

    def get_auth_revision(self, module_codes=None):
        """Build the permission revision, reusing prefetched module codes."""
        if self.is_superuser:
            module_part = "*"
        else:
            codes = (
                self._codigos_modulos_asignados()
                if module_codes is None
                else sorted(module_codes)
            )
            module_part = ",".join(codes)
        raw_value = "|".join(
            [
                str(self.pk or ""),
                self.rol,
                str(self.disciplina_id or ""),
                str(self.perfil_id or ""),
                "1" if self.is_active else "0",
                module_part,
            ]
        )
        return hashlib.sha256(raw_value.encode("utf-8")).hexdigest()

    def tiene_acceso_modulo(self, modulo_codigo):
        codigo = (modulo_codigo or "").strip().lower()
        if not codigo or not self.is_active:
            return False
        cached = getattr(self, "_paldaca_module_codes", None)
        if cached is not None:
            return codigo in cached
        if self.is_superuser:
            return Modulo.objects.filter(codigo=codigo, activo=True).exists()
        return self.accesos_modulo.filter(
            modulo__codigo=codigo,
            modulo__activo=True,
        ).exists()

    def es_administrador_en_modulo(self, modulo_codigo):
        """Admin dentro del modulo si tiene acceso y rol administrador (o es superuser)."""
        if not self.tiene_acceso_modulo(modulo_codigo):
            return False
        return self.is_superuser or self.rol == self.ROL_ADMINISTRADOR

    def modulos_habilitados(self):
        qs = Modulo.objects.filter(activo=True)
        if not self.is_superuser:
            qs = qs.filter(accesos_usuario__usuario=self)
        return qs.distinct().order_by("nombre")

    def modulos_payload(self):
        return [
            {"codigo": m.codigo, "nombre": m.nombre}
            for m in self.modulos_habilitados()
        ]


class Role(models.Model):
    """Roles internos del modulo Calidad (tablas compartidas en paldaca_db)."""

    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "calidad_role"
        verbose_name = "Rol"
        verbose_name_plural = "Roles"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class UserRole(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="calidad_roles",
    )
    rol = models.ForeignKey(Role, on_delete=models.CASCADE, related_name="usuarios")
    fecha_asignacion = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = "calidad_user_role"
        verbose_name = "Rol de Usuario"
        verbose_name_plural = "Roles de Usuarios"
        unique_together = ["usuario", "rol"]
        ordering = ["-fecha_asignacion"]

    def __str__(self):
        return f"{self.usuario.username} - {self.rol.nombre}"


class GoogleDriveToken(models.Model):
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="google_drive_token",
    )
    token_encrypted = models.TextField(help_text="Token encriptado")
    refresh_token_encrypted = models.TextField(
        blank=True,
        help_text="Refresh token encriptado",
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = "calidad_google_drive_token"
        verbose_name = "Token de Google Drive"
        verbose_name_plural = "Tokens de Google Drive"

    def __str__(self):
        return f"Token de {self.usuario.username}"
