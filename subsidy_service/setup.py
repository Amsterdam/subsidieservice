from setuptools import setup, find_packages

setup(name='subsidy_service',
      version='0.1',
      description='Service for database and bank API interaction',
      packages=find_packages(),
      install_requires=[
          'bunq_sdk',
          'pymongo',
          'connexion',
          'passlib',
      ],
      python_requires='>=3.6')
