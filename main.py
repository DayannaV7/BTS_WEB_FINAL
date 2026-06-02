# BTS WORLD FastAPI App
# Ejecutar: uvicorn main:app --reload

from fastapi import FastAPI, HTTPException, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Optional
from datetime import timedelta
from db import create_all_tables, SessionDep
from utils import subir_imagen

# Modelos
from models.integrante import Integrante, IntegranteBase, IntegranteUpdate
from models.album      import Album, AlbumBase, AlbumUpdate
from models.tour       import Tour, TourBase, TourUpdate
from models.voto       import VotoFan, VotoBase

#Operaciones
from operations.operations_integrantes import (
    crear_integrante, ver_integrantes, buscar_por_id as buscar_integrante_id,
    buscar_por_nombre as buscar_integrante_nombre,
    editar_integrante, actualizar_imagen as actualizar_img_integrante,
    desactivar_integrante, ver_historial
)
from operations.operations_albumes import (
    crear_album, ver_albumes, buscar_por_id as buscar_album_id,
    buscar_por_nombre as buscar_album_nombre,
    editar_album, actualizar_imagen as actualizar_img_album, desactivar_album
)
from operations.operations_tours import (
    crear_tour, ver_tours, buscar_por_id as buscar_tour_id,
    buscar_por_ciudad, editar_tour, cancelar_tour, tours_del_album
)
from operations.operations_votos import (
    crear_voto, ver_votos, votos_recientes, estadisticas_popularidad
)

app = FastAPI(
    lifespan=create_all_tables,
    title="BTS WORLD API",
    description="API del proyecto BTS: integrantes, álbumes, tours y popularidad ARMY.",
    version="1.0.0",
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

#RUTAS HTML


@app.get("/", response_class=HTMLResponse, tags=["HTML"])
def inicio(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/integrantes", response_class=HTMLResponse, tags=["HTML"])
def pagina_integrantes(request: Request, session: SessionDep,
                       mensaje: str = "", tipo_mensaje: str = "success"):
    integrantes = ver_integrantes(session)
    return templates.TemplateResponse("integrantes.html", {
        "request": request,
        "integrantes": integrantes,
        "mensaje": mensaje,
        "tipo_mensaje": tipo_mensaje
    })


@app.get("/albumes", response_class=HTMLResponse, tags=["HTML"])
def pagina_albumes(request: Request, session: SessionDep,
                   mensaje: str = "", tipo_mensaje: str = "success"):
    albumes = ver_albumes(session)
    return templates.TemplateResponse("albumes.html", {
        "request": request,
        "albumes": albumes,
        "mensaje": mensaje,
        "tipo_mensaje": tipo_mensaje
    })


@app.get("/tours", response_class=HTMLResponse, tags=["HTML"])
def pagina_tours(request: Request, session: SessionDep,
                 album_id: Optional[int] = None,
                 mensaje: str = "", tipo_mensaje: str = "success"):
    if album_id:
        tours = tours_del_album(album_id, session)
    else:
        tours = ver_tours(session)
    albumes = ver_albumes(session)
    return templates.TemplateResponse("tours.html", {
        "request": request,
        "tours": tours,
        "albumes": albumes,
        "mensaje": mensaje,
        "tipo_mensaje": tipo_mensaje
    })


@app.get("/dashboard", response_class=HTMLResponse, tags=["HTML"])
def pagina_dashboard(request: Request, session: SessionDep,
                     mensaje: str = "", tipo_mensaje: str = "success"):
    stats        = estadisticas_popularidad(session)
    recientes    = votos_recientes(session, limite=8)
    integrantes  = ver_integrantes(session)
    albumes      = ver_albumes(session)
    total_votos  = sum(s.total_votos for s in stats)
    # Mapear integrante_id → nombre para la tabla de votos
    nombres_mapa = {i.id: i.nombre for i in integrantes}
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "stats":                stats,
        "votos_recientes":      recientes,
        "integrantes":          integrantes,
        "albumes":              albumes,
        "timedelta": timedelta(hours=-5),
        "total_votos":          total_votos,
        "total_albumes":        len(albumes),
        "nombres_chart":        [s.nombre_integrante for s in stats],
        "votos_chart":          [s.total_votos        for s in stats],
        "nombres_integrantes":  nombres_mapa,
        "mensaje":              mensaje,
        "tipo_mensaje":         tipo_mensaje
    })


