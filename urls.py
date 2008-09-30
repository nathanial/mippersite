from django.conf.urls.defaults import *
from django.contrib import admin

urlpatterns = patterns('',
                       (r'^$', 'mips.views.index'),
                       (r'^programs/$', 'mips.views.programs'),
                       (r'^programs/(?P<name>[^/]+)/$', 'mips.views.details'),
                       (r'^update/$', 'mips.views.update'),
                       (r'^run/(?P<name>[^/]+)/$', 'mips.views.run'),
                       (r'^reset/$', 'mips.views.reset'),
                       (r'^add/$', 'mips.views.add'),
                       (r'^del/$', 'mips.views.delete'),
                       (r'^login/$', 'mips.views.login'),
                       (r'^logout/$', 'mips.views.logout'),
                       )


