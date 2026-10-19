from rest_framework import serializers

from reservas.models import Horario, Profesor


class ProfesorListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profesor
        fields = ("uuid", "nombre", "especialidades", "descripcion")


class HorarioDisponibleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Horario
        fields = ("uuid", "inicio", "duracion_minutos")


class ProfesorDetailSerializer(serializers.ModelSerializer):
    horarios_disponibles = HorarioDisponibleSerializer(many=True, read_only=True)

    class Meta:
        model = Profesor
        fields = (
            "uuid",
            "nombre",
            "descripcion",
            "especialidades",
            "horarios_disponibles",
        )