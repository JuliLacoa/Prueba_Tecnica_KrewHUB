# Aula IA — Reserva de clases

Módulo de demostración para una plataforma educativa de inteligencia artificial. Permite consultar profesores y sus horarios, reservar una clase y visualizar las próximas clases del alumno.

> **Alcance:** este proyecto fue desarrollado como prueba técnica, priorizando un flujo de reserva funcional de punta a punta. **No está preparado para ofrecer reservas reales en Internet:** utiliza un alumno de demostración compartido, SQLite y una configuración de Django para desarrollo. No ingresar datos reales ni exponerlo públicamente sin realizar primero los cambios de seguridad indicados más abajo.

## Parte 1 — Instalación y ejecución

### 1. Tecnologías y requisitos

- **Backend:** Python, Django y Django REST Framework.
- **Frontend:** React y Vite (Node.js y npm).
- **Base de datos:** SQLite.
- **Servidor de aplicación para Linux:** Gunicorn.

Versiones requeridas para la instalación:

- Python **3.12**, o una versión compatible con `back/requirements.txt`.
- Node.js **20.19+** o **22.12+**, y npm.
- Git (si se va a clonar el repositorio).

La estructura principal del repositorio es:

```text
aula-ia/
├── back/
│   ├── manage.py
│   ├── requirements.txt
│   └── ...
├── front/
│   ├── package.json
│   ├── vite.config.js
│   └── ...
└── README.md
```

Los comandos siguientes parten de la **raíz del repositorio**, excepto donde se indique lo contrario.

### 2. Instalación local del backend

Abrir una terminal y entrar en `back`.

**Linux / macOS:**

```bash
cd back
python3 -m venv env
source env/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python manage.py migrate
python manage.py cargar_demo
```

**Windows (PowerShell):**

```powershell
cd back
py -m venv env
.\env\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python manage.py migrate
python manage.py cargar_demo
```

`migrate` crea o actualiza las tablas de la base de datos. `cargar_demo` prepara los datos necesarios para probar el recorrido: profesores, horarios y alumno de demostración.

Para iniciar Django, desde `back` y con el entorno virtual activado:

```bash
python manage.py runserver
```

Por defecto, la API estará disponible en `http://127.0.0.1:8000/`.

### 3. Instalación local del frontend

En **otra terminal**, entrar en `front` desde la raíz del repositorio:

```bash
cd front
npm ci
npm run dev
```

Abrir la dirección que indique Vite en la terminal (habitualmente `http://localhost:5173/`).

En desarrollo, el proxy definido en `front/vite.config.js` dirige las solicitudes `/api` al backend. **Django y Vite deben estar ejecutándose simultáneamente** para probar el flujo completo.

### 4. Pruebas y verificación

Desde `back`, con el entorno virtual activado:

```bash
python manage.py test reservas
python manage.py check
```

Desde `front`:

```bash
npm run lint
npm run build
```

Para comprobar manualmente el recorrido:

1. Abrir la aplicación y consultar el listado de profesores.
2. Seleccionar un profesor y consultar sus horarios disponibles.
3. Reservar uno de esos horarios y comprobar el mensaje de confirmación.
4. Verificar que el turno ya no aparezca como disponible.
5. Consultar **Mis próximas clases** y comprobar que figure la reserva.
6. Intentar reservar un horario ocupado y verificar que se informe el error.

Como verificaciones adicionales, el backend expone `/api/profesores/` para consultar profesores y `/api/alumno-demo/` para obtener el alumno compartido usado en la demo.

### 5. Instalación en un servidor Linux existente

Estas indicaciones permiten **instalar y ejecutar la versión de demostración** en un equipo Linux ya configurado. Se presupone que la máquina, la conectividad, el dominio (si corresponde) y un servidor web/proxy están disponibles. **Los pasos no constituyen una puesta en producción segura.**

En los ejemplos se utiliza `/opt/aula-ia` como ubicación del proyecto; cambiarla si se instala en otra carpeta.

**Backend:**

```bash
cd /opt/aula-ia/back
python3 -m venv env
./env/bin/pip install --upgrade pip
./env/bin/pip install -r requirements.txt
./env/bin/python manage.py migrate
./env/bin/python manage.py cargar_demo
./env/bin/python manage.py test reservas
./env/bin/python manage.py check
```

**Frontend:**

```bash
cd /opt/aula-ia/front
npm ci
npm run lint
npm run build
```

La compilación se genera en `front/dist`. Copiar **el contenido** de ese directorio al directorio desde el que el servidor web sirva los archivos estáticos (por ejemplo, `/var/www/aula-ia`). Configurar el fallback de rutas de la SPA para que las rutas del frontend respondan con `index.html`.

**Servidor Django:**

```bash
cd /opt/aula-ia/back
./env/bin/pip install gunicorn
./env/bin/gunicorn config.wsgi:application --bind 127.0.0.1:8000
```

