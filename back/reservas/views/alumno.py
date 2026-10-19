from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from reservas.serializers.alumno import AlumnoDemoSerializer
from reservas.serializers.reserva import AlumnoReservasSerializer
from reservas.services.alumno import (
    listar_proximas_reservas_alumno,
    obtener_alumno_demo,
)


class AlumnoDemoView(APIView):
    def get(self, request):
        alumno = obtener_alumno_demo()
        return Response(AlumnoDemoSerializer(alumno).data)


class AlumnoReservasView(ListAPIView):
    serializer_class = AlumnoReservasSerializer

    def get_queryset(self):
        return listar_proximas_reservas_alumno(
            self.kwargs["alumno_uuid"]
        )