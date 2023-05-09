from json import loads
from datetime import datetime
from Utils.Response import Response
from Class.Database import Database
from Models.LogAPI import LogAPI
import traceback
class Log(Response):
    @classmethod
    def filter(cls, filter):
        """
        Filter the logs by path and query
        :param query: 
            Query to filter
        :return: 
            List of logs
        """
        session = Database('dbr').session
        try:
            if filter is None:
                return Log.bad_request('No se encontró ningún parámetro en la ruta')
            
            filters = []
            limit = filter.get('limit', None)
            offset = filter.get('offset', None)
            
            limit = int(limit) if limit else None
            offset = int(offset) if offset else None
            offset = 0 if (offset - 1) < 0 else (offset - 1)
            if filter:
                for key, value in filter.items():
                    if key in ['limit', 'offset']: continue
                    if key not in LogAPI.__table__.c:
                        return Log.bad_request(f'La columna {key} no existe en la tabla de logs')
                    filters.append(getattr(LogAPI, key) == value)
            
            logs = session.query(LogAPI).filter(*filters).limit(limit).offset(offset).all()
            if logs == []:
                return Log.not_found()
            return cls.create_response(logs)
        except KeyError as e:
            return Log.bad_request('No se encontró el parámetro en la ruta')
        except ValueError as e:
            traceback.print_exc()
            return Log.bad_request(e.__str__())
        except Exception as e:
            traceback.print_exc()
            raise e(f'Error en la consulta de logs: {e}')
        finally:
            session.invalidate()
            session.close()
    
    @staticmethod
    def create_response(logs):
        """
        Create a response for the log
        :param log: Log to create response
        :return: Response for the log
        """
        response = []
        for log in logs:
            request_headers = loads(log.HEADERS) if log.HEADERS else {}
            request_body = loads(log.BODY) if log.BODY else {}
            
            response_headers = loads(log.HEADERS_RESPONSE) if log.HEADERS_RESPONSE else {}
            body = loads(
                log.BODY_RESPONSE) if log.BODY_RESPONSE else {}
            response.append({
                'id': log.ID,
                'username': log.USERNAME,
                'path': log.PATH,
                'domain': log.DOMAIN_NAME,
                'method': log.METHOD,
                'status_code': log.STATUS_CODE,
                'request': {
                    'headers': request_headers,
                    'body': request_body
                },
                'response': {
                    'headers': response_headers,
                    'body': body,
                },
                'api_date': log.TIME,
                'created_at': datetime.strftime(log.CREATED_AT, '%Y-%m-%d %H:%M:%S'),
                'updated_at': datetime.strftime(log.UPDATED_AT, '%Y-%m-%d %H:%M:%S') if log.UPDATED_AT else None,
                'time': (log.UPDATED_AT - log.CREATED_AT).total_seconds() if log.UPDATED_AT else None
            })
        return response