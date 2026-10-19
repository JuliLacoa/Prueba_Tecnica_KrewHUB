# Backend — Reservas de clases de IA

API de demostración construida con Django 6.1, Django REST Framework y SQLite. Permite listar profesores, consultar horarios, confirmar reservas y ver las próximas clases del alumno demo. No incluye autenticación, pagos ni videollamadas.

## Requisitos e instalación

Se requiere Python 3.12 o superior compatible con las dependencias fijadas. Desde esta carpeta (`back`):

```powershell
python -m venv env
.\env\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Crear o actualizar el esquema solo cuando se cambien modelos; para una instalación limpia basta con aplicar las migraciones existentes:

```powershell
python manage.py migrate
```

La configuración local usa SQLite y UTC con zonas horarias habilitadas.

## Datos de demostración

```powershell
python manage.py cargar_demo
```

El comando idempotente crea/actualiza el alumno de demo, tres profesores y horarios futuros para probar el flujo. Imprime el UUID del alumno. El frontend obtiene automáticamente el alumno activo mediante `GET /api/alumno-demo/`. Ejecutar la carga después de migrar y en la base de datos que realmente usa la instancia.

## Ejecutar y probar

Iniciar el servidor de desarrollo:

```powershell
python manage.py runserver
```

Ejecutar comprobaciones y pruebas:

```powershell
python manage.py check
python manage.py test reservas
```

La suite incluye 16 pruebas para la carga demo, identificación del alumno, consultas de profesores, disponibilidad, reservas, validaciones, próximas clases y restricciones de unicidad.

## Estructura y responsabilidades

- `reservas/models.py`: `Profesor`, `Horario`, `Alumno` y `Reserva`.
- `reservas/serializers/`: validación de entrada y serialización de respuestas.
- `reservas/services/`: consultas y reglas de negocio.
- `reservas/views/` y `reservas/urls.py`: endpoints REST.
- `reservas/management/commands/cargar_demo.py`: carga idempotente de datos de prueba.
- `reservas/tests.py`: pruebas automatizadas.

Un `Horario` representa un turno concreto, se almacena con zona horaria y no se duplica para el mismo profesor e inicio. `Reserva.horario` es `OneToOneField`, por lo que la base impide reservar dos veces un turno. La creación se realiza dentro de una transacción y la restricción de base de datos es la protección final. Las reservas son directamente confirmadas; no se liberan ni cancelan en esta versión.

## API

Todas las rutas tienen prefijo `/api/`.

| Método y ruta | Resultado |
| --- | --- |
| `GET /api/alumno-demo/` | UUID y nombre del alumno precargado; `404` si no se ejecutó la carga demo. |
| `GET /api/profesores/` | Profesores activos con UUID, nombre, especialidades y descripción. |
| `GET /api/profesores/<profesor_uuid>/` | Perfil y horarios activos, futuros y sin reserva; `404` si no existe o está inactivo. |
| `POST /api/horarios/<horario_uuid>/reservar/` | Crea una reserva confirmada. Body: `{"alumno_id": "<uuid>"}`. |
| `GET /api/alumnos/<alumno_uuid>/reservas/` | Próximas reservas del alumno, ordenadas por inicio; `404` si no existe. |

Ejemplo:

```http
POST /api/horarios/<horario_uuid>/reservar/
Content-Type: application/json

{"alumno_id": "<uuid-del-alumno>"}
```

La respuesta `201` contiene `uuid`, `profesor`, `especialidades`, `fecha`, `hora` y `estado`. Los errores principales son `400` para datos incompletos/incorrectos o un horario pasado/inactivo, `404` para alumno u horario inexistente y `409` para un horario ya reservado. El backend vuelve a validar disponibilidad al confirmar.

## Integración con el frontend

El proyecto React está en `../front`; su [README](../front/README.md) documenta instalación y ejecución local. Vite reenvía `/api` a `http://127.0.0.1:8000` durante desarrollo. Para producción, consultar las [instrucciones de despliegue](../Intrucciones_Despliegue.md).

## Límites conocidos y uso de IA

La identidad demo es compartida y no constituye autenticación; todos los visitantes pueden actuar como ese alumno. No se gestionan altas/cambios de profesores, horarios, cancelación, reprogramación, pagos ni videollamadas. Tampoco se evitan solapamientos entre horarios que empiezan a distinta hora. SQLite es para desarrollo y prueba, no para concurrencia productiva.

Copilot en VS Code se utilizó como asistencia para implementar y documentar la aplicación. Se revisaron manualmente el contrato entre frontend y API, validaciones, restricciones de integridad y resultados de las pruebas, lint y compilación.

## Estado

Pasos 0 a 6 completados. La documentación del paso 7 está en el [README principal](../README.md), en este archivo y en [Intrucciones_Despliegue.md](../Intrucciones_Despliegue.md). No se realizó un despliegue real; la guía describe la instalación del código existente y señala qué falta para un uso público seguro.
