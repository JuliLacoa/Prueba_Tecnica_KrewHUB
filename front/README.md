# Frontend — Aula IA

Interfaz React 19 con Vite 8 para descubrir profesores de IA, ver horarios disponibles, reservar una clase y consultar la agenda del alumno demo. Usa la API Django del directorio `../back`.

## Requisitos y ejecución local

- Node.js 20.19+ o 22.12+ y npm.
- Backend migrado, con datos demo cargados y disponible en `http://127.0.0.1:8000`.

En una terminal desde esta carpeta:

```powershell
npm ci
npm run dev
```

En otra terminal, desde `../back`:

```powershell
.\env\Scripts\Activate.ps1
python manage.py migrate
python manage.py cargar_demo
python manage.py runserver
```

Abrir la URL indicada por Vite (normalmente `http://localhost:5173`). El proxy de desarrollo en `vite.config.js` reenvía `/api` al backend local. La interfaz solicita `GET /api/alumno-demo/` al iniciar y usa el UUID recibido como sesión demo; no hay que copiarlo ni ingresarlo manualmente.

## Flujo y estados de interfaz

1. Consulta y muestra profesores activos.
2. Al elegir un profesor, obtiene el perfil y sus horarios disponibles.
3. Envía la reserva al backend. Solo muestra éxito si la API responde correctamente; ante errores o conflicto, informa el mensaje y actualiza los horarios.
4. Muestra las próximas clases del alumno demo, ordenadas por la API.

Se muestran estados de carga, error, éxito y lista vacía. Las fechas se formatean en la zona horaria local del navegador. El frontend no decide si un horario es reservable: la validación final la realiza el backend.

## Endpoints utilizados

| Método | Ruta | Propósito |
| --- | --- | --- |
| `GET` | `/api/alumno-demo/` | Cargar la identidad demo |
| `GET` | `/api/profesores/` | Listar profesores |
| `GET` | `/api/profesores/<profesor_uuid>/` | Perfil y horarios libres |
| `POST` | `/api/horarios/<horario_uuid>/reservar/` | Reservar con `{"alumno_id": "<uuid>"}` |
| `GET` | `/api/alumnos/<alumno_uuid>/reservas/` | Ver próximas clases |

## Comprobaciones y compilación

```powershell
npm run lint
npm run build
npm run preview
```

La compilación de producción queda en `dist/`. Consume rutas relativas `/api`, así que puede servirse bajo el mismo dominio que Django mediante un proxy inverso. El proxy de Vite es solo para desarrollo. Ver la [guía de despliegue](../Intrucciones_Despliegue.md).

## Alcance

No incluye autenticación real, registro, administración de profesores, cancelación, reprogramación, pagos ni videollamadas. El alumno demo es una identidad compartida para pruebas y no debe usarse con datos personales o reservas reales.
