from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^test/', 'api.views.test', name='test'),
    url(r'^login/', 'api.views.login', name='login'),
)