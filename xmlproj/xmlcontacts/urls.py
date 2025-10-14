from django.urls import path
from . import views

urlpatterns = [
    path('', views.contact_form, name='contact_form'),
    path('contacts/', views.contact_list, name='contact_list'),
    path('upload/', views.upload_xml, name='upload_xml'),
    path('files/', views.xml_files_list, name='xml_files_list'),
    path('files/<str:filename>/', views.view_xml_file, name='view_xml_file'),
    path('download/<str:filename>/', views.download_xml_file, name='download_xml_file')
]