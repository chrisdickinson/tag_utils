from django.conf.urls.defaults import patterns, include, handler500
from django.conf import settings
from django.contrib import admin
admin.autodiscover()

handler500 # Pyflakes

class test_var(object):
    val = 3 
    val_s = "internal string"

test_context = {
    'xxx':test_var(),
    'xxx_i':3,
    'xxx_s':'string',
}

urlpatterns = patterns(
    '',
    (r'^admin/(.*)', admin.site.root),
    (r'^accounts/login/$', 'django.contrib.auth.views.login'),
    (r'^', 'django.views.generic.simple.direct_to_template', {'template':'test.html', 'extra_context':test_context}),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve',
         {'document_root': settings.MEDIA_ROOT}),
    )
