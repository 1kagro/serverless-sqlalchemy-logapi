from setuptools import setup

setup(name='Log_Api',
      version='0.1',
      description='Paquete para el manejo de logs de apis aws lambda serverles con sqlalchemy',
      url='https://github.com/1kagro/serverless-sqlalchemy-logapi',
      author='Fabian Lozano',
      author_email='fabianlozano044@gmail.com',
      license='MIT',
      packages=['Log_Api', 'Log_Api.Models', 'Log_Api.Class'],
      install_requires=['SQLAlchemy'],
      zip_safe=False)
