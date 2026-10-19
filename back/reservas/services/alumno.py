from django.shortcuts import get_object_or_404
from django.utils import timezone

from reservas.constants import DEMO_STUDENT_EMAIL
from reservas.models import Alumno, Reserva


def obtener_alumno_demo():
    return get_object_or_404(Alumno, email=DEMO_STUDENT_EMAIL)


def listar_proximas_reservas_alumno(alumno_uuid):
    alumno = get_object_or_404(Alumno, uuid=alumno_uuid)
    return (
        Reserva.objects.filter(
            alumno=alumno,
            horario__inicio__gt=timezone.now(),
        )
        .select_related("horario__profesor")
        .order_by("horario__inicio")
    )