from rest_framework import serializers

from reservas.models import Alumno


class AlumnoDemoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alumno
        fields = ("uuid", "nombre")