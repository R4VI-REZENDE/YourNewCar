from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from . import views
from .forms import LoginForm

urlpatterns = [
    # Carros
    path("", views.CarListView.as_view(), name="car_list"),
    path("<int:pk>/", views.CarDetailView.as_view(), name="car_detail"),
    path("novo/", views.CarCreateView.as_view(), name="car_create"),
    path("<int:pk>/editar/", views.CarUpdateView.as_view(), name="car_update"),
    path("<int:pk>/excluir/", views.CarDeleteView.as_view(), name="car_delete"),
    path("meus-anuncios/", views.MeusAnunciosListView.as_view(), name="meus_anuncios"),

    # Favoritos e mensagens
    path("<int:pk>/favoritar/", views.alternar_favorito, name="car_favoritar"),
    path("<int:pk>/mensagem/", views.enviar_mensagem, name="car_mensagem"),
    path("favoritos/", views.FavoritoListView.as_view(), name="favoritos"),
    path("mensagens/", views.MensagemListView.as_view(), name="mensagens"),

    # Contas
    path(
        "entrar/",
        LoginView.as_view(
            template_name="cars/login.html",
            authentication_form=LoginForm,
            redirect_authenticated_user=True,
        ),
        name="login",
    ),
    path("sair/", LogoutView.as_view(), name="logout"),
    path("cadastrar/", views.RegisterView.as_view(), name="register"),
]
