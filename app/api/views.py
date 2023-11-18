from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from app.models import Template, Mail
from app.api.tools.user import is_authenticated_and_authorized

from app.api.serializers import \
    CreateTemplateSerializer,\
    ShowTemplateSerializer,\
    ShowMailSerilizer,\
    UpdateTemplateSerializer
    
# Verifica que el usuario esté autenticado y sea administrador
def auth_decorator(method):
    def wrapper(self, *args, **kwargs):
        token = args[0].META.get('HTTP_AUTHORIZATION')
        try:
            if not (is_authenticated_and_authorized(token)):
                return Response({"error":"No está autorizado/autenticado."}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as error:
            print(f"Se produjo un error: {error}")
            return Response({"error":"El token es inválido."}, status=status.HTTP_400_BAD_REQUEST)
        return method(self, *args, **kwargs)
    return wrapper

class CreateOrIndexTemplateView(APIView):
    
    @auth_decorator
    def post(self, request, *args, **kwargs):
        print("Creando un template")
        template_serializer = CreateTemplateSerializer(data=request.data)
        template_serializer.is_valid(raise_exception=True)
        template = template_serializer.save()
        return Response({"template":ShowTemplateSerializer(template).data})

    @auth_decorator
    def get(self, request, *args, **kwargs):
        print("Buscando TODOS los template")
        templates = Template.objects.all()
        templates_serializer = ShowTemplateSerializer(templates, many=True)
        return Response({"templates": templates_serializer.data})
    
class ShowOrUpdateOrDeleteTemplateView(APIView):
    
    @auth_decorator
    def get(self, request, *args, **kwargs):
        print("Buscando un template")
        template = Template.objects.filter(id=kwargs["template_id"]).first()
        if not template:
            return Response({"error": "Template no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        template_serializer = ShowTemplateSerializer(template)
        return Response({"template": template_serializer.data})

    @auth_decorator
    def put(self, request, *args, **kwargs):
        print("Actualizando un template")
        template = Template.objects.filter(id=kwargs["template_id"]).first()
        if not template:
            return Response({"error": "Template no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        template_serializer = UpdateTemplateSerializer(template, data = request.data, partial=True)
        template_serializer.is_valid(raise_exception=True)
        template = template_serializer.save()
        return Response({"template": ShowTemplateSerializer(template).data})
    
    @auth_decorator
    def delete(self, request, *args, **kwargs):
        print("Borrando un template")
        template = Template.objects.filter(id=kwargs["template_id"]).first()
        if not template:
            return Response({"error": "Template no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        template.delete()
        return Response(status=status.HTTP_200_OK)

class MailsView(APIView):
    
    @auth_decorator
    def get(self, request, *args, **kwargs):
        print("Buscando TODOS los mails")
        template = Template.objects.filter(id=kwargs["template_id"]).first()
        if not template:
            return Response({"error": "Template no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        mails = template.mail_set.all()
        mails_serializer = ShowMailSerilizer(mails, many=True)
        return Response({"mails": mails_serializer.data})
    
"""
Por hacer:
- Rabbit tasks con crontab (las 3)
"""