from sqlalchemy.exc import NoResultFound
from sqlmodel import Session, select
from models.integrante import Integrante, IntegranteBase, IntegranteUpdate


def crear_integrante(datos: IntegranteBase, session: Session) -> Integrante:
    nuevo = Integrante.model_validate(datos)
    session.add(nuevo)
    session.commit()
    session.refresh(nuevo)
    return nuevo


def ver_integrantes(session: Session) -> list[Integrante]:
    """Solo activos."""
    return list(session.exec(select(Integrante).where(Integrante.estado == "activo")).all())


def ver_historial(session: Session) -> list[Integrante]:
    return list(session.exec(select(Integrante)).all())


def buscar_por_nombre(nombre: str, session: Session) -> list[Integrante]:
    stmt = select(Integrante).where(
        Integrante.nombre.ilike(f"%{nombre}%"),
        Integrante.estado == "activo"
    )
    return list(session.exec(stmt).all())


def buscar_por_id(id: int, session: Session) -> Integrante | None:
    try:
        return session.get_one(Integrante, id)
    except NoResultFound:
        return None


def editar_integrante(id: int, datos: IntegranteUpdate, session: Session) -> Integrante | None:
    integrante = buscar_por_id(id, session)
    if not integrante or integrante.estado == "inactivo":
        return None
    campos = datos.model_dump(exclude_unset=True)
    integrante.sqlmodel_update(campos)
    session.add(integrante)
    session.commit()
    session.refresh(integrante)
    return integrante


def actualizar_imagen(id: int, url: str, session: Session) -> Integrante | None:
    integrante = buscar_por_id(id, session)
    if not integrante:
        return None
    integrante.imagen_url = url
    session.add(integrante)
    session.commit()
    session.refresh(integrante)
    return integrante


def desactivar_integrante(id: int, session: Session) -> Integrante | None:
    integrante = buscar_por_id(id, session)
    if not integrante:
        return None
    integrante.estado = "inactivo"
    session.add(integrante)
    session.commit()
    session.refresh(integrante)
    return integrante
