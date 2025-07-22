"""
MYSQL = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'codigos_db',
        'USER': 'ADMIN',
        'PASSWORD': 'ADMINPALDACA12345',
        'HOST': 'localhost',
        'PORT': '',
    }
}
"""
#Configuración de desarrollo local
MYSQL = {
    'default': {
       'ENGINE': 'django.db.backends.mysql',
       'NAME': 'codigos_db',   # asegúrate de que esta base exista localmente
       'USER': 'root',
       'PASSWORD': 'admin',         # sin contraseña
     'HOST': 'localhost',    # puedes usar localhost o 127.0.0.1
       'PORT': '3306',         # puerto por defecto de MySQL
    }
}