@app.get("/buscar", response_class=HTMLResponse, tags=["HTML"])
def buscar_global(request: Request, session: SessionDep, q: str = ""):
    integrantes = buscar_integrante_nombre(q, session) if q else []
    albumes     = buscar_album_nombre(q, session)      if q else []
    tours       = buscar_por_ciudad(q, session)        if q else []
    total       = len(integrantes) + len(albumes) + len(tours)
    return templates.TemplateResponse("buscar.html", {
        "request":    request,
        "query":      q,
        "integrantes": integrantes,
        "albumes":    albumes,
        "tours":      tours,
        "total":      total
    })



#FORMULARIOS HTML (POST redirect con mensaje)

@app.post("/form/integrantes", tags=["Formularios"])
async def form_crear_integrante(
    session: SessionDep,
    nombre:      str   = Form(...),
    edad:        int   = Form(...),
    altura:      float = Form(...),
    rol:         str   = Form(...),
    descripcion: str   = Form(""),
    imagen:      UploadFile = File(None)
):
    base = IntegranteBase(nombre=nombre, edad=edad, altura=altura,
                          rol=rol, descripcion=descripcion or None)
    nuevo = crear_integrante(base, session)
    if imagen and imagen.filename:
        url = subir_imagen(imagen, carpeta="integrantes")
        actualizar_img_integrante(nuevo.id, url, session)
    return RedirectResponse("/integrantes?mensaje=Integrante+creado+exitosamente", status_code=303)


@app.post("/form/albumes", tags=["Formularios"])
async def form_crear_album(
    session: SessionDep,
    nombre:        str   = Form(...),
    num_canciones: int   = Form(...),
    anio:          int   = Form(...),
    descripcion:   str   = Form(""),
    imagen:        UploadFile = File(None)
):
    base = AlbumBase(nombre=nombre, num_canciones=num_canciones,
                     anio=anio, descripcion=descripcion or None)
    nuevo = crear_album(base, session)
    if imagen and imagen.filename:
        url = subir_imagen(imagen, carpeta="albumes")
        actualizar_img_album(nuevo.id, url, session)
    return RedirectResponse("/albumes?mensaje=Album+creado+exitosamente", status_code=303)


@app.post("/form/tours", tags=["Formularios"])
async def form_crear_tour(
    session: SessionDep,
    nombre:            str = Form(...),
    ciudades_visitadas: str = Form(...),
    anio:              int = Form(...),
    album_id:          int = Form(...)
):
    # Validar que el álbum existe
    album = buscar_album_id(album_id, session)
    if not album:
        return RedirectResponse(
            f"/tours?mensaje=El+album+ID+{album_id}+no+existe&tipo_mensaje=danger",
            status_code=303
        )
    base = TourBase(nombre=nombre, ciudades_visitadas=ciudades_visitadas,
                    anio=anio, album_id=album_id)
    crear_tour(base, session)
    return RedirectResponse("/tours?mensaje=Tour+creado+exitosamente", status_code=303)


@app.post("/form/votar", tags=["Formularios"])
async def form_votar(
    session: SessionDep,
    nombre_fan:    str           = Form(...),
    integrante_id: int           = Form(...),
    comentario:    Optional[str] = Form(None)
):
    # Validar que el integrante existe
    integrante = buscar_integrante_id(integrante_id, session)
    if not integrante or integrante.estado == "inactivo":
        return RedirectResponse(
            "/dashboard?mensaje=Integrante+no+encontrado&tipo_mensaje=danger",
            status_code=303
        )
    base = VotoBase(nombre_fan=nombre_fan, integrante_id=integrante_id,
                    comentario=comentario)
    crear_voto(base, session)
    return RedirectResponse(
        f"/dashboard?mensaje=Gracias+{nombre_fan}+tu+voto+fue+registrado",
        status_code=303
    )



#API JSON INTEGRANTES

@app.get("/api/integrantes", tags=["API — Integrantes"])
def api_ver_integrantes(request: Request, session: SessionDep, q: Optional[str] = None):
    """GET: lista integrantes activos. Pasa ?q=nombre para buscar."""
    if q:
        return buscar_integrante_nombre(q, session)
    return ver_integrantes(session)


@app.post("/api/integrantes", tags=["API — Integrantes"])
def api_crear_integrante(datos: IntegranteBase, session: SessionDep):
    return crear_integrante(datos, session)


@app.get("/api/integrantes/{id}", tags=["API — Integrantes"])
def api_un_integrante(id: int, session: SessionDep):
    i = buscar_integrante_id(id, session)
    if not i:
        raise HTTPException(404, f"Integrante con ID {id} no encontrado")
    return i


@app.patch("/api/integrantes/{id}", tags=["API — Integrantes"])
def api_editar_integrante(id: int, datos: IntegranteUpdate, session: SessionDep):
    actualizado = editar_integrante(id, datos, session)
    if not actualizado:
        raise HTTPException(404, f"Integrante con ID {id} no encontrado o inactivo")
    return actualizado


