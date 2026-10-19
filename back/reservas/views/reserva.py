from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from reservas.serializers.reserva import (
    ReservaCrearSerializer,
    ReservaDetailSerializer,
)
from reservas.services.reserva import crear_reserva


class ReservaCrearView(APIView):
    def post(self, request, horario_uuid):
        serializer = ReservaCrearSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        reserva = crear_reserva(horario_uuid, serializer.validated_data)
        return Response(
            ReservaDetailSerializer(reserva).data,
            status=status.HTTP_201_CREATED,
        )