# Intrucciones de despliegue

Pasos para instalar y publicar la aplicación en una PC/servidor Linux ya operativo. Se asume que el equipo, el dominio y el acceso a la red ya están preparados; aquí solo se instala y arranca este proyecto.

> **Importante:** tal como está el código, es una demo, no un servicio público para reservas reales. No tiene autenticación: todas las personas comparten el alumno demo. Además, Django usa SQLite, `DEBUG=True` y una clave de desarrollo. No exponerlo en Internet ni usar datos reales hasta adaptar y revisar la configuración de producción y agregar autenticación.

## Requisitos en la máquina

- Python 3.12 o compatible con las dependencias del backend.
- Node.js 20.19+ o 22.12+ y npm.
- El proyecto copiado o clonado en la máquina.
- Para servirlo detrás de un dominio, un servidor web/proxy ya disponible que pueda servir archivos estáticos y reenviar `/api/` a Django.

En los comandos de ejemplo, el proyecto está en `/opt/aula-ia`. Cambiar esa ruta por la ubicación elegida.

## 1. Instalar el backend

```bash
cd /opt/aula-ia/back
python3 -m venv env
./env/bin/pip install --upgrade pip
./env/bin/pip install -r requirements.txt
```

Crear las tablas y cargar los datos de prueba:

```bash
./env/bin/python manage.py migrate
./env/bin/python manage.py cargar_demo
```

Antes de publicar una versión, ejecutar las pruebas:

```bash
./env/bin/python manage.py test reservas
./env/bin/python manage.py check
```

## 2. Instalar y compilar el frontend

```bash
cd /opt/aula-ia/front
npm ci
npm run lint
npm run build
```

La aplicación compilada queda en `front/dist`. Copiar **el contenido** de esa carpeta al directorio estático que ya sirva el servidor web, por ejemplo `/var/www/aula-ia`. Configurar el fallback de rutas de la SPA para que las rutas de frontend respondan con `index.html`.

## 3. Arrancar Django y conectar el dominio

Instalar Gunicorn dentro del entorno virtual y arrancarlo desde `back`:

```bash
cd /opt/aula-ia/back
./env/bin/pip install gunicorn
./env/bin/gunicorn config.wsgi:application --bind 127.0.0.1:8000
```

Dejar Gunicorn ejecutándose con el supervisor de procesos que ya utilice la máquina. Configurar el servidor web existente para:

- Servir `front/dist` para `/`.
- Reenviar `/api/` al backend en `http://127.0.0.1:8000`, conservando la ruta.
- Reenviar `/admin/` al mismo backend, si se necesita Django Admin.

El frontend llama a la API usando `/api`, por lo que en producción ambos deben quedar bajo el mismo dominio. El proxy de Vite en `front/vite.config.js` es únicamente para desarrollo.

## 4. Comprobar la instalación

Desde la máquina o el navegador, verificar:

- `/` carga la interfaz.
- `/api/profesores/` devuelve profesores.
- `/api/alumno-demo/` devuelve el alumno demo.
- Se puede consultar un horario, reservarlo y verlo en “Mis próximas clases”.

La reserva de prueba queda guardada en la base SQLite. Los horarios reservados no vuelven a aparecer como disponibles.

## Configuración necesaria para producción real

Esta guía instala la aplicación existente, pero no convierte su configuración de demo en una configuración segura para producción. Antes de hacerla pública, como mínimo:

1. Cambiar Django a `DEBUG=False` y cargar `SECRET_KEY` y `ALLOWED_HOSTS` desde variables de entorno.
2. Configurar HTTPS y las opciones de seguridad de Django para el proxy utilizado.
3. Usar una base de datos de producción y respaldos; probar las migraciones y concurrencia en ese motor.
4. Implementar autenticación y autorización por alumno y quitar el alumno compartido y el endpoint `/api/alumno-demo/`.

Estas modificaciones están fuera del alcance de esta guía y no se deben simular cambiando solo los comandos de arranque.
