# It makes it easier to create a REST API with Python and AWS serverless.

Included Decorators:
--------------------
``lambda_decorators`` includes the following decorators to avoid boilerplate
for common usecases when using AWS Lambda with Python.

* `async_handler` - support for async handlers
* `cors_headers` - automatic injection of CORS headers
* `dump_json_body` - auto-serialization of http body to JSON
* `load_json_body` - auto-deserialize of http body from JSON
* `json_http_resp` - automatic serialization of python object to HTTP JSON response
* `json_schema_validator` - use JSONSchema to validate request&response payloads
* `load_urlencoded_body` - auto-deserialize of http body from a querystring encoded body
* `no_retry_on_failure` - detect and stop retry attempts for scheduled lambdas
* `ssm_parameter_store` - fetch parameters from the AWS SSM Parameter Store
* `secret_manager` - fetch secrets from the AWS Secrets Manager
* `log_resquest_response` - log request and response

Installation:
-------------
```bash
pip install Log-Api
```

Usage:
------

#### load_json_body
```python
from aws_handler_decorators import load_json_body

@load_json_body
def handler(event, context):
    # event['body'] is now a python object
    return event['body']['foo']

handler({'body': '{"foo": "bar"}'}, object())
```

#### json_schema_validator
You can use to validate the request. The schema is a JSON object or a path to a JSON file.

```python
from aws_handler_decorators import json_schema_validator
@json_schema_validator(request_schema={
    'type': 'object',
    'properties': {
        'foo': {'type': 'string'}
    },
    'required': ['foo']
})
def handler(event, context):
    # event['body'] is now a python object
    return event['body']['foo']

handler({'body': '{"foo": "bar"}'}, object())

@json_schema_validator(request_schema='path/to/schema.json', in_file=True)
def handler(event, context):
    # event['body'] is now a python object
    return event['body']['foo']

handler({'body': '{"foo": "bar"}'}, object())
```

If you don't pass a request schema, it will validate from the name of the function

I was inspired by `dschep <https://github.com/dschep>`_

## Log Api

Prerequisites:
--------------

* Python 3.6+
* A secret for database connection in AWS Secrets Manager
`dbr/stage` (stage is the environment, for example: dev, qa, prod)
`dbw/stage` (stage is the environment, for example: dev, qa, prod)
```json
{
  "username": "user",
  "password": "password",
  "host": "host",
  "port": "port",
  "bd_name": "database"
}
```
```sql
CREATE TABLE `LOG_APIS` (
  `ID` BIGINT NOT NULL AUTO_INCREMENT COMMENT 'Id del registro',
  `USERNAME` VARCHAR(15) DEFAULT NULL COMMENT 'Nombre del usuario que consume el servicio',
  `PATH` VARCHAR(50) NOT NULL COMMENT 'Ruta de la api',
  `DOMAIN_NAME` VARCHAR(200) DEFAULT NULL COMMENT 'Host de la api',
  `METHOD` VARCHAR(10) NOT NULL COMMENT 'Metodo de solicitud',
  `STATUS_CODE` SMALLINT DEFAULT NULL COMMENT 'Codigo de estado de la respuesta',
  `HEADERS_RESPONSE` LONGTEXT COMMENT 'Cabecera de la respuesta',
  `BODY_RESPONSE` LONGTEXT COMMENT 'Payload de la respuesta',
  `HEADERS` LONGTEXT COMMENT 'Cabecera de la solicitud',
  `BODY` LONGTEXT COMMENT 'Payload de la solicitud',
  `QUERY_STR_PARAMETERS` TEXT COMMENT 'Query string parameters',
  `PATH_PARAMETERS` TEXT,
  `COOKIES` TEXT,
  `RAW_QUERY_STR` TEXT,
  `REQUEST_CONTEXT` LONGTEXT,
  `AWS_CONTEXT` TEXT,
  `IP` VARCHAR(15) NOT NULL COMMENT 'Ip del cliente',
  `USER_AGENT` TEXT,
  `TIME` TEXT CHARACTER SET utf8 COLLATE utf8_general_ci COMMENT 'Fecha en la que se ejecuto la api',
  `VERSION` VARCHAR(50) DEFAULT NULL COMMENT 'Version de la respuesta',
  `CREATED_AT` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Fecha de creacion del registro',
  `UPDATED_AT` TIMESTAMP NULL DEFAULT NULL COMMENT 'Fecha en la que se actualizo el registro',
  PRIMARY KEY (`ID`)
) ENGINE=INNODB AUTO_INCREMENT=24 DEFAULT CHARSET=utf8;

```

### Usage
```python
from aws_handler_decorators import (
    async_handler, cors_headers, dump_json_body, json_http_resp, json_schema_validator,
    load_json_body, load_urlencoded_body, no_retry_on_failure, ssm_parameter_store,
    secret_manager, log_resquest_response
)

from Log_Api import log_resquest_response

@log_resquest_response be to used before the other decorators like this:
* `json_schema_validator`
See each individual decorators for specific usage details and the example_
for some more use cases. This library is also meant to serve as an example for how to write
decorators for use as lambda middleware.
```