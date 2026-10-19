import uuid

from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


class Profesor(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True)
    especialidades = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    fecha_create = models.DateTimeField(auto_now_add=True)
    fecha_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nombre

    @property
    def horarios_disponibles(self):
        return self.horarios.filter(
            is_active=True,
            inicio__gt=timezone.now(),
            reserva__isnull=True,
        ).order_by("inicio")


class Horario(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    profesor = models.ForeignKey(
        Profesor,
        on_delete=models.PROTECT,
        related_name="horarios",
    )
    inicio = models.DateTimeField()
    duracion_minutos = models.PositiveIntegerField(
        default=60,
        validators=[MinValueValidator(1)],
    )
    is_active = models.BooleanField(default=True)
    fecha_create = models.DateTimeField(auto_now_add=True)
    fecha_update = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("profesor", "inicio"),
                name="reservas_horario_profesor_inicio_unico",
            ),
            models.CheckConstraint(
                condition=models.Q(duracion_minutos__gt=0),
                name="reservas_horario_duracion_positiva",
            ),
        ]
        ordering = ("inicio",)

    def __str__(self):
        return f"{self.profesor} - {self.inicio}"

    @property
    def disponible(self):
        return (
            self.is_active
            and self.inicio > timezone.now()
            and not hasattr(self, "reserva")
        )


class Alumno(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    nombre = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    fecha_create = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre


class Reserva(models.Model):
    class Estado(models.TextChoices):
        CONFIRMADA = "confirmada", "Confirmada"

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    alumno = models.ForeignKey(
        Alumno,
        on_delete=models.PROTECT,
        related_name="reservas",
    )
    horario = models.OneToOneField(
        Horario,
        on_delete=models.PROTECT,
        related_name="reserva",
    )
    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.CONFIRMADA,
    )
    fecha_create = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (
            f"{self.alumno} - {self.horario.profesor} - "
            f"{self.horario.inicio} - {self.get_estado_display()}"
        )
