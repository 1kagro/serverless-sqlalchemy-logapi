import logging
import ast
import boto3
from json import load, loads, dumps
from functools import wraps, update_wrapper

try:
    import asyncio
except ImportError:
    pass

try:
    from jsonschema import ValidationError, validate
except ImportError:
    jsonschema = None

try:
    from urllib.parse import parse_qs
except ImportError:
    from urlparse import parse_qs

try:
    basestring
except NameError:
    basestring = str

logger = logging.getLogger(__name__)

__version__ = '0.0.7'

class AwsHandlerDecorator(object):
    def __init__(self, func):
        update_wrapper(self, func)
        self.func = func

    def __call__(self, event, context):
        try:
            return self.after(self.func(*self.before(event, context)))
        except Exception as exception:
            return self.on_exception(exception)
        
    def before(self, event, context):
        return event, context
    
    def after(self, result):
        return result
    
    def on_exception(self, exception):
        return exception

def before(func):
    """
    Run a function before the handler is called, it will be called with 
    the event and context as parameters
    """
    class BeforeDecorator(AwsHandlerDecorator):
        def before(self, event, context):
            return func(event, context)
    return BeforeDecorator


def after(func):
    """
    Run a function after the handler is called, it will be called with
    the response returned by the handler as a parameter
    """
    class AfterDecorator(AwsHandlerDecorator):
        def after(self, result):
            return func(result)
    return AfterDecorator

def on_exception(func):
    """
    Run a function when an exception is raised in the handler, 
    it will be called with the exception raised as a parameter
    """
    class OnExceptionDecorator(AwsHandlerDecorator):
        def on_exception(self, exception):
            return func(exception)
    return OnExceptionDecorator

def async_handler(handler):
    """
    Decorator to run a handler asynchronously, it will return a function
    that can be used as an AWS Lambda handler and will call the original
    handler asynchronously
    """
    @wraps(handler)
    def wrapper(event, context):
        try:
            context.loop = asyncio.get_event_loop()
        except RuntimeError:
            context.loop = asyncio.new_event_loop()
            # asyncio.set_event_loop(context.loop)
        return context.loop.run_until_complete(handler(event, context))
    return wrapper
    # def async_handler(event, context):
    #     boto3.client('lambda').invoke(
    #         FunctionName=context.function_name,
    #         InvocationType='Event',
    #         Payload=dumps({'event': event, 'context': context})
    #     )
    
def cors_headers(handler_or_origin=None, origin=None, credentials=False):
    """
    Decorator to add CORS headers to the response. 
    It will add the Access-Control-Allow-Origin header with the value
    of the `origin` parameter. If the `credentials` parameter is True, it will also add the
    Access-Control-Allow-Credentials header with the value of the `credentials` parameter.
    """
    if isinstance(handler_or_origin, str) and origin is not None:
        raise TypeError('cors_headers() takes either a handler or origin, not both')
    if isinstance(handler_or_origin, str) or origin is not None:
        def wrapper_wrapper(handler):
            @wraps(handler)
            def wrapper(event, context):
                response = handler(event, context)
                if response is None:
                    response = {}
                headers = response.setdefault('headers', {})
                if origin is not None:
                    headers['Access-Control-Allow-Origin'] = origin
                else:
                    headers['Access-Control-Allow-Origin'] = handler_or_origin
                if credentials:
                    headers['Access-Control-Allow-Credentials'] = True
                return response
            return wrapper
        return wrapper_wrapper
    elif handler_or_origin is None:
        return cors_headers("*", credentials=credentials)
    else:
        return cors_headers("*")(handler_or_origin)

def dump_json_body(handler=None, **kwargs):
    """
    Decorator to dump the body of the request as JSON. 
    It will add the body as a `body_json` parameter to the handler.
    """
    if handler is not None and len(kwargs) > 0:
        raise TypeError('dump_json_body() takes either a handler or kwargs, not both')
    
    if handler is None:
        def wrapper_wrapper(handler):
            @wraps(handler)
            def wrapper(event, context):
                try:
                    response = handler(event, context)
                    if response and "body" in response:
                        response["body"] = dumps(response["body"], **kwargs)
                    return response
                except Exception as exception:
                    if hasattr(context, "serverless_sdk"):
                        context.serverless_sdk.capture_exception(exception)
                    raise exception
            return wrapper
        return wrapper_wrapper
    else:
        return dump_json_body()(handler)

def json_http_response(handler=None, **kwargs):
    """
    Decorator to dump the body of the request as JSON.
    It will add the body as a `body_json` parameter to the handler.
    """
    if handler is not None and len(kwargs) > 0:
        raise TypeError('json_http_response() takes either a handler or kwargs, not both')
    if handler is None:
        def wrapper_wrapper(handler):
            @wraps(handler)
            def wrapper(event, context):
                try:
                    response = handler(event, context)
                    if isinstance(response, dict):
                        status_code = response.pop("statusCode", 200)
                        headers = response.pop("headers", None)
                    else:
                        headers = None
                        status_code = 200
                    
                    http_response = {
                        "statusCode": status_code,
                        "body": dumps(response, **kwargs),
                    }
                    if headers:
                        http_response["headers"] = headers
                    return http_response
                except Exception as exception:
                    if hasattr(context, "serverless_sdk"):
                        context.serverless_sdk.capture_exception(exception)
                    return {"statusCode": 500, "body": str(exception)}
            return wrapper
        return wrapper_wrapper
    else:
        return json_http_response()(handler)

