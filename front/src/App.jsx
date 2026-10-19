import { useEffect, useState } from 'react'
import './App.css'

function errorMessage(payload, status) {
  if (typeof payload?.detail === 'string') return payload.detail

  if (payload && typeof payload === 'object') {
    for (const value of Object.values(payload)) {
      const message = Array.isArray(value) ? value[0] : value
      if (typeof message === 'string') return message
    }
  }

  return `No se pudo completar la solicitud (HTTP ${status}).`
}

async function requestJson(url, options) {
  const response = await fetch(url, options)
  const payload = await response.json()

  if (!response.ok) {
    throw new Error(errorMessage(payload, response.status))
  }

  return payload
}

function formatDateTime(value) {
  return new Intl.DateTimeFormat('es-AR', {
    dateStyle: 'full',
    timeStyle: 'short',
  }).format(new Date(value))
}

function formatReservationDateTime(reservation) {
  return formatDateTime(`${reservation.fecha}T${reservation.hora}Z`)
}

function App() {
  const [activeStudentId, setActiveStudentId] = useState('')
  const [studentName, setStudentName] = useState('')
  const [demoStudentLoading, setDemoStudentLoading] = useState(true)
  const [demoStudentError, setDemoStudentError] = useState('')
  const [teachers, setTeachers] = useState([])
  const [teachersLoading, setTeachersLoading] = useState(true)
  const [teachersError, setTeachersError] = useState('')
  const [selectedTeacherId, setSelectedTeacherId] = useState('')
  const [selectedTeacher, setSelectedTeacher] = useState(null)
  const [teacherLoading, setTeacherLoading] = useState(false)
  const [teacherError, setTeacherError] = useState('')
  const [selectedSlotId, setSelectedSlotId] = useState('')
  const [upcomingClasses, setUpcomingClasses] = useState([])
  const [classesLoading, setClassesLoading] = useState(false)
  const [classesError, setClassesError] = useState('')
  const [bookingError, setBookingError] = useState('')
  const [bookingSuccess, setBookingSuccess] = useState(null)
  const [bookingSlotId, setBookingSlotId] = useState('')

  useEffect(() => {
    let isCurrent = true
    requestJson('/api/profesores/')
      .then((results) => {
        if (isCurrent) setTeachers(results)
      })
      .catch((error) => {
        if (isCurrent) setTeachersError(error.message)
      })
      .finally(() => {
        if (isCurrent) setTeachersLoading(false)
      })

    return () => {
      isCurrent = false
    }
  }, [])

  useEffect(() => {
    let isCurrent = true
    requestJson('/api/alumno-demo/')
      .then((student) => {
        if (isCurrent) {
          setClassesLoading(true)
          setActiveStudentId(student.uuid)
          setStudentName(student.nombre)
          setDemoStudentError('')
        }
      })
      .catch((error) => {
        if (isCurrent) setDemoStudentError(error.message)
      })
      .finally(() => {
        if (isCurrent) setDemoStudentLoading(false)
      })

    return () => {
      isCurrent = false
    }
  }, [])

  useEffect(() => {
    if (!selectedTeacherId) return undefined

    let isCurrent = true
    requestJson(`/api/profesores/${selectedTeacherId}/`)
      .then((teacher) => {
        if (isCurrent) {
          setSelectedTeacher(teacher)
          setTeacherError('')
        }
      })
      .catch((error) => {
        if (isCurrent) setTeacherError(error.message)
      })
      .finally(() => {
        if (isCurrent) setTeacherLoading(false)
      })

    return () => {
      isCurrent = false
    }
  }, [selectedTeacherId])

  useEffect(() => {
    if (!activeStudentId) return undefined

    let isCurrent = true
    requestJson(`/api/alumnos/${activeStudentId}/reservas/`)
      .then((reservations) => {
        if (isCurrent) {
          setUpcomingClasses(reservations)
          setClassesError('')
        }
      })
      .catch((error) => {
        if (isCurrent) {
          setUpcomingClasses([])
          setClassesError(error.message)
        }
      })
      .finally(() => {
        if (isCurrent) setClassesLoading(false)
      })

    return () => {
      isCurrent = false
    }
  }, [activeStudentId])

  async function refreshSelectedTeacher(uuid) {
    try {
      const teacher = await requestJson(`/api/profesores/${uuid}/`)
      setSelectedTeacher(teacher)
      setSelectedSlotId('')
      setTeacherError('')
    } catch (error) {
      setTeacherError(error.message)
    }
  }

  async function bookSelectedSlot() {
    if (!selectedSlotId) return
    if (!activeStudentId) {
      setBookingError('No se pudo identificar al alumno de demo. Revisá la conexión con el backend.')
      return
    }

    setBookingSlotId(selectedSlotId)
    setBookingError('')
    setBookingSuccess(null)

    try {
      const reservation = await requestJson(
        `/api/horarios/${selectedSlotId}/reservar/`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ alumno_id: activeStudentId }),
        },
      )
      setBookingSuccess(reservation)
      setClassesError('')
      setClassesLoading(true)
      await Promise.all([
        refreshSelectedTeacher(selectedTeacherId),
        requestJson(`/api/alumnos/${activeStudentId}/reservas/`)
          .then(setUpcomingClasses)
          .catch((error) => setClassesError(error.message)),
      ])
      setClassesLoading(false)
    } catch (error) {
      setBookingError(error.message)
      if (error.message.toLowerCase().includes('reserv')) {
        await refreshSelectedTeacher(selectedTeacherId)
      }
    } finally {
      setBookingSlotId('')
    }
  }

  const selectedSlot = selectedTeacher?.horarios_disponibles.find(
    (slot) => slot.uuid === selectedSlotId,
  )

  return (
    <main className="app-shell">
      <header className="topbar">
        <a className="brand" href="#inicio" aria-label="Aula IA, inicio">
          <span className="brand-mark" aria-hidden="true">a.</span>
          <span>Aula<span className="brand-accent">IA</span></span>
        </a>
        <nav aria-label="Navegación principal">
          <a href="#profesores">Profesores</a>
          <a href="#mis-clases">Mis clases</a>
        </nav>
        <a className="topbar-cta" href="#profesores">Encontrá tu clase <span aria-hidden="true">↗</span></a>
      </header>

      <section className="hero" id="inicio">
        <div className="hero-copy">
          <p className="eyebrow"><span className="live-dot" /> APRENDÉ CON EXPERTOS EN IA</p>
          <h1>La próxima idea<br />empieza con una <em>clase.</em></h1>
          <p className="hero-description">
            Encontrá a tu próximo profesor, elegí un horario y empezá a llevar
            tus proyectos de inteligencia artificial más lejos.
          </p>
          <a className="button button-primary" href="#profesores">
            Explorar profesores <span aria-hidden="true">↓</span>
          </a>
          <div className="hero-note"><span aria-hidden="true">✳</span> Clases 1 a 1 · A tu ritmo · 100% online</div>
        </div>
        <div className="hero-art" aria-hidden="true">
          <div className="orbit orbit-one" />
          <div className="orbit orbit-two" />
          <div className="art-card art-card-top"><span className="art-icon">✳</span><span>IDEAS EN MOVIMIENTO</span></div>
          <div className="art-core"><span className="core-spark">✳</span><span>IA</span></div>
          <div className="art-card art-card-bottom"><span className="art-avatar">✦</span><span><strong>Tu próximo paso</strong><small>está más cerca</small></span><span className="art-arrow">↗</span></div>
          <span className="art-star star-one">✳</span>
          <span className="art-star star-two">✦</span>
          <span className="art-caption">APRENDIZAJE<br />CON PROPÓSITO</span>
        </div>
      </section>

      <section className="section teachers-section" id="profesores">
        <div className="section-heading">
          <div>
            <p className="eyebrow">01 — ENCONTRÁ TU GUÍA</p>
            <h2>Aprendé de quienes<br /><em>lo están haciendo.</em></h2>
          </div>
          <p className="section-intro">Personas expertas, clases personalizadas y el conocimiento que necesitás para dar el siguiente paso.</p>
        </div>

        {teachersLoading && <p className="notice">Buscando profesores...</p>}
        {teachersError && <p className="notice notice-error" role="alert">{teachersError}</p>}
        {!teachersLoading && !teachersError && teachers.length === 0 && (
          <p className="notice">Todavía no hay profesores disponibles.</p>
        )}

        <div className="teacher-grid">
          {teachers.map((teacher, index) => {
            const specialties = teacher.especialidades
              .split(',')
              .map((specialty) => specialty.trim())
              .filter(Boolean)
            return (
              <article className={`teacher-card teacher-card-${index % 3}`} key={teacher.uuid}>
                <div className="teacher-card-top">
                  <span className="teacher-index">0{index + 1}</span>
                  <span className="teacher-spark" aria-hidden="true">✳</span>
                </div>
                <h3>{teacher.nombre}</h3>
                <p className="teacher-description">{teacher.descripcion || 'Docente experto en inteligencia artificial.'}</p>
                <div className="specialty-list">
                  {specialties.map((specialty) => <span className="specialty-tag" key={specialty}>{specialty}</span>)}
                </div>
                <button
                  className="text-button"
                  type="button"
                  onClick={() => {
                    if (selectedTeacherId === teacher.uuid) return
                    setBookingSuccess(null)
                    setBookingError('')
                    setTeacherError('')
                    setTeacherLoading(true)
                    setSelectedTeacher(null)
                    setSelectedSlotId('')
                    setSelectedTeacherId(teacher.uuid)
                  }}
                  aria-expanded={selectedTeacherId === teacher.uuid}
                >
                  Ver horarios <span aria-hidden="true">↗</span>
                </button>
              </article>
            )
          })}
        </div>

        {selectedTeacherId && (
          <section className="schedule-panel" aria-labelledby="schedule-title">
            {teacherLoading && <p className="notice">Cargando perfil y horarios...</p>}
            {teacherError && <p className="notice notice-error" role="alert">{teacherError}</p>}
            {selectedTeacher && (
              <>
                <div className="schedule-heading">
                  <div>
                    <p className="eyebrow">HORARIOS DISPONIBLES</p>
                    <h3 id="schedule-title">Una clase con {selectedTeacher.nombre}</h3>
                    <p>{selectedTeacher.descripcion}</p>
                  </div>
                  <button className="close-button" type="button" onClick={() => setSelectedTeacherId('')} aria-label="Cerrar horarios">×</button>
                </div>
                {selectedTeacher.horarios_disponibles.length === 0 ? (
                  <p className="empty-state">Por ahora no hay horarios libres. Volvé pronto para encontrar nuevas opciones.</p>
                ) : (
                  <>
                    <div className="slot-list">
                      {selectedTeacher.horarios_disponibles.map((slot) => (
                        <label className={`slot-option${selectedSlotId === slot.uuid ? ' slot-selected' : ''}`} key={slot.uuid}>
                          <input
                            type="radio"
                            name="horario"
                            value={slot.uuid}
                            checked={selectedSlotId === slot.uuid}
                            onChange={() => setSelectedSlotId(slot.uuid)}
                          />
                          <span className="slot-date">{formatDateTime(slot.inicio)}</span>
                          <span className="slot-duration">{slot.duracion_minutos} min</span>
                          <span className="slot-check" aria-hidden="true">{selectedSlotId === slot.uuid ? '✓' : '+'}</span>
                        </label>
                      ))}
                    </div>
                    <div className="booking-controls">
                      <button
                        className="button button-dark"
                        type="button"
                                      disabled={!selectedSlotId || Boolean(bookingSlotId) || demoStudentLoading || !activeStudentId}
                        onClick={bookSelectedSlot}
                      >
                        {bookingSlotId ? 'Confirmando...' : 'Reservar esta clase'}
                        {!bookingSlotId && <span aria-hidden="true">↗</span>}
                      </button>
                      {selectedSlot && <span className="booking-time">Seleccionaste {formatDateTime(selectedSlot.inicio)}</span>}
                    </div>
                    {bookingError && <p className="notice notice-error" role="alert">{bookingError}</p>}
                    {bookingSuccess && (
                      <p className="notice notice-success" role="status">
                        ¡Reserva confirmada! Tu clase con {bookingSuccess.profesor} es el {formatReservationDateTime(bookingSuccess)}.
                      </p>
                    )}
                  </>
                )}
              </>
            )}
          </section>
        )}
      </section>

      <section className="section classes-section" id="mis-clases">
        <div className="classes-layout">
          <div className="classes-copy">
            <p className="eyebrow">02 — TU CAMINO DE APRENDIZAJE</p>
            <h2>Un paso a la vez.<br /><em>Todo por delante.</em></h2>
            <p>Guardá tus próximas clases en un solo lugar. Tu perfil de alumno demo se carga automáticamente para esta sesión.</p>
            <div className="demo-session" aria-live="polite">
              <span className="demo-session-icon" aria-hidden="true">✓</span>
              <span>
                <strong>{demoStudentLoading ? 'Cargando alumno demo...' : studentName || 'Sesión demo no disponible'}</strong>
                <small>
                  {demoStudentError
                    ? 'Iniciá el backend y ejecutá python manage.py cargar_demo.'
                    : activeStudentId ? 'Sesión de alumno iniciada' : 'Conectando con el backend'}
                </small>
              </span>
            </div>
            {demoStudentError && <p className="notice notice-error" role="alert">{demoStudentError}</p>}
          </div>
          <div className="classes-list">
            <div className="classes-list-heading">
              <div><span className="list-kicker">AGENDA</span><h3>Mis próximas clases</h3></div>
              <span className="class-count">{upcomingClasses.length.toString().padStart(2, '0')}</span>
            </div>
            {classesLoading && <p className="notice">Cargando tus clases...</p>}
            {classesError && <p className="notice notice-error" role="alert">{classesError}</p>}
            {!classesLoading && !classesError && !demoStudentLoading && !demoStudentError && activeStudentId && upcomingClasses.length === 0 && (
              <p className="empty-state">Todavía no tenés clases programadas. Elegí un profesor y reservá tu primer horario.</p>
            )}
            {!classesLoading && !classesError && upcomingClasses.map((reservation) => (
              <article className="reservation-row" key={reservation.uuid}>
                <div className="reservation-date-icon" aria-hidden="true">✳</div>
                <div className="reservation-info">
                  <h4>{reservation.profesor}</h4>
                  <p>{reservation.especialidades}</p>
                  <span>{formatReservationDateTime(reservation)}</span>
                </div>
                <span className="reservation-status">{reservation.estado}</span>
              </article>
            ))}
          </div>
        </div>
      </section>

      <footer className="footer">
        <a className="brand" href="#inicio"><span className="brand-mark" aria-hidden="true">a.</span><span>Aula<span className="brand-accent">IA</span></span></a>
        <span>Un espacio para aprender lo que viene.</span>
        <a href="#inicio">Volver arriba ↑</a>
      </footer>
    </main>
  )
}

export default App
