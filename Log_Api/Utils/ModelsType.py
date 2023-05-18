import json
from sqlalchemy import Column, Integer, String, sql
from ..Class.Database import declarative_base as BASE

class Model:
    """
    Clase para generar los modelos de la base de datos de tipo detalle
    """
    @classmethod
    def create(cls, table_name):
        """
        Función para crear el modelo de cualquier tabla de tipo detalle
        :param table_name: str 
            Nombre de la tabla
        return: Modelo de la tabla
            id: Identificador del registro
            name: Nombre del registro
            code: Código del registro
            description: Descripción del registro (opcional)
            status: Estado del registro (1: Activo, 0: Inactivo)
            date: Fecha de creación del registro
            date_update: Fecha de actualización del registro
        """
        class Table(BASE()):
            __tablename__ = table_name
            
            id_table = Column('ID', Integer, primary_key=True)
            code = Column('CODE', String)
            name = Column('NAME', String)
            description = Column('DESCRIPTION', String, nullable=True)
            status = Column('STATUS', Integer, nullable=False)
            date = Column('DATE_REG',
                        String, nullable=False,
                        server_default=sql.func.now()
            )
            date_update = Column('DATE_UPDATE',
                        String, nullable=True,
                        server_default=sql.null()
            )

            def __init__(self, table_name):
                self.__tablename__ = table_name

            def get_id(self, name: str, session):
                """
                Obtiene el id del registro a partir del nombre
                :param name: str
                    Nombre del registro
                :param session: Session
                    Sesión de la base de datos
                :return: int
                    Id de la tabla
                """
                # data = session.query(self.id_table).filter_by(name=name).first()
                data = session.query(self.id_table).filter(self.name.ilike(f"%{name}%")).first()
                if data:
                    id_table = data.id_table
                else:
                    id_table = sql.null()
                # print(data.id_table)
                return id_table
            
            def get_id_code(self, code: str, session):
                """
                Obtiene el id del registro a partir del código
                :param code: str
                    Código del registro
                :param session: Session
                    Sesión de la base de datos
                :return: int
                    Id de la tabla
                """
                data = session.query(self.id_table).filter_by(code=code).first()
                if data:
                    id_table = data.id_table
                else:
                    id_table = sql.null()
                return id_table

            def __repr__(self) -> str:
                columns = {
                    "id": self.id_table,
                    "code": self.code,
                    "name": self.name,
                    "status": self.status,
                    "date": str(self.date),
                    "user": str(self.date_update)
                }
                return json.dumps(columns)
        return Table