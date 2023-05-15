from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import QueuePool, NullPool
# from utils.Secrets import Secretos
from Utils.Aws import Aws
import json

#Excepciones
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import FlushError

base_class = declarative_base()  # Extend class for models


class Database():

    # Mode can be:
    # dbr: Mode Read
    # dbw: Mode Write
    def __init__(self, mode):
        if mode is None or (mode != "dbw" and mode != "dbr"):
            raise Warning("El modo de uso de base de datos no es válido.")

        try:
            connection_data = Aws.get_secret(f'{mode}-fcc')

            # Get connections strings from secret manager
            __connection_strings = self.__get_connection_strings(
                connection_data)

            # Create a engine DB
            self.__engine = create_engine(
                __connection_strings,
                poolclass=QueuePool
            )
            # Create the association between the engine and the session
            self.__session_maker = sessionmaker(bind=self.__engine)
            # Create a new session
            self.session = self.__session_maker()

        except Exception as e:
            print(f'Error en conexion Base de datos: {e}')
            raise Exception('Error en conexion Base de datos')

    def __get_connection_strings(self, credentials_data):
        """
        Get the connection strings from the credentials
        :param credentials_data:
            Credentials data
        :return:
            Connection strings
        """

        string_conexion = "mysql+pymysql://{0}:{1}@{2}/{3}".format(
            credentials_data["username"],
            credentials_data["password"],
            credentials_data["host"],
            credentials_data["bd_name"],
        )
        # Se retorna la cadena de conexion
        return string_conexion
