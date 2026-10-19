from rest_framework.generics import ListAPIView, RetrieveAPIView

from reservas.serializers.profesor import (
    ProfesorDetailSerializer,
    ProfesorListSerializer,
)
from reservas.services.profesor import (
    listar_profesores,
    obtener_detalle_profesor_y_horarios,
)


class ProfesorListView(ListAPIView):
    serializer_class = ProfesorListSerializer

    def get_queryset(self):
        return listar_profesores()


class ProfesorDetailView(RetrieveAPIView):
    serializer_class = ProfesorDetailSerializer
    lookup_field = "uuid"
    lookup_url_kwarg = "profesor_uuid"

    def get_queryset(self):
        return listar_profesores()

    def get_object(self):
        return obtener_detalle_profesor_y_horarios(
            self.kwargs[self.lookup_url_kwarg]
        )