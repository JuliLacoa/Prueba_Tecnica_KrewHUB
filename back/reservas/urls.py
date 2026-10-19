from django.urls import path

from reservas.views.alumno import AlumnoDemoView, AlumnoReservasView
from reservas.views.profesor import ProfesorDetailView, ProfesorListView
from reservas.views.reserva import ReservaCrearView


urlpatterns = [
    path("alumno-demo/", AlumnoDemoView.as_view(), name="alumno-demo"),
    path("profesores/", ProfesorListView.as_view(), name="profesor-list"),
    path(
        "profesores/<uuid:profesor_uuid>/",
        ProfesorDetailView.as_view(),
        name="profesor-detail",
    ),
    path(
        "horarios/<uuid:horario_uuid>/reservar/",
        ReservaCrearView.as_view(),
        name="reserva-crear",
    ),
    path(
        "alumnos/<uuid:alumno_uuid>/reservas/",
        AlumnoReservasView.as_view(),
        name="alumno-reservas",
    ),
]