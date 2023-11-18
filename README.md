# Microservicio Mail Service 

```
# Instalar modulo para entorno virtual
pip install virtualenv

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
venv\Scripts\activate

# Instalar modulos del proyecto
pip install -r requirements.txt

# Crea las migraciones partiendo desde los modelos
python manage.py makemigrations

# Correr migraciones
python manage.py migrate

# Ejecutar proyecto
python manage.py runserver

# Levantar proceso demonio del comunicación asincrona
python rabbit_script.py
```
