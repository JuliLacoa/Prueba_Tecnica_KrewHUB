from datetime import timedelta
from io import StringIO

from django.core.management import call_command
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from reservas.models import Alumno, Horario, Profesor, Reserva


class CargarDemoCommandTests(TestCase):
    def test_command_is_idempotent_and_creates_future_schedules(self):
        call_command("cargar_demo", stdout=StringIO())
        call_command("cargar_demo", stdout=StringIO())

        self.assertEqual(Alumno.objects.count(), 1)
        self.assertEqual(Profesor.objects.count(), 3)
        self.assertEqual(Horario.objects.count(), 9)
        self.assertEqual(
            Horario.objects.filter(inicio__gt=timezone.now()).count(),
            9,
        )


class AlumnoDemoApiTests(TestCase):
    def test_returns_preloaded_demo_student(self):
        call_command("cargar_demo", stdout=StringIO())

        response = APIClient().get("/api/alumno-demo/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["nombre"], "Alumno Demo")
        self.assertEqual(
            response.data["uuid"],
            str(Alumno.objects.get(email="alumno.demo@example.com").uuid),
        )

    def test_returns_404_when_demo_student_is_not_loaded(self):
        response = APIClient().get("/api/alumno-demo/")

        self.assertEqual(response.status_code, 404)


class ProfesorApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.profesor = Profesor.objects.create(
            nombre="Profesora Activa",
            descripcion="Descripción",
            especialidades="Machine learning",
        )
        self.profesor_inactivo = Profesor.objects.create(
            nombre="Profesor Inactivo",
            is_active=False,
        )

    def test_list_returns_only_active_teachers(self):
        response = self.client.get("/api/profesores/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["uuid"], str(self.profesor.uuid))
        self.assertEqual(response.data[0]["especialidades"], "Machine learning")

    def test_detail_returns_future_active_unreserved_schedules(self):
        available_schedule = Horario.objects.create(
            profesor=self.profesor,
            inicio=timezone.now() + timedelta(days=1),
        )
        Horario.objects.create(
            profesor=self.profesor,
            inicio=timezone.now() + timedelta(days=2),
            is_active=False,
        )
        Horario.objects.create(
            profesor=self.profesor,
            inicio=timezone.now() - timedelta(days=1),
        )
        alumno = Alumno.objects.create(
            nombre="Alumno",
            email="alumno@example.com",
        )
        reserved_schedule = Horario.objects.create(
            profesor=self.profesor,
            inicio=timezone.now() + timedelta(days=3),
        )
        Reserva.objects.create(alumno=alumno, horario=reserved_schedule)

        response = self.client.get(
            f"/api/profesores/{self.profesor.uuid}/"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["uuid"], str(self.profesor.uuid))
        self.assertEqual(len(response.data["horarios_disponibles"]), 1)
        self.assertEqual(
            response.data["horarios_disponibles"][0]["uuid"],
            str(available_schedule.uuid),
        )

    def test_reserved_schedule_disappears_from_available_schedules(self):
        horario = Horario.objects.create(
            profesor=self.profesor,
            inicio=timezone.now() + timedelta(days=1),
        )
        alumno = Alumno.objects.create(
            nombre="Alumno",
            email="alumno-reserva@example.com",
        )
        response = self.client.post(
            f"/api/horarios/{horario.uuid}/reservar/",
            {"alumno_id": str(alumno.uuid)},
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        detail = self.client.get(
            f"/api/profesores/{self.profesor.uuid}/"
        )
        self.assertEqual(detail.status_code, 200)
        self.assertEqual(detail.data["horarios_disponibles"], [])

    def test_detail_returns_404_for_missing_or_inactive_teacher(self):
        missing_uuid = "00000000-0000-0000-0000-000000000001"

        missing_response = self.client.get(
            f"/api/profesores/{missing_uuid}/"
        )
        inactive_response = self.client.get(
            f"/api/profesores/{self.profesor_inactivo.uuid}/"
        )

        self.assertEqual(missing_response.status_code, 404)
        self.assertEqual(inactive_response.status_code, 404)


class ReservaApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.profesor = Profesor.objects.create(
            nombre="Profesor de prueba",
            especialidades="Machine learning",
        )
        self.alumno = Alumno.objects.create(
            nombre="Alumno de prueba",
            email="reserva@example.com",
        )
        self.horario = Horario.objects.create(
            profesor=self.profesor,
            inicio=timezone.now() + timedelta(days=2),
        )

    def reservar(self, horario_uuid=None, data=None):
        return self.client.post(
            f"/api/horarios/{horario_uuid or self.horario.uuid}/reservar/",
            data if data is not None else {"alumno_id": str(self.alumno.uuid)},
            format="json",
        )

    def test_create_reservation_returns_confirmed_reservation(self):
        response = self.reservar()

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["uuid"], str(Reserva.objects.get().uuid))
        self.assertEqual(response.data["estado"], Reserva.Estado.CONFIRMADA)
        self.assertEqual(response.data["profesor"], self.profesor.nombre)
        self.assertEqual(
            response.data["fecha"],
            timezone.localtime(self.horario.inicio).date(),
        )
        self.assertEqual(
            response.data["hora"],
            timezone.localtime(self.horario.inicio).time(),
        )
        self.assertEqual(Reserva.objects.count(), 1)

    def test_reserved_schedule_cannot_be_reserved_again(self):
        self.assertEqual(self.reservar().status_code, 201)

        response = self.reservar()

        self.assertEqual(response.status_code, 409)
        self.assertEqual(Reserva.objects.count(), 1)

    def test_missing_or_invalid_student_id_returns_400(self):
        missing = self.reservar(data={})
        invalid = self.reservar(data={"alumno_id": "no-es-un-uuid"})

        self.assertEqual(missing.status_code, 400)
        self.assertEqual(invalid.status_code, 400)
        self.assertEqual(Reserva.objects.count(), 0)

    def test_unknown_student_or_schedule_returns_404(self):
        unknown_student = self.reservar(
            data={"alumno_id": "00000000-0000-0000-0000-000000000001"}
        )
        unknown_schedule = self.reservar(
            horario_uuid="00000000-0000-0000-0000-000000000001"
        )

        self.assertEqual(unknown_student.status_code, 404)
        self.assertEqual(unknown_schedule.status_code, 404)

    def test_inactive_or_past_schedule_returns_400(self):
        inactive_schedule = Horario.objects.create(
            profesor=self.profesor,
            inicio=timezone.now() + timedelta(days=3),
            is_active=False,
        )
        past_schedule = Horario.objects.create(
            profesor=self.profesor,
            inicio=timezone.now() - timedelta(days=1),
        )

        inactive = self.reservar(horario_uuid=inactive_schedule.uuid)
        past = self.reservar(horario_uuid=past_schedule.uuid)

        self.assertEqual(inactive.status_code, 400)
        self.assertEqual(past.status_code, 400)
        self.assertEqual(Reserva.objects.count(), 0)

    def test_student_reservations_only_include_upcoming_classes_in_order(self):
        later_schedule = Horario.objects.create(
            profesor=self.profesor,
            inicio=timezone.now() + timedelta(days=4),
        )
        earlier_schedule = Horario.objects.create(
            profesor=self.profesor,
            inicio=timezone.now() + timedelta(days=1),
        )
        past_schedule = Horario.objects.create(
            profesor=self.profesor,
            inicio=timezone.now() - timedelta(days=1),
        )
        Reserva.objects.create(alumno=self.alumno, horario=later_schedule)
        Reserva.objects.create(alumno=self.alumno, horario=earlier_schedule)
        Reserva.objects.create(alumno=self.alumno, horario=past_schedule)
        otro_alumno = Alumno.objects.create(
            nombre="Otro alumno",
            email="otro@example.com",
        )
        otra_reserva = Reserva.objects.create(
            alumno=otro_alumno,
            horario=Horario.objects.create(
                profesor=self.profesor,
                inicio=timezone.now() + timedelta(days=2),
            ),
        )

        response = self.client.get(
            f"/api/alumnos/{self.alumno.uuid}/reservas/"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(
            [item["uuid"] for item in response.data],
            [
                str(Reserva.objects.get(horario=earlier_schedule).uuid),
                str(Reserva.objects.get(horario=later_schedule).uuid),
            ],
        )
        self.assertEqual(response.data[0]["profesor"], self.profesor.nombre)
        self.assertEqual(response.data[0]["especialidades"], "Machine learning")
        self.assertEqual(
            response.data[0]["fecha"],
            timezone.localtime(earlier_schedule.inicio).date(),
        )
        self.assertEqual(
            response.data[0]["hora"],
            timezone.localtime(earlier_schedule.inicio).time(),
        )
        self.assertEqual(response.data[0]["estado"], Reserva.Estado.CONFIRMADA)
        self.assertNotIn(
            str(otra_reserva.uuid),
            [item["uuid"] for item in response.data],
        )

    def test_unknown_student_reservations_returns_404(self):
        response = self.client.get(
            "/api/alumnos/00000000-0000-0000-0000-000000000001/reservas/"
        )

        self.assertEqual(response.status_code, 404)


class DatabaseConstraintTests(TestCase):
    def setUp(self):
        self.profesor = Profesor.objects.create(nombre="Profesor")
        self.alumno = Alumno.objects.create(
            nombre="Alumno",
            email="constraint@example.com",
        )
        self.inicio = timezone.now() + timedelta(days=1)
        self.horario = Horario.objects.create(
            profesor=self.profesor,
            inicio=self.inicio,
        )

    def test_same_teacher_cannot_have_two_schedules_at_same_start(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Horario.objects.create(
                    profesor=self.profesor,
                    inicio=self.inicio,
                )

        self.assertEqual(
            Horario.objects.filter(
                profesor=self.profesor,
                inicio=self.inicio,
            ).count(),
            1,
        )

    def test_schedule_can_only_have_one_reservation(self):
        Reserva.objects.create(alumno=self.alumno, horario=self.horario)
        otro_alumno = Alumno.objects.create(
            nombre="Otro alumno",
            email="constraint-otro@example.com",
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Reserva.objects.create(
                    alumno=otro_alumno,
                    horario=self.horario,
                )

        self.assertEqual(Reserva.objects.filter(horario=self.horario).count(), 1)
