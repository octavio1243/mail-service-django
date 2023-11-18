from django.db import models

# Create your models here.
class Template(models.Model):
    name = models.CharField('Nombre',max_length=256, unique=True, blank = False, null = False)
    description = models.CharField('Descripción',max_length=256, blank = True, null = True)
    subject = models.CharField('Asunto',max_length=256, blank = False, null = False)
    body = models.CharField('Cuerpo',max_length=4096, blank = False, null = False)
    email_from = models.CharField('Correo origen',max_length=256, blank = False, null = False)
    is_html = models.BooleanField(default = True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Plantilla'
        verbose_name_plural = 'Plantillas'
        ordering = ['id'] # Puedo ordenarlo
    
    def __str__(self):
        return self.name
    
class Mail(models.Model):
    subject = models.CharField('Asunto',max_length=256, blank = False, null = False)
    body = models.CharField('Cuerpo',max_length=4096, blank = False, null = False)
    email_to = models.CharField('Correo destino',max_length=256, blank = False, null = False)
    email_from = models.CharField('Correo origen',max_length=256, blank = False, null = False)
    created_at = models.DateTimeField(auto_now_add=True)

    # Relaciones
    template = models.ForeignKey(Template, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Correo'
        verbose_name_plural = 'Correos'
        ordering = ['id'] # Puedo ordenarlo
    
    def __str__(self):
        return self.name