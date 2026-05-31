from sqlalchemy.exc import NoResultFound
from sqlmodel import Session, select
from models.album import Album, AlbumBase, AlbumUpdate


def crear_album(datos: AlbumBase, session: Session) -> Album:
    nuevo = Album.model_validate(datos)
    session.add(nuevo)
    session.commit()
    session.refresh(nuevo)
    return nuevo


def ver_albumes(session: Session) -> list[Album]:
    return list(session.exec(select(Album).where(Album.estado == "activo")).all())


def buscar_por_id(id: int, session: Session) -> Album | None:
    try:
        return session.get_one(Album, id)
    except NoResultFound:
        return None


def buscar_por_nombre(nombre: str, session: Session) -> list[Album]:
    stmt = select(Album).where(
        Album.nombre.ilike(f"%{nombre}%"),
        Album.estado == "activo"
    )
    return list(session.exec(stmt).all())


def editar_album(id: int, datos: AlbumUpdate, session: Session) -> Album | None:
    album = buscar_por_id(id, session)
    if not album or album.estado == "inactivo":
        return None
    campos = datos.model_dump(exclude_unset=True)
    album.sqlmodel_update(campos)
    session.add(album)
    session.commit()
    session.refresh(album)
    return album


def actualizar_imagen(id: int, url: str, session: Session) -> Album | None:
    album = buscar_por_id(id, session)
    if not album:
        return None
    album.imagen_url = url
    session.add(album)
    session.commit()
    session.refresh(album)
    return album


def desactivar_album(id: int, session: Session) -> Album | None:
    album = buscar_por_id(id, session)
    if not album:
        return None
    album.estado = "inactivo"
    session.add(album)
    session.commit()
    session.refresh(album)
    return album
