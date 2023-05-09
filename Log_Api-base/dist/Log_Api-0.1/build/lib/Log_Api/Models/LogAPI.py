from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class LogAPI(Base):
    __tablename__ = 'LOG_APIS'
    ID = Column(Integer, primary_key=True,
                autoincrement=True, comment='Id del registro')
    USERNAME = Column(String, nullable=True,
                      comment='Nombre del usuario que consume el servicio')
    PATH = Column(String, nullable=False, comment='Ruta de la api')
    DOMAIN_NAME = Column(String, nullable=True, comment='Host de la api')
    METHOD = Column(String, nullable=False, comment='Metodo de solicitud')
    STATUS_CODE = Column(Integer, nullable=True,
                         comment='Codigo de estado de la respuesta')
    HEADERS_RESPONSE = Column(Text, nullable=True, comment='Cabecera de la respuesta')
    BODY_RESPONSE = Column(Text, nullable=True,
                           comment='Payload de la respuesta')
    HEADERS = Column(Text, nullable=False, comment='Cabecera de la solicitud')
    BODY = Column(Text, nullable=True, comment='Payload de la solicitud')
    QUERY_STR_PARAMETERS = Column(
        Text, nullable=True, comment='Query string parameters')
    PATH_PARAMETERS = Column(Text, nullable=True, comment='Path parameters')
    COOKIES = Column(Text, nullable=True)
    RAW_QUERY_STR = Column(Text, nullable=True)
    REQUEST_CONTEXT = Column(Text, nullable=True)
    AWS_CONTEXT = Column(Text, nullable=True)
    IP = Column(String, nullable=False, comment='Ip del cliente')
    USER_AGENT = Column(Text, nullable=True, comment='User agent del cliente')
    VERSION = Column(String, nullable=True, comment='Version de la respuesta')
    TIME = Column(String, nullable=True,
                  comment='Fecha en la que se ejecuto la api')

