#  BTS WORLD

Proyecto integrador de Desarrollo de Software — Aplicación web sobre el grupo de K-Pop **BTS (방탄소년단)**.

---

##  Stack tecnológico

| Capa | Tecnología |
|------|-----------|
| Backend | FastAPI + Python 3.11 |
| ORM / Validación | SQLModel + Pydantic |
| Base de datos | NeonDB (PostgreSQL serverless) |
| Almacenamiento de imágenes | Supabase Storage |
| Frontend | Jinja2 + Bootstrap 5 + Chart.js |
| Despliegue | Render |
| Control de versiones | GitHub |

---

##  Estructura del proyecto

```
BTS_WEB/
├── main.py                  ← Rutas HTML, API JSON y formularios
├── db.py                    ← Conexión a NeonDB
├── utils.py                 ← Subida de imágenes a Supabase
├── requirements.txt
├── .env.example             ← Plantilla de variables de entorno
│
├── models/                  ← Modelos Pydantic + SQLModel
│   ├── integrante.py        ← Tabla: integrante
│   ├── album.py             ← Tabla: album
│   ├── tour.py              ← Tabla: tour (FK → album)
│   └── voto.py              ← Tabla: votofan (FK → integrante)
│
├── operations/              ← Lógica de negocio (CRUD)
│   ├── operations_integrantes.py
│   ├── operations_albumes.py
│   ├── operations_tours.py
│   └── operations_votos.py
│
├── templates/               ← HTML con Jinja2
│   ├── base.html            ← Layout base (navbar + footer)
│   ├── index.html           ← Inicio (info BTS, video, premios)
│   ├── integrantes.html     ← Cards CRUD de integrantes
│   ├── albumes.html         ← Cards CRUD de álbumes
│   ├── tours.html           ← Lista CRUD de tours
│   ├── dashboard.html       ← Gráficas + formulario de voto
│   └── buscar.html          ← Resultados de búsqueda global
│
└── static/
    ├── css/style.css        ← Tema BTS (púrpura oscuro)
    └── js/bts.js            ← JavaScript global
```

---

##  Modelos y relaciones

```
Integrante (1) ──────────── (N) VotoFan
   id, nombre, edad,              id, nombre_fan,
   altura, rol,                   integrante_id (FK),
   imagen_url, estado             comentario, fecha

Album (1) ───────────────── (N) Tour
   id, nombre, anio,              id, nombre,
   num_canciones,                 ciudades_visitadas,
   imagen_url, estado             anio, album_id (FK), estado
```

---

## 🔗 Endpoints principales

### Páginas HTML
| Ruta | Descripción |
|------|-------------|
| `GET /` | Inicio: info BTS, video YouTube, premios |
| `GET /integrantes` | Cards de los 7 integrantes con CRUD |
| `GET /albumes` | Discografía con CRUD |
| `GET /tours` | Tours con relación a álbumes |
| `GET /dashboard` | Gráficas de popularidad + formulario de voto |
| `GET /buscar?q=xxx` | Búsqueda global en todos los modelos |

### API JSON (documentación automática en `/docs`)
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/integrantes` | Lista integrantes activos |
| POST | `/api/integrantes` | Crear integrante |
| PATCH | `/api/integrantes/{id}` | Editar integrante |
| DELETE | `/api/integrantes/{id}` | Desactivar (soft delete) |
| POST | `/api/integrantes/{id}/imagen` | Subir foto a Supabase |
| GET | `/api/albumes` | Lista álbumes |
| POST | `/api/albumes` | Crear álbum |
| PATCH | `/api/albumes/{id}` | Editar álbum |
| DELETE | `/api/albumes/{id}` | Desactivar álbum |
| GET | `/api/tours` | Lista tours |
| POST | `/api/tours` | Crear tour |
| PATCH | `/api/tours/{id}` | Editar tour |
| DELETE | `/api/tours/{id}` | Cancelar tour |
| GET | `/api/votos` | Lista votos |
| POST | `/api/votos` | Registrar voto |
| GET | `/api/dashboard/stats` | Estadísticas de popularidad |
| POST | `/seed` | **Poblar BD con datos reales de BTS (1 sola vez)** |

---

## ⚙️ Configuración local (PyCharm)

### 1. Clonar el repositorio
```bash
git clone https://github.com/TU_USUARIO/BTS_WEB.git
cd BTS_WEB
```

### 2. Crear entorno virtual y activar
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Mac/Linux:
source .venv/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Crear el archivo `.env`
Copia `.env.example` como `.env` y llena tus credenciales:
```
DATABASE_URL=postgresql+psycopg2://...   ← de NeonDB
SUPABASE_URL=https://xxxx.supabase.co
SUPABASE_KEY=eyJ...
SUPABASE_BUCKET=bts-imagenes
```

### 5. Arrancar el servidor
```bash
uvicorn main:app --reload
```

### 6. Poblar la base de datos (UNA sola vez)
Abre el navegador en: `http://localhost:8000/docs` → ejecutar `POST /seed`
O desde terminal:
```bash
curl -X POST http://localhost:8000/seed
```

---

##  Despliegue en Render

1. Sube el proyecto a GitHub (sin el `.env`)
2. En [render.com](https://render.com) → **New Web Service** → conectar tu repo
3. Configuración:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. En **Environment Variables** agrega `DATABASE_URL`, `SUPABASE_URL`, `SUPABASE_KEY`, `SUPABASE_BUCKET`
5. Deploy → esperar ~2 minutos → URL pública disponible
6. Visita `https://TU-APP.onrender.com/seed` para poblar la BD

---

##  Configuración de Supabase

1. Crear proyecto en [supabase.com](https://supabase.com)
2. Storage → **New bucket** → nombre: `bts-imagenes` → marcar como **Public**
3. Copiar `Project URL` y `public key` al `.env`

---

