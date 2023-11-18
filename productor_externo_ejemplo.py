import pika
from decouple import config
import json
import random

def enviar_mail(template_id, routing_key):
  
  # Conexión con el servidor RabbitMQ
  connection = pika.BlockingConnection(pika.ConnectionParameters(config('rabbit_url')))
  channel = connection.channel()

  # Declara el exchange
  channel.exchange_declare(exchange='mail-to-send', exchange_type='direct')

  # Mensaje a enviar
  object_json = {
    "compra": {
      "id": "ABC123",
      "fecha": "2023-01-15",
      "total": 150.75,
      "productos": [
        {"id": 1, "nombre": "Producto A", "precio": 50.25, "cantidad": 2},
        {"id": 2, "nombre": "Producto B", "precio": 25.50, "cantidad": 1}
      ],
      "cliente": {
        "nombre": "Juan Pérez",
        "email": "juan@example.com",
        "telefono": "123-456-7890"
      },
      "direccion_entrega": {
        "calle": "Calle Principal",
        "numero": "123",
        "ciudad": "Ciudad Ejemplo",
        "codigo_postal": "12345",
        "pais": "EjemploLand"
      }
    }
  }

  message = {
      "template_id": template_id,
      "email_to": "example@email.com",
      "object_json": object_json,
      "reference_id": random.randint(1, 1000),
      "routing_key":"ordenes"
  }

  # Envia el mensaje al exchange con una clave de enrutamiento específica
  channel.basic_publish(exchange='mail-to-send', routing_key='to-send', body=json.dumps(message))

  print(f" [x] Enviado '{message}'")

  # Cierra la conexión
  connection.close()

template_id=1
routing_key="ordenes"
enviar_mail(template_id, routing_key)
