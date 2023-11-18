import pika
from decouple import config

def esperar_respuesta(routing_key):
  
  def callback(ch, method, properties, body):
      print(f" [x] Recibido '{body}' con clave de enrutamiento '{method.routing_key}'")

  connection = pika.BlockingConnection(pika.ConnectionParameters(config('rabbit_url')))
  channel = connection.channel()

  channel.exchange_declare(exchange='mail-sent', exchange_type='topic')
  result = channel.queue_declare(queue='', exclusive=True)
  queue_name = result.method.queue

  channel.queue_bind(exchange='mail-sent', queue=queue_name, routing_key=routing_key)

  print(f" [*] Esperando mensajes con clave de enrutamiento '{routing_key}'. Presiona CTRL+C para salir.")

  channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

  channel.start_consuming()

template_id=1 
routing_key="ordenes"
esperar_respuesta(routing_key)