@app.delete("/api/integrantes/{id}", tags=["API — Integrantes"])
def api_desactivar_integrante(id: int, session: SessionDep):
    i = buscar_integrante_id(id, session)
    if not i:
        raise HTTPException(404, f"Integrante con ID {id} no encontrado")
    if i.estado == "inactivo":
        raise HTTPException(409, f"El integrante {id} ya está inactivo")
    return desactivar_integrante(id, session)


@app.post("/api/integrantes/{id}/imagen", tags=["API — Integrantes"])
async def api_imagen_integrante(id: int, session: SessionDep,
                                imagen: UploadFile = File(...)):
    i = buscar_integrante_id(id, session)
    if not i:
        raise HTTPException(404, "Integrante no encontrado")
    url = subir_imagen(imagen, carpeta="integrantes")
    return actualizar_img_integrante(id, url, session)



#API JSON ÁLBUMES

@app.get("/api/albumes", tags=["API — Álbumes"])
def api_ver_albumes(session: SessionDep):
    return ver_albumes(session)


@app.post("/api/albumes", tags=["API — Álbumes"])
def api_crear_album(datos: AlbumBase, session: SessionDep):
    return crear_album(datos, session)


@app.get("/api/albumes/{id}", tags=["API — Álbumes"])
def api_un_album(id: int, session: SessionDep):
    a = buscar_album_id(id, session)
    if not a:
        raise HTTPException(404, f"Álbum con ID {id} no encontrado")
    return a


@app.patch("/api/albumes/{id}", tags=["API — Álbumes"])
def api_editar_album(id: int, datos: AlbumUpdate, session: SessionDep):
    a = editar_album(id, datos, session)
    if not a:
        raise HTTPException(404, f"Álbum con ID {id} no encontrado o inactivo")
    return a


@app.delete("/api/albumes/{id}", tags=["API — Álbumes"])
def api_desactivar_album(id: int, session: SessionDep):
    a = buscar_album_id(id, session)
    if not a:
        raise HTTPException(404, f"Álbum con ID {id} no encontrado")
    return desactivar_album(id, session)


@app.post("/api/albumes/{id}/imagen", tags=["API — Álbumes"])
async def api_imagen_album(id: int, session: SessionDep,
                           imagen: UploadFile = File(...)):
    a = buscar_album_id(id, session)
    if not a:
        raise HTTPException(404, "Álbum no encontrado")
    url = subir_imagen(imagen, carpeta="albumes")
    return actualizar_img_album(id, url, session)



#API JSON TOURS


@app.get("/api/tours", tags=["API — Tours"])
def api_ver_tours(session: SessionDep, ciudad: Optional[str] = None):
    if ciudad:
        return buscar_por_ciudad(ciudad, session)
    return ver_tours(session)


@app.post("/api/tours", tags=["API — Tours"])
def api_crear_tour(datos: TourBase, session: SessionDep):
    album = buscar_album_id(datos.album_id, session)
    if not album:
        raise HTTPException(404, f"Álbum con ID {datos.album_id} no existe")
    return crear_tour(datos, session)


@app.patch("/api/tours/{id}", tags=["API — Tours"])
def api_editar_tour(id: int, datos: TourUpdate, session: SessionDep):
    t = editar_tour(id, datos, session)
    if not t:
        raise HTTPException(404, f"Tour con ID {id} no encontrado")
    return t


@app.delete("/api/tours/{id}", tags=["API — Tours"])
def api_cancelar_tour(id: int, session: SessionDep):
    t = buscar_tour_id(id, session)
    if not t:
        raise HTTPException(404, f"Tour con ID {id} no encontrado")
    return cancelar_tour(id, session)



#API JSON VOTOS y DASHBOARD


@app.get("/api/votos", tags=["API — Votos"])
def api_ver_votos(session: SessionDep):
    return ver_votos(session)


@app.post("/api/votos", tags=["API — Votos"])
def api_crear_voto(datos: VotoBase, session: SessionDep):
    integrante = buscar_integrante_id(datos.integrante_id, session)
    if not integrante or integrante.estado == "inactivo":
        raise HTTPException(404, "Integrante no encontrado o inactivo")
    return crear_voto(datos, session)


@app.get("/api/dashboard/stats", tags=["API — Votos"])
def api_stats(session: SessionDep):
    """Retorna estadísticas de popularidad en JSON (útil para clientes externos)."""
    return estadisticas_popularidad(session)



#  SEED Poblar BD con datos reales de BTS


@app.post("/seed", tags=["Utilidades"], summary="Poblar BD con datos de BTS")
def seed_database(session: SessionDep):
    """
    Crea los 7 integrantes, 5 álbumes y 3 tours reales de BTS.
    Ejecutar UNA sola vez después del despliegue.
    """
    from sqlmodel import select

    # Solo seedear si no hay datos
    if session.exec(select(Integrante)).first():
        return {"mensaje": "La BD ya tiene datos. Seed omitido."}

    integrantes_data = [
        {"nombre": "RM",        "edad": 30, "altura": 1.81, "rol": "Líder / Rapper Principal",
         "descripcion": "Kim Namjoon, el líder de BTS. Habla inglés con fluidez y es conocido por su profundidad lírica y activismo social."},
        {"nombre": "Jin",       "edad": 32, "altura": 1.79, "rol": "Vocalista / Visual",
         "descripcion": "Kim Seokjin, el mayor del grupo. Conocido por su humor y considerado uno de los visuales más impactantes del K-Pop."},
        {"nombre": "Suga",      "edad": 31, "altura": 1.74, "rol": "Rapper Principal / Productor",
         "descripcion": "Min Yoongi, también conocido como Agust D en sus proyectos solistas. Productor excepcional y compositor prolífico."},
        {"nombre": "J-Hope",    "edad": 30, "altura": 1.77, "rol": "Bailarín Principal / Rapper",
         "descripcion": "Jung Hoseok, la chispa del grupo. Reconocido como uno de los mejores bailarines del K-Pop y una energía positiva inigualable."},
        {"nombre": "Jimin",     "edad": 29, "altura": 1.74, "rol": "Bailarín Principal / Vocalista",
         "descripcion": "Park Jimin, conocido por su expresividad al bailar y su voz única. Primer artista coreano en debutar en el #1 del Billboard Hot 100 en solitario."},
        {"nombre": "V",         "edad": 29, "altura": 1.79, "rol": "Vocalista / Visual",
         "descripcion": "Kim Taehyung, también conocido como V. Su voz barítono y su carisma lo han convertido en uno de los ídolos más populares del mundo."},
        {"nombre": "Jungkook",  "edad": 27, "altura": 1.78, "rol": "Vocalista Principal / Maknae",
         "descripcion": "Jeon Jungkook, el miembro más joven (maknae). Talentoso en canto, baile y producción. Apodado 'Golden Maknae' por su versatilidad."},
    ]
    for d in integrantes_data:
        session.add(Integrante(**d))
    session.commit()

    albumes_data = [
        {"nombre": "Love Yourself: Her",  "num_canciones": 9,  "anio": 2017,
         "descripcion": "EP que inició la trilogía Love Yourself. Incluye el exitoso sencillo DNA."},
        {"nombre": "Map of the Soul: 7",  "num_canciones": 20, "anio": 2020,
         "descripcion": "Cuarto álbum de estudio. Exploración del yo a través de la psicología junguiana."},
        {"nombre": "BE",                  "num_canciones": 8,  "anio": 2020,
         "descripcion": "Álbum creado durante la pandemia de COVID-19. Refleja las emociones del aislamiento y la esperanza."},
        {"nombre": "Proof",               "num_canciones": 48, "anio": 2022,
         "descripcion": "Álbum antología que celebra 9 años de carrera con canciones nuevas y clásicos remasterizados."},
        {"nombre": "Wings",               "num_canciones": 15, "anio": 2016,
         "descripcion": "Segundo álbum de estudio. Inspirado en 'Demian' de Hermann Hesse. Marcó el crecimiento artístico del grupo."},
    ]
    albumes_guardados = []
    for d in albumes_data:
        a = Album(**d)
        session.add(a)
        session.commit()
        session.refresh(a)
        albumes_guardados.append(a)

    tours_data = [
        {"nombre": "Love Yourself World Tour", "ciudades_visitadas": "Seúl, Los Ángeles, Oakland, Fort Worth, Hamilton, Newark, Berlín, Amsterdam, París, Londres, Osaka, Tokio, Hong Kong, Singapur, Sydney", "anio": 2018, "album_id": albumes_guardados[0].id},
        {"nombre": "Map of the Soul Tour",     "ciudades_visitadas": "Seúl, Los Ángeles, Dallas, Orlando, Washington, San José, Londres, Berlín, París, Barcelona, Osaka, Tokio", "anio": 2020, "album_id": albumes_guardados[1].id},
        {"nombre": "Yet to Come in Busan",     "ciudades_visitadas": "Busan", "anio": 2022, "album_id": albumes_guardados[3].id},
    ]
    for d in tours_data:
        session.add(Tour(**d))
    session.commit()

    return {"mensaje": " Base de datos poblada con datos reales de BTS",
            "integrantes": 7, "albumes": 5, "tours": 3}
