from django.conf.urls.defaults import patterns, include, url
import views

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',('^$', views.home),('^new$', views.note_write),('^note_edit_auth$', views.note_edit_auth), ('^edit$', views.edit_conf),('^note_edit$', views.note_edit), ('^note_read_auth$', views.note_read_auth),# ('^note_read$', views.note_read),
    # Examples:
    # url(r'^$', 'deathnote.views.home', name='home'),
    # url(r'^deathnote/', include('deathnote.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
