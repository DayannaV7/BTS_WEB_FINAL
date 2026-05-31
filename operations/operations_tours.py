from sqlalchemy.exc import NoResultFound
from sqlmodel import Session, select
from models.tour import Tour, TourBase, TourUpdate


def crear_tour(datos: TourBase, session: Session) -> Tour:
    nuevo = Tour.model_validate(datos)
    session.add(nuevo)
    session.commit()
    session.refresh(nuevo)
    return nuevo


def ver_tours(session: Session) -> list[Tour]:
    return list(session.exec(select(Tour).where(Tour.estado == "activo")).all())


def tours_del_album(album_id: int, session: Session) -> list[Tour]:
    stmt = select(Tour).where(Tour.album_id == album_id, Tour.estado == "activo")
    return list(session.exec(stmt).all())


def buscar_por_id(id: int, session: Session) -> Tour | None:
    try:
        return session.get_one(Tour, id)
    except NoResultFound:
        return None


def buscar_por_ciudad(ciudad: str, session: Session) -> list[Tour]:
    stmt = select(Tour).where(
        Tour.ciudades_visitadas.ilike(f"%{ciudad}%"),
        Tour.estado == "activo"
    )
    return list(session.exec(stmt).all())


def editar_tour(id: int, datos: TourUpdate, session: Session) -> Tour | None:
    tour = buscar_por_id(id, session)
    if not tour or tour.estado == "inactivo":
        return None
    campos = datos.model_dump(exclude_unset=True)
    tour.sqlmodel_update(campos)
    session.add(tour)
    session.commit()
    session.refresh(tour)
    return tour


def cancelar_tour(id: int, session: Session) -> Tour | None:
    tour = buscar_por_id(id, session)
    if not tour:
        return None
    tour.estado = "inactivo"
    session.add(tour)
    session.commit()
    session.refresh(tour)
    return tour
