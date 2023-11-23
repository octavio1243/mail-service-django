import os
import django
import pika
import json
from jinja2 import Environment, Template
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import multiprocessing

# Configura Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mail_notifications.settings")
django.setup()

from decouple import config
from app.api.tools.token import delete_token_permissions,get_user_id
from app.models import Template, Mail
from app.api.serializers import CreateMailSerializer
from django.core.cache import cache
from rest_framework import serializers

# ---> Consumidor de Auth <---

def expire_tokens():
    connection_params = pika.ConnectionParameters(config('rabbit_url'))
    connection = pika.BlockingConnection(connection_params)
    channel = connection.channel()

    # Declara el exchange
    channel.exchange_declare(exchange='auth', exchange_type='fanout')

    # Crea una cola temporal y obtén su nombre
    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue

    # Hace la conexión entre la cola y el exchange usando la clave de enrutamiento (routing key)
    channel.queue_bind(exchange='auth', queue=queue_name, routing_key=queue_name)

    # Función de callback para procesar los mensajes recibidos
    def callback(ch, method, properties, body):
        objeto_json = json.loads(body.decode('utf-8'))
        #print(objeto_json)
        if objeto_json["type"] == "logout":
            user_id = get_user_id(objeto_json["message"])
            delete_token_permissions(user_id)
            print(f" [Auth Process] Usuario {user_id} desautenticado... ")

    # Consume mensajes de la cola
    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

    print(' [Auth Process] Esperando mensajes. Presiona CTRL+C para salir.')
    channel.start_consuming()

# ---> Consumidor/Productor de Mails <---

def send_mail(data, is_html):

    # Configuración de las credenciales de Mailtrap
    mailtrap_username = '4c0017d30276da'
    mailtrap_password = 'edbb26d174bd9b'
    mailtrap_host = 'sandbox.smtp.mailtrap.io'
    mailtrap_port = 587

    # Configurar los detalles del mensaje
    msg = MIMEMultipart()
    msg['From'] = data["email_from"]
    msg['To'] = data["email_to"]
    msg['Subject'] = data["subject"]

    if is_html:
        contenido = MIMEText(data["body"], 'html')
    else:
        contenido = MIMEText(data["body"], 'plain')

    msg.attach(contenido)

    with smtplib.SMTP(mailtrap_host, mailtrap_port) as server:
        server.login(mailtrap_username, mailtrap_password)
        server.sendmail(data["email_from"], data["email_to"], msg.as_string())

    print(f' [Mail Process] Correo electrónico enviado a {data["email_to"]}.')

def reply_service(message,routing_key):
    connection = pika.BlockingConnection(pika.ConnectionParameters(config('rabbit_url')))
    channel = connection.channel()
    channel.exchange_declare(exchange='mail-sent', exchange_type='topic')
    channel.basic_publish(exchange='mail-sent', routing_key=routing_key, body=f"{message}")
    print(f' [Mail Process] Enviando confirmación a {routing_key}.')
    connection.close()

def email_processor():
    
    def format_serializer_errors(errors):
        formatted_errors = {}
        for key, value in errors.items():
            formatted_errors[key] = [str(error) for error in value]
        return formatted_errors

    def get_value(message, name):
        value = message.get(name,None)
        return value

    # Función de callback para procesar los mensajes recibidos
    def callback(ch, method, properties, message):
        message = json.loads(message.decode('utf-8'))
        
        template_id = get_value(message,"template_id")
        email_to = get_value(message,"email_to")
        object_json = get_value(message,"object_json")
        reference_id = get_value(message,"reference_id")
        routing_key = get_value(message,"routing_key")

        try:
            template = Template.objects.filter(id=template_id).first()
            if not template:
                raise ValueError({"template":"No fue encontrado"})
            
            env = Environment()
            template_body = env.from_string(template.body)
            template_subject = env.from_string(template.subject)
            body_renderized = template_body.render(body=object_json)
            subject_renderized = template_subject.render(body=object_json)
                
            data = {
                "email_to": email_to,
                "body": body_renderized,
                "subject": subject_renderized,
                "email_from": template.email_from,
                "template":template.id
            }
            mail_serializer = CreateMailSerializer(data=data)
            mail_serializer.is_valid(raise_exception=True)
            send_mail(data, template.is_html)
            mail_serializer.save()
            
            message_response = {
                "sent": True,
                "reference_id":reference_id
            }
        except serializers.ValidationError as e: # No deberia lanzarse nunca pero lo dejo por las dudas
            formatted_errors = format_serializer_errors(e.detail)
            #print("Errores del serializer: ",formatted_errors)
        except ValueError  as ve:
            
            message_response = {
                "sent": False,
                "errors":ve.args[0],
                "reference_id":reference_id
            }
        
        reply_service(message_response,routing_key)

    # Conexión con el servidor RabbitMQ
    connection = pika.BlockingConnection(pika.ConnectionParameters(config('rabbit_url')))
    channel = connection.channel()

    # Declara el exchange
    channel.exchange_declare(exchange='mail-to-send', exchange_type='direct')

    # Declara una cola temporal
    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue
    
    # Bind de la cola al exchange con una clave de enrutamiento específica
    channel.queue_bind(exchange='mail-to-send', queue=queue_name, routing_key="to-send")

    # Configura la función de callback para procesar los mensajes
    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

    print(' [Mail Process] Esperando mensajes. Presiona CTRL+C para salir.')

    # Inicia el consumo de mensajes
    channel.start_consuming()

# ---> Ejecutando procesos <---

def run_rabbit_script():
    proceso_expire_tokens = multiprocessing.Process(target=expire_tokens)
    proceso_email_processor = multiprocessing.Process(target=email_processor)
    
    proceso_expire_tokens.start()
    proceso_email_processor.start()

    #proceso_expire_tokens.join()
    #proceso_email_processor.join()

