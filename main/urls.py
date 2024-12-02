from django.urls import path
from . import views
from .views import CustomLoginView, PostListView, PostDetailView
from .views import PostCreateView, VadaszteruletCreateView, VadaszteruletListView, VadaszteruletDeleteView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns=[
    path("",views.homepage, name=""),
    path("register",views.register, name="register"),
    path("dashboard",views.dashboard, name="dashboard"),
    path("user-logout", views.user_logout, name="user-logout"),
    path("add",views.beiras_create_view, name="add-beiras"),
    path("ajax/load-vad", views.load_vad, name="loadvad"),
    path("profil", views.profilpage, name="profil"),
    path("lekerdezes", views.lekerdezesek, name="lekerdezes"),
    path("krotaliafel", views.krotalia_feltolt, name="krotaliafel"),
    path("krotaliaatadas", views.krotalia_atadas, name="krotaliaatadas"),
    path("vadaszteruletek", views.teruletfoglalas, name="vadaszteruletek"),
    path("foglalas", views.foglalas_create_view, name="foglalas"),
    path('hatosag', views.hatosag_dashboard, name='hatosag'),
    path('foglalasaim', views.foglalasaim, name='foglalasaim'),
    path('foglalas/torles/<int:idopont_id>/', views.foglalas_torlese, name='foglalas_torlese'),
    path('foglalas/beiras/<int:idopont_id>/', views.vadaszat_befejezese, name='idopont_beirasa'),
    path('tarsasag', views.tarsasag_dash, name='tarsasag'),
    path('mylogin/', CustomLoginView.as_view(), name='mylogin'),
    path('post', PostListView.as_view(), name='post_list'),
    path('post/<int:pk>/',PostDetailView.as_view(), name='post_detail'),
    path('post/add/', PostCreateView.as_view(), name='post_add'),
    path('admin_dashboard', views.admin_dashboard, name='admin_dashboard'),
    path('idopont_generator', views.idopont_generator, name='idopont_generator'),
    path('jogosultsagkezeles', views.jog_kezeles, name='jogosultsagkezeles'),
    path('vadasztarsasagok', views.vadasztarsasag_list, name='vadasztarsasag_list'),
    path('vadasztarsasag/<int:vadasztarsasag_id>/assign/', views.assign_vadaszok, name='assign_vadaszok'),
    path('assign_vadasztarsasag', views.assign_vadasztarsasag_view, name='assign_vadasztarsasag'),
    path('vadaszteruletek/',VadaszteruletListView.as_view(), name='vadaszteruletek_list'),
    path('vadaszteruletek/uj/', VadaszteruletCreateView.as_view(), name='vadaszterulet_create'),
    path('vadaszteruletek/<int:pk>/torles/', VadaszteruletDeleteView.as_view(), name='vadaszterulet_delete'),
    path('beirasok/', views.beiras_list_view, name='beiras_list'),
    path('sajat_krotaliak/', views.sajat_krotaliak, name='sajat_krotaliak'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

