from sqlmodel import Session, select, func
from models.voto import VotoFan, VotoBase, VotoStats
from models.integrante import Integrante


def crear_voto(datos: VotoBase, session: Session) -> VotoFan:
    nuevo = VotoFan.model_validate(datos)
    session.add(nuevo)
    session.commit()
    session.refresh(nuevo)
    return nuevo


def ver_votos(session: Session) -> list[VotoFan]:
    return list(session.exec(select(VotoFan).order_by(VotoFan.fecha.desc())).all())


def votos_recientes(session: Session, limite: int = 10) -> list[VotoFan]:
    stmt = select(VotoFan).order_by(VotoFan.fecha.desc()).limit(limite)
    return list(session.exec(stmt).all())


def estadisticas_popularidad(session: Session) -> list[VotoStats]:
    """Calcula votos por integrante para el dashboard."""
    # Contar votos por integrante
    stmt = (
        select(VotoFan.integrante_id, func.count(VotoFan.id).label("total"))
        .group_by(VotoFan.integrante_id)
    )
    conteos = {row.integrante_id: row.total for row in session.exec(stmt).all()}

    total_global = sum(conteos.values()) or 1  # Evitar división por cero

    # Traer todos los integrantes activos y armar estadísticas
    integrantes = list(session.exec(
        select(Integrante).where(Integrante.estado == "activo")
    ).all())

    stats = []
    for i in integrantes:
        votos = conteos.get(i.id, 0)
        stats.append(VotoStats(
            integrante_id=i.id,
            nombre_integrante=i.nombre,
            imagen_url=i.imagen_url,
            total_votos=votos,
            porcentaje=round((votos / total_global) * 100, 1)
        ))

    # Ordenar de mayor a menor popularidad
    return sorted(stats, key=lambda x: x.total_votos, reverse=True)
