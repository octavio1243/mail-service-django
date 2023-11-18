from rest_framework import serializers
from app.models import Template, Mail

class CreateTemplateSerializer(serializers.ModelSerializer):
    
    class Meta(object):
        model = Template
        exclude = ['id']

class ShowTemplateSerializer(serializers.ModelSerializer):
    
    class Meta(object):
        model = Template
        fields = '__all__'

class UpdateTemplateSerializer(serializers.ModelSerializer):
    
    class Meta(object):
        model = Template
        exclude = ['id','name']

class ShowMailSerilizer(serializers.ModelSerializer):

    class Meta(object):
        model = Mail
        fields = '__all__'

class CreateMailSerializer(serializers.ModelSerializer):
    
    class Meta(object):
        model = Mail
        exclude = ['id']