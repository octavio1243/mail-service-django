from django.urls import path, re_path
from app.api.views import \
    CreateOrIndexTemplateView,\
    ShowOrUpdateOrDeleteTemplateView,\
    MailsView

urlpatterns = [
    path('templates', CreateOrIndexTemplateView.as_view(),name='template_create_index'),
    path('templates/<template_id>', ShowOrUpdateOrDeleteTemplateView.as_view(),name='template_show_update_delete'),
    path('templates/<template_id>/mails', MailsView.as_view(),name='mails')
]