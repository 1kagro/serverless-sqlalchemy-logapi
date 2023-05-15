import json

# Clase encargada de dar la respuesta aws
class Response:

    @classmethod
    def aws(cls, data: dict):

        data['data'] = data.get('data', [])
        data['error'] = data.get('error', False)

        return {
            "statusCode": data['statusCode'],
            "headers": {
                'Content-Type': 'application/json'
            },
            "body": json.dumps(data)
        }

    @classmethod
    def error(cls,  message: str = 'Error del cliente'):
        data = {
            'statusCode': 400,
            'error': True,
            'data': [],
            'message': message,
        }
        return cls.aws(data)

    @classmethod
    def success(cls, data: list = [], message: str = 'Petición exitosa'):
        response = {
            'statusCode': 200,
            'data': data,
            'message': message
        }
        return cls.aws(response)

    @classmethod
    def success_create(cls, data: list = [], message: str = 'Petición exitosa'):
        response = {
            'statusCode': 201,
            'data': data,
            'message': message
        }
        return cls.aws(response)

    @classmethod
    def not_found(cls, message: str = 'Recurso no encontrado'):
        data = {
            'statusCode': 404,
            'error': True,
            'data': [],
            'message': message,
        }
        return cls.aws(data)

    @classmethod
    def internal_server_error(cls):
        data = {
            'statusCode': 500,
            'error': True,
            'data': [],
            'message': 'Error interno del servidor',
        }
        return cls.aws(data)

    @classmethod
    def bad_request(cls, message: str = 'Error en la petición'):
        data = {
            'statusCode': 400,
            'error': True,
            'data': [],
            'message': message,
        }
        return cls.aws(data)

    @classmethod
    def unauthorized(cls, data: dict):
        data = {
            'statusCode': 401,
            'error': True,
            'data': [],
            'message': 'No autorizado',
        }
        return cls.aws(data)

    @classmethod
    def forbidden(cls, data: dict):
        data['statusCode'] = 403
        data['error'] = True
        data['data'] = []
        return cls.aws(data)

    @classmethod
    def conflict(cls, data: dict):
        data['statusCode'] = 409
        data['error'] = True
        data['message'] = 'Conflict'
        data['data'] = []
        return cls.aws(data)

    @classmethod
    def method_not_allowed(cls):
        data = {
            'statusCode': 405,
            'error': True,
            'data': [],
            'message': 'Metodo no permitido',
        }
        return cls.aws(data)

    @classmethod
    def not_acceptable(cls, data: dict):
        data['statusCode'] = 406
        data['error'] = True
        data['message'] = 'Not acceptable'
        data['data'] = []
        return cls.aws(data)

    @classmethod
    def unsupported_media_type(cls, data: dict):
        data['statusCode'] = 415
        data['error'] = True
        data['message'] = 'Unsupported Media Type'
        data['data'] = []
        return cls.aws(data)

    @classmethod
    def too_many_requests(cls, data: dict):
        data['statusCode'] = 429
        data['error'] = True
        data['message'] = 'Demasiadas solicitudes'
        data['data'] = []
        return cls.aws(data)

    @classmethod
    def service_unavailable(cls, data: dict):
        data['statusCode'] = 503
        data['error'] = True
        data['message'] = 'Servicio no disponible'
        data['data'] = []
        return cls.aws(data)

    @classmethod
    def gateway_timeout(cls, data: dict):
        data['statusCode'] = 504
        data['error'] = True
        data['message'] = 'Tiempo de espera agotado'
        data['data'] = []
        return cls.aws(data)
