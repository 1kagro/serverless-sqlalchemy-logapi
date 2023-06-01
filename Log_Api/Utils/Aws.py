import os
import json
import boto3
import base64
import logging
from datetime import datetime
from botocore.exceptions import NoCredentialsError
from botocore.exceptions import ClientError

class Aws:

    def __init__(self, secret_name: str):
        self.__secret_name = secret_name
    
    def get_secret(self):
        """
        Obtener secreto
        param: str
            name llave del nombre del secreto a obtener
        """
        stage = os.getenv('STAGE')

        secret_name = f'{stage}/{self.__secret_name}'

        client = self.get_client('secretsmanager')

        try:
            secret_request = client.get_secret_value(
                SecretId=secret_name
            )
        except client.exceptions.ResourceNotFoundException as e:
            raise ValueError(f"No se encontró el secreto {e}")
        except client.exceptions.InvalidParameterException as e:
            raise ValueError(f"InvalidParameterException {e}")
        except client.exceptions.InvalidRequestException as e:
            raise ValueError(f"InvalidRequestException {e}")
        except client.exceptions.DecryptionFailure as e:
            raise ValueError(f"DecryptionFailure {e}")
        except client.exceptions.InternalServiceError as e:
            raise ValueError(f"InternalServiceError {e}")
        except Exception as e:
            raise ValueError(f"Error en el secreto {e}")

        if 'SecretString' in secret_request:
            secret = secret_request['SecretString']
        else:
            secret = base64.b64decode(secret_request['SecretBinary'])

        return json.loads(secret)

    @classmethod
    def get_client(cls, service_name: str, credentials: dict = {}):
        """
        Obtener cliente de aws
        param: service_name
            nombre del servicio
        param: credentials
            credenciales de aws (opcional)
                access_key (str): 
                    access key de aws
                secret_acces_key (str): 
                    secret access key de aws
        return: client
            cliente de aws
        """
        session = boto3.session.Session()
        
        client = session.client(
            service_name=service_name,
            region_name=os.getenv('REGION'),
            aws_access_key_id=credentials.get('accessKey', None),
            aws_secret_access_key=credentials.get('secretKey', None),
        )

        return client

    @classmethod
    def lambdaInvoke(cls, function_name: str, data: dict, inv_type: str = 'RequestResponse') -> dict:
        """
            Invocar lambda
        Args:
            function_name (str): Nombre de la función lambda
            data (dict): Datos a enviar a la función lambda
            inv_type (str): Tipo de invocación de la función lambda
        
        Returns:
            response (dict): Respuesta de la función lambda
        """
        # if inv_type == 'RequestResponse':
        #     data = {'body': json.dumps(data)}
        data = {'body': json.dumps(data)}
        data = json.dumps(data)
        client = cls.get_client('lambda')
        response = client.invoke(
            FunctionName=function_name,
            Payload=data,
            LogType='Tail',
            InvocationType=inv_type
        )

        if inv_type == 'RequestResponse':
            response = cls.get_data_from_response(response)
        return response

    @classmethod
    def get_data_from_response(cls, response):
        """
        Obtener datos de la respuesta de la función lambda
        :param: response
            respuesta de la función lambda
        :return: data
        """
        response_document = response['Payload'].read().decode('utf-8')
        response_document = json.loads(response_document)
        response_body = json.loads(response_document['body'])

        return response_body
    
    @classmethod
    def function_name(cls, function: str, service: str='', stage=os.getenv('STAGE'), ext_app=False):
        """
        Crea nombre de función lambda
        :param: function
            nombre de la función
        :param: stage
            nombre del stage
        :param: ext_app
            si es una aplicación externa
        :return: function_name
        """
        if ext_app == False:
            service = os.getenv('SERVICE', '')
        
        if service == '':
            raise Exception("No se ha definido el nombre del servicio en la variable de entorno SERVICE")
        return f"{service}-{stage}-{function}"
    
    def put_in_s3(self, file_name: str, file_path: str):
        """
        Subir archivo a S3
        :param: file_name
            nombre del archivo, debe tener esta estructura:
                carpeta/nombre_archivo.extension
        :param: file_path
            ruta del archivo a subir
        :return: s3_path_file
        """
        
        # Get S3 info
        secrets = self.get_secret()

        # S3 Bucket Name
        bucket_name = secrets["bucket_name"]


        s3_client = boto3.client('s3')

        try:
            s3_client.upload_file(file_path, bucket_name, file_name)
        except FileNotFoundError:
            raise ValueError("Error al guardar el archivo")
        except NoCredentialsError:
            raise ValueError("Credenciales invalidas")
        except Exception as e:
            raise e
    
    def delete_s3_file(self, file_path: str):
        """
        Eliminar archivo de S3
        :param: file_path
            ruta del archivo, debe tener esta estructura:
                carpeta/nombre_archivo.extension
        """
        # Get S3 info
        secrets = self.get_secret()

        # S3 Bucket Name
        bucket_name = secrets["bucket_name"]
        
        # Put object to bucket
        s3_client = boto3.client('s3')

        try:
            s3_client.delete_object(Bucket=bucket_name, Key=file_path)
        except FileNotFoundError:
            raise ValueError("Error al eliminar el archivo")
        except NoCredentialsError:
            raise ValueError("Credenciales invalidas")
        except Exception as e:
            raise e
    
    def upload_fileobj(self, file_route, filename):
        """
        Subir archivo a S3
        :param: file 
            archivo a subir (BufferedReader)
        :param: filename
            nombre del archivo, debe tener esta estructura:
                carpeta/nombre_archivo.extension
        """
        try:
            filename = f"{datetime.now().strftime('%d-%m-%Y')}_{filename}"
            secrets = self.get_secret()

            bucket_name = secrets["bucket_name"]

            s3_client = boto3.client('s3')
            with open(file_route, 'rb') as file:
                s3_client.upload_fileobj(file, bucket_name, filename)
        except FileNotFoundError:
            raise ValueError("Error al guardar el archivo")
        except NoCredentialsError:
            raise ValueError("Credenciales invalidas")
        except Exception as e:
            raise e
    
    @classmethod
    def get_object(cls, bucket_name: str, object_name: str):
        """Get an object from an S3 bucket

        :param bucket_name: string
        :param object_name: string
        :return: Boto3 S3 object. If error, returns None.
        """

        # Generate a presigned URL for the S3 object
        s3_client = boto3.client('s3')
        try:
            s3_object = s3_client.get_object(Bucket=bucket_name, Key=object_name)
            response = s3_object['Body'].read()
        except ClientError as e:
            logging.error(e)
            return None
        return response

    def create_presigned_url(self, object_name, expiration=7257600):
        """Generate a presigned URL to share an S3 object

        :param bucket_name: string
        :param object_name: string
        :param expiration: Time in seconds for the presigned URL to remain valid
        :return: Presigned URL as string. If error, returns None.
        """
        # Get S3 info
        secrets = self.get_secret()

        # S3 Bucket Name
        bucket_name = secrets["bucket_name"]
        
        # Generate a presigned URL for the S3 object
        s3_client = boto3.client('s3')
        try:
            file_valid = True
            try:
                s3_client.head_object(Bucket=bucket_name, Key=object_name)
            except:
                # raise ValueError("El archivo especificado no existe")
                file_valid = False
            
            if file_valid:
                response = s3_client.generate_presigned_url(
                    'get_object',
                    Params={
                        'Bucket': bucket_name,
                        'Key': object_name},
                    ExpiresIn=expiration)
            else:
                response = None
            
        except ClientError as e:
            logging.error(e)
            return None

        # The response contains the presigned URL
        return response
