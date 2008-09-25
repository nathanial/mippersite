from django.conf.urls.defaults import *
from django.contrib import admin

urlpatterns = patterns('',
                       (r'^mips/$', 'gaesite.mips.views.index'),
                       (r'^mips/program/(?P<name>[^/]+)/$', 'gaesite.mips.views.details'),
                       (r'^mips/program/(?P<name>.+)/submit_code/$', 'gaesite.mips.views.submit_code'),
                       (r'^mips/program/[^/]+/update/$', 'gaesite.mips.views.update'),
                       (r'^mips/program/[^/]+/run/$', 'gaesite.mips.views.run'),
                       (r'^mips/add/$', 'gaesite.mips.views.add'),
                       (r'^mips/del/$', 'gaesite.mips.views.delete'),
                       (r'^javascript/(?P<path>.*)$', 'django.views.static.serve', {'document_root':'/Development/Projects/gaesite/static/javascript'}),
                       (r'^styles/(?P<path>.*)$', 'django.views.static.serve', {'document_root':'/Development/Projects/gaesite/static/styles'}),
                       (r'^images/(?P<path>.*)$', 'django.views.static.serve', {'document_root':'/Development/Projects/gaesite/static/images'}))

