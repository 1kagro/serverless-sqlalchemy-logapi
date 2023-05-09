from Class.Log import Log

def log(event, context):
    try:
        query_str = event.get("queryStringParameters", None)
        
        response = Log.filter(query_str)
    except Exception as e:
        print(f'Error en la consulta de logs: {e}')
        response = Log.internal_server_error()

    return response