Para una instalación persistente, mantener Gunicorn en ejecución mediante el supervisor de procesos disponible en el servidor. Configurar el servidor web/proxy para:

- Servir el frontend compilado en `/`.
- Reenviar las solicitudes a `/api/` hacia `http://127.0.0.1:8000`, **sin modificar la ruta**.
- Reenviar `/admin/` al mismo backend si se necesita Django Admin.
- Hacer que frontend y API funcionen bajo **el mismo dominio**, ya que el frontend solicita los recursos mediante `/api`.

El proxy configurado en Vite se utiliza solamente durante el desarrollo; no reemplaza al proxy del servidor.

**Comprobación:** verificar que `/` muestre la interfaz, que `/api/profesores/` y `/api/alumno-demo/` respondan y que sea posible reservar un horario y visualizarlo en **Mis próximas clases**. Las reservas de prueba quedan guardadas en SQLite.

### 6. Limitaciones de la demo y requisitos antes de una publicación real

La versión entregada **no debe exponerse públicamente como servicio de reservas real**. Para llevarla a producción se necesitaría, como mínimo:

- Configurar `DEBUG=False`, `SECRET_KEY` y `ALLOWED_HOSTS` mediante variables de entorno.
- Configurar HTTPS y las medidas de seguridad de Django correspondientes al proxy.
- Evaluar una base de datos apta para producción, sus copias de seguridad y el comportamiento de las reservas concurrentes.
- Incorporar autenticación y autorización por alumno, y eliminar el alumno compartido y `/api/alumno-demo/`.

Estas mejoras **no están implementadas** como parte de las instrucciones de despliegue anteriores.

## Parte 2 — Desarrollo y decisiones tomadas

### 1. Criterio de implementación

El objetivo principal fue resolver el flujo solicitado: **elegir un profesor → consultar sus horarios → reservar una clase → ver la reserva en las próximas clases**.

Considerando el tiempo disponible para la prueba técnica, prioricé la funcionalidad y las validaciones esenciales por sobre el diseño visual o las características propias de una plataforma comercial completa.

La especificación de trabajo utilizada para desarrollar el proyecto está incluida en `back/especificaciones/26.10.19_PProyectoReservasClasesIA.txt`.

### 2. Proceso de trabajo

1. **Planificación.** Definí una lista de tareas y su secuencia, considerando el límite de tiempo disponible.
2. **Reutilización de una base previa.** Tomé como referencia un CRUD que había desarrollado anteriormente y solicité a ChatGPT que adaptara su especificación a la nueva consigna.
3. **Revisión de la especificación.** Revisé el documento resultante y lo utilicé como guía para la implementación.
4. **Desarrollo incremental.** Ejecuté las tareas de forma secuencial. Al terminar cada etapa, revisé su resultado antes de continuar con la siguiente.
5. **Versionado.** Subí el proyecto completo a GitHub.
6. **Prueba general.** Realicé una verificación final del funcionamiento del flujo.
7. **Documentación.** Completé este README con los requisitos, los comandos y las decisiones tomadas.
8. **Entrega.** Compartí la solución desarrollada.

### 3. Decisiones técnicas y de alcance

- **Separación entre backend y frontend.** Organicé el proyecto en `back/` y `front/`, dentro de un único repositorio, para mantener diferenciadas las responsabilidades de cada parte.
- **Django y API REST.** Elegí Django para el backend y una API para comunicarlo con el frontend.
- **SQLite.** Utilicé una base de datos simple, suficiente para una prueba ejecutable sin infraestructura adicional.
- **Datos de demostración.** Incorporé un comando para cargar profesores, horarios y un alumno de prueba, de modo que el flujo pueda evaluarse sin una configuración manual extensa.
- **Reservas únicas.** La especificación contempla asociar cada reserva a un horario concreto, impedir más de una reserva sobre ese turno y volver a comprobar su disponibilidad al confirmar.
- **Alcance acotado.** No incorporé autenticación real, pagos ni videollamadas, porque la consigna los dejaba expresamente fuera del alcance obligatorio.

### 4. Uso de inteligencia artificial

Utilicé **ChatGPT** para adaptar la especificación de un CRUD previo al sistema de reservas solicitado y como apoyo durante el desarrollo.

Por la restricción de tiempo, opté por un uso de IA en la implementación **más intensivo del que preferiría en un proyecto sin este límite**. Para compensarlo, trabajé por etapas y revisé los resultados de cada una antes de avanzar, además de efectuar una prueba general al finalizar.

### 5. Limitaciones y posibles mejoras

Además de las consideraciones de seguridad indicadas en la primera parte, una evolución del proyecto podría incorporar autenticación real y reservas independientes por alumno, cancelaciones o reprogramaciones, gestión de disponibilidad de profesores, pagos, videollamadas y mayor cobertura de pruebas (en especial, concurrencia y superposición de horarios).

El foco de esta entrega fue **demostrar el funcionamiento del circuito básico de reservas** dentro del tiempo disponible.
