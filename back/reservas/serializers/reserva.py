from django.utils import timezone

from rest_framework import serializers

from reservas.models import Reserva


class ReservaCrearSerializer(serializers.Serializer):
    alumno_id = serializers.UUIDField()


class ReservaDetailSerializer(serializers.ModelSerializer):
    profesor = serializers.CharField(
        source="horario.profesor.nombre",
        read_only=True,
    )
    especialidades = serializers.CharField(
        source="horario.profesor.especialidades",
        read_only=True,
    )
    fecha = serializers.SerializerMethodField()
    hora = serializers.SerializerMethodField()

    class Meta:
        model = Reserva
        fields = ("uuid", "profesor", "especialidades", "fecha", "hora", "estado")

    def get_fecha(self, reserva):
        return timezone.localtime(reserva.horario.inicio).date()

    def get_hora(self, reserva):
        return timezone.localtime(reserva.horario.inicio).time()


class AlumnoReservasSerializer(ReservaDetailSerializer):
    pass