def loads_json_body(handler=None, **kwargs):
    """
    Decorator to load the body of the request as JSON.
    returns a bad request response if the body is not valid JSON
    """
    if handler is not None and len(kwargs) > 0:
        raise TypeError('loads_json_body() takes either a handler or kwargs, not both')
    if handler is None:
        def wrapper_wrapper(handler):
            @wraps(handler)
            def wrapper(event, context):
                if isinstance(event.get("body"), str):
                    try:
                        event["body"] = loads(event["body"], **kwargs)
                    except Exception as exception:
                        if hasattr(context, "serverless_sdk"):
                            context.serverless_sdk.capture_exception(exception)
                        return {"statusCode": 400, "body": "bad request"}
                else:
                    event["body"] = {}
                return handler(event, context)
            return wrapper
        return wrapper_wrapper
    else:
        return loads_json_body()(handler)

def load_json_queryStringParameters(handler):
    """
    Decorator to load the event queryStringParameters of the request as JSON.
    returns a bad request response if the queryStringParameters is not valid JSON
    """
    @wraps(handler)
    def wrapper(event, context):
        isObject = lambda x: type(x) in [dict, list, tuple]

        def evaluate_items(obj):
            def seq(obj):
                if isinstance(obj, dict):
                    keys = obj.keys()
                    return zip([key for key in keys], [obj[key] for key in keys])
                else:
                    return enumerate(obj)

            tuple_flag = isinstance(obj, tuple)
            obj = list(obj) if tuple_flag else obj
            for i, value in seq(obj):
                try:
                    obj[i] = ast.literal_eval(value)
                except ValueError as e:
                    pass
                if isObject(obj[i]):
                    obj[i] = evaluate_items(obj[i])
            obj = tuple(obj) if tuple_flag else obj
            return obj
        
        if isinstance(event.get("queryStringParameters"), str):
            try:
                event["queryStringParameters"] = ast.literal_eval(event["queryStringParameters"])
                if isObject(event["queryStringParameters"]):
                    event["queryStringParameters"] = evaluate_items(event["queryStringParameters"])
            except Exception as exception:
                return {"statusCode": 400, "body": str(exception)}
        elif isinstance(event.get("queryStringParameters"), dict) and event.get("body") in [None, {}]:
            event["body"] = event.get("queryStringParameters", {})
        return handler(event, context)
    return wrapper

def json_schema_validator(request_schema=None, document=None, body=True, in_file=False):
    """
    Decorator to validate the request for a API Gateway event.
    Validate the request against the schema passed as `request_schema` parameter
    """
    def wrapper_wrapper(handler):
        @wraps(handler)
        def wrapper(event, context):
            def validate_request_schema(request_data):
                if request_schema is not None:
                    try:
                        with open(request_schema) as lfile:
                            schema_data = load(lfile)
                            if document is None:
                                document_name = handler.__name__
                            else:
                                document_name = document
                            if in_file == False:
                                schema_data = schema_data[document_name]
                            validate(request_data, schema_data)
                    except ValidationError as ex:
                        error_path = ".".join(str(path) for path in ex.path)
                        error_message = f"Validation error at field '{error_path}': {ex.message}"
                        logging.error(error_message)
                        return {
                            "statusCode": 400,
                            "body": error_message
                        }
            # if 'jsonschema' not in globals():
            #     logger.error("jsonschema is not installed")
            #     raise Exception("jsonschema is not installed")
            
            if body:
                result = validate_request_schema(event["body"])
                if result is not None:
                    return result
            return handler(event, context)
        return wrapper
    return wrapper_wrapper

def load_urlencoded_body(handler):
    """
    Decorator to load the body of the request as urlencoded, 
    deserialize application/x-www-form-urlencoded bodies
    """
    @wraps(handler)
    def wrapper(event, context):
        if isinstance(event.get("body"), str):
            try:
                event["body"] = parse_qs(event["body"])
            except Exception as exception:
                if hasattr(context, "serverless_sdk"):
                    context.serverless_sdk.capture_exception(exception)
                return {"statusCode": 400, "body": "bad request"}
        return handler(event, context)
    return wrapper


def no_retry_on_failure(handler):
    """
    Decorator to disable retry on failure
    """
    seen_request_ids = set()
    
    @wraps(handler)
    def wrapper(event, context):
        if context.aws_request_id in seen_request_ids:
            logger.critical(
                "Request ID has already been seen, this is a retry. ", context.aws_request_id
            )
            return {"statusCode": 200}
        seen_request_ids.add(context.aws_request_id)
        return handler(event, context)
    return wrapper


def ssm_parameter_store(*parameters):
    """
    Decorator to load parameters from AWS SSM Parameter Store
    """
    
    if len(parameters) == 1 and not isinstance(parameters[0], basestring):
        parameters = parameters[0]

    def wrapper_wrapper(handler):
        @wraps(handler)
        def wrapper(event, context):
            ssm = boto3.client("ssm")
            if not hasattr(context, "parameters"):
                context.parameters = {}
            for parameter in ssm.get_parameters(Names=parameters, WithDecryption=True)["Parameters"]:
                context.parameters[parameter["Name"]] = parameter["Value"]

            return handler(event, context)

        return wrapper

    return wrapper_wrapper


def secrets_manager(*secret_names):
    """
    Decorator to load secrets from AWS Secrets Manager
    """
    def wrapper_wrapper(handler):
        @wraps(handler)
        def wrapper(event, context):
            if not hasattr(context, "secrets"):
                context.secrets = {}
            for secret_name in secret_names:
                secret_value = boto3.client(
                    service_name="secretsmanager"
                ).get_secret_value(SecretId=secret_name)
                if "SecretString" in secret_value:
                    context.secrets[secret_name] = loads(
                        secret_value["SecretString"]
                    )
                else:
                    context.secrets[secret_name] = secret_value["SecretBinary"]

            return handler(event, context)

        return wrapper

    return wrapper_wrapper


def secret_manager(secret_name):
    """
    Get a single secret from AWS Secrets Manager
    """
    return secrets_manager(secret_name)
