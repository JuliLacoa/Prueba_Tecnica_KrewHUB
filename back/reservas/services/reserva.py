from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.exceptions import APIException, NotFound, ValidationError

from reservas.models import Alumno, Horario, Reserva


class HorarioReservado(APIException):
    status_code = 409
    default_detail = "El horario ya fue reservado."
    default_code = "horario_reservado"


def crear_reserva(horario_uuid, validated_data):
    alumno = get_object_or_404(Alumno, uuid=validated_data["alumno_id"])

    try:
        with transaction.atomic():
            horario = get_object_or_404(
                Horario.objects.select_for_update().select_related("profesor"),
                uuid=horario_uuid,
            )
            if not horario.is_active:
                raise ValidationError("El horario está inactivo.")
            if horario.inicio <= timezone.now():
                raise ValidationError("No se puede reservar un horario pasado.")
            if Reserva.objects.filter(horario=horario).exists():
                raise HorarioReservado()

            return Reserva.objects.create(alumno=alumno, horario=horario)
    except IntegrityError as error:
        raise HorarioReservado() from error