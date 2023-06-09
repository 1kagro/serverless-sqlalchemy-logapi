from setuptools import setup
import aws_handler_decorators

setup(name='Log_Api',
      version=aws_handler_decorators.__version__,
      description='Paquete para el manejo de logs de apis aws lambda serverles con sqlalchemy',
      url='https://github.com/1kagro/serverless-sqlalchemy-logapi',
      author='Fabian Lozano',
      author_email='fabianlozano044@gmail.com',
      license='MIT',
      py_modules=['aws_handler_decorators'],
      packages=['Log_Api', 'Log_Api.Models', 'Log_Api.Class', 'Log_Api.Utils'],
      install_requires=['SQLAlchemy', 'pymysql',
                        'jsonschema', 'boto3', 'urllib3'],
      zip_safe=False)
