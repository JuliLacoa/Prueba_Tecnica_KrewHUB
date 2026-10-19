# Reservas de clases de IA

Aplicación de demostración para explorar profesores de IA, consultar horarios, confirmar una reserva y ver las próximas clases de un alumno demo.

## Componentes

- **Backend:** Python 3.12+, Django 6.1, Django REST Framework y SQLite en desarrollo.
- **Frontend:** React 19, Vite 8 y Tailwind CSS 4.
- **Ejecución local:** el frontend usa el proxy de Vite para consumir la API Django.

## Documentación

- [Backend: instalación, modelos, API y pruebas](./back/README.md)
- [Frontend: instalación, flujo y compilación](./front/README.md)
- [Intrucciones_Despliegue.md](./Intrucciones_Despliegue.md): instalación de backend y frontend en una máquina Linux ya operativa, compilación y conexión al servidor web existente.
- [Especificación funcional](./back/especificaciones/26.10.19_ProyectoReservasClasesIA.txt)

## Inicio rápido local

Primero, preparar backend desde `back`:

```powershell
python -m venv env
.\env\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py cargar_demo
python manage.py runserver
```

Luego, desde `front`, instalar dependencias y arrancar la interfaz:

```powershell
npm ci
npm run dev
```

Abrir la URL local que indique Vite. Los pasos completos, endpoints, comandos de prueba y limitaciones están detallados en los README de cada componente.

## Alcance y advertencia

Es una prueba técnica/demo: no implementa autenticación real. Todos los visitantes comparten el alumno demo y pueden reservar en su nombre. No usar con usuarios ni datos personales reales. La guía de despliegue detalla los pasos de instalación y las adaptaciones necesarias antes de un uso público real.
