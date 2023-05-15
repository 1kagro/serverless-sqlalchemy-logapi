from json import dumps
from .Database import Database, IntegrityError
from .LogAPI import LogAPI

def log_resquest_response(api_func):
    def wrapper(*args, **kwargs):
        request = __request(*args, **kwargs)
        response = api_func(*args, **kwargs)
        __response(request, response)
        return response
    return wrapper

def __request(event, context):
    session = Database('dbw').session
    try:
        method, path = event['routeKey'].split(" ")
        raw_query_str = event.get('rawQueryString', None)
        
        headers = event['headers']
        user_agent = headers.get('user-agent', None)
        
        request_context = event['requestContext']
        
        host = headers['host'] if headers.get(
            'host') else request_context['domainName']
        
        # method = request_context['http']['method']
        # path = request_context['http']['path']
        query_str = event.get('queryStringParameters', None)
        path_parameters = event.get('pathParameters', None)
        
        ip = request_context['identity']['sourceIp'] if request_context.get(
            'identity') else request_context['http']['sourceIp']
        
        username = request_context.get('authorizer', {}).get('jwt', {}).get('claims', {}).get('username', None) 
        
        time = request_context.get('time', None)
        body = event.get('body', {})
        cookies = event.get('cookies', None)
        
        log_api = LogAPI(
            USERNAME=username,
            PATH=path,
            DOMAIN_NAME=host,
            METHOD=method,
            HEADERS=dumps(headers) if headers else None,
            BODY=dumps(body) if body else None,
            QUERY_STR_PARAMETERS=dumps(query_str) if query_str else None,
            PATH_PARAMETERS=path_parameters,
            COOKIES=dumps(cookies) if cookies else None,
            RAW_QUERY_STR=raw_query_str if raw_query_str else None,
            REQUEST_CONTEXT=dumps(request_context),
            AWS_CONTEXT=str(context),
            IP=ip,
            USER_AGENT=user_agent,
            TIME=time
        )
        session.add(log_api)
        session.commit()
        return log_api
    except IntegrityError as e:
        session.rollback()
        raise e
    except Exception as e:
        raise e
    finally:
        session.invalidate()
        session.close()


def __response(request, response):
    """
    Log response
    request: SQLAlchemy object
        Object of the request to log
    response: dict
        Response of the API
    """
    print(response)
    session = Database('dbw').session
    try:
        if response:
            log_api = session.merge(request)
            log_api.STATUS_CODE = response.get('statusCode')
            log_api.HEADERS_RESPONSE = dumps(response.get('headers', None))
            log_api.BODY_RESPONSE = dumps(response.get('body', None))
            session.commit()
    except IntegrityError as e:
        session.rollback()
        raise e
    except Exception as e:
        raise e
    finally:
        session.invalidate()
        session.close()