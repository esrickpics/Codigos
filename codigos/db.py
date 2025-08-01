
#Configuración de desarrollo local
"""Configuración de la base de datos para el entorno local de desarrollo.
MYSQL = {
   'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'codigos_db',   # asegúrate de que esta base exista localmente
        'USER': 'RAG',
        'PASSWORD': 'RAG12345',         # sin contraseña
        'HOST': '127.0.0.1',    # puedes usar localhost o 127.0.0.1
        'PORT': '3306',         # puerto por defecto de MySQL
    }
}
"""
#Configuración de producción
MYSQL = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'ssapmcco_codigos_db',
        'USER': 'ssapmcco_ADMIN',
        'PASSWORD': 'ADMINPALDACA12345',
        'HOST': 'localhost',
        'PORT': '',
    }
}
