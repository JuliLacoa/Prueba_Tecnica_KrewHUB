from datetime import datetime, time, timedelta
import uuid

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from reservas.constants import DEMO_STUDENT_EMAIL, DEMO_STUDENT_NAME
from reservas.models import Alumno, Horario, Profesor


PROFESORES_DEMO = (
    {
        "uuid": uuid.UUID("b4d7dbd3-a1f3-4ee9-a7ca-23834bced001"),
        "nombre": "Ana García",
        "descripcion": "Especialista en aprendizaje automático y fundamentos de IA.",
        "especialidades": "Machine learning, fundamentos de IA",
    },
    {
        "uuid": uuid.UUID("b4d7dbd3-a1f3-4ee9-a7ca-23834bced002"),
        "nombre": "Mateo Ruiz",
        "descripcion": "Enseña a crear aplicaciones con modelos de lenguaje.",
        "especialidades": "LLMs, procesamiento de lenguaje natural",
    },
    {
        "uuid": uuid.UUID("b4d7dbd3-a1f3-4ee9-a7ca-23834bced003"),
        "nombre": "Lucía Fernández",
        "descripcion": "Guía proyectos de visión por computadora y deep learning.",
        "especialidades": "Visión por computadora, deep learning",
    },
)

HORARIOS_DEMO = (
    (1, time(10, 0)),
    (2, time(14, 0)),
    (3, time(16, 0)),
)
PROFESORES_DEMO_COUNT = len(PROFESORES_DEMO)


class Command(BaseCommand):
    help = "Crea o actualiza el alumno, profesores y horarios de demostración."

    @transaction.atomic
    def handle(self, *args, **options):
        alumno, alumno_creado = Alumno.objects.update_or_create(
            email=DEMO_STUDENT_EMAIL,
            defaults={"nombre": DEMO_STUDENT_NAME},
        )

        profesores_creados = 0
        horarios_creados = 0
        hoy = timezone.localdate()

        for datos_profesor in PROFESORES_DEMO:
            profesor, creado = Profesor.objects.update_or_create(
                uuid=datos_profesor["uuid"],
                defaults={
                    "nombre": datos_profesor["nombre"],
                    "descripcion": datos_profesor["descripcion"],
                    "especialidades": datos_profesor["especialidades"],
                    "is_active": True,
                },
            )
            profesores_creados += creado

            for dias_adelante, hora in HORARIOS_DEMO:
                fecha = hoy + timedelta(days=dias_adelante)
                inicio = timezone.make_aware(datetime.combine(fecha, hora))
                _, creado = Horario.objects.get_or_create(
                    profesor=profesor,
                    inicio=inicio,
                    defaults={"duracion_minutos": 60, "is_active": True},
                )
                horarios_creados += creado

        self.stdout.write(
            self.style.SUCCESS(
                "Datos de demo listos: "
                f"{PROFESORES_DEMO_COUNT} profesores "
                f"({profesores_creados} nuevos), "
                f"{len(PROFESORES_DEMO) * len(HORARIOS_DEMO)} horarios previstos "
                f"({horarios_creados} nuevos)."
            )
        )
        self.stdout.write(f"Alumno demo: {alumno.nombre} ({alumno.uuid})")
        if alumno_creado:
            self.stdout.write("Alumno creado.")
