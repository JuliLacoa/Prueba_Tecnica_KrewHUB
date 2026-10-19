from django.shortcuts import get_object_or_404

from reservas.models import Profesor


def listar_profesores():
    return Profesor.objects.filter(is_active=True).order_by("nombre")


def obtener_detalle_profesor_y_horarios(profesor_uuid):
    return get_object_or_404(
        Profesor,
        uuid=profesor_uuid,
        is_active=True,
    )