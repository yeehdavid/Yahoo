from django.conf.urls import url
from . import views

app_name = 'main'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^create', views.create, name='create'),
    url(r'^uploadFile', views.upload, name='upload'),
    url(r'^download/$', views.download, name='download')
    # url(r'^tea/(?P<pk>[0-9]+)/$', views.detail, name='detail'),
]
