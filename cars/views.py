from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, TemplateView, UpdateView,
)

from .forms import CarForm, RegisterForm
from .models import Car, Favorito, Mensagem


# ---------------------------------------------------------------- Carros
class CarListView(ListView):
    """Página inicial: lista os anúncios ativos, com os filtros da sidebar."""
    model = Car
    context_object_name = "cars"

    def get_queryset(self):
        carros = Car.objects.filter(ativo=True).prefetch_related("fotos")
        busca = self.request.GET

        if busca.get("marca"):
            carros = carros.filter(marca=busca["marca"])
        if busca.get("usado") in ("0", "1"):
            carros = carros.filter(usado=busca["usado"] == "1")

        # filtros numéricos: campo do formulário -> filtro do banco
        faixas = {
            "preco_min": "preco__gte",
            "preco_max": "preco__lte",
            "ano_min": "ano__gte",
            "ano_max": "ano__lte",
        }
        for campo, filtro in faixas.items():
            if busca.get(campo, "").isdigit():
                carros = carros.filter(**{filtro: busca[campo]})
        return carros


class CarDetailView(DetailView):
    queryset = Car.objects.select_related("vendedor").prefetch_related("fotos")


class CarCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Car
    form_class = CarForm
    success_message = "Anúncio publicado!"

    def form_valid(self, form):
        form.instance.vendedor = self.request.user  # o dono é quem está logado
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("car_detail", args=[self.object.pk])


class DonoMixin(LoginRequiredMixin):
    """Só enxerga (e portanto só edita/exclui) os próprios anúncios; os outros dão 404."""

    def get_queryset(self):
        return Car.objects.filter(vendedor=self.request.user)


class CarUpdateView(DonoMixin, SuccessMessageMixin, UpdateView):
    form_class = CarForm
    success_message = "Anúncio atualizado."

    def get_success_url(self):
        return reverse("car_detail", args=[self.object.pk])


class CarDeleteView(DonoMixin, SuccessMessageMixin, DeleteView):
    success_url = reverse_lazy("car_list")
    success_message = "Anúncio excluído."


class MeusAnunciosListView(LoginRequiredMixin, ListView):
    template_name = "cars/meus_anuncios.html"
    context_object_name = "cars"

    def get_queryset(self):
        return Car.objects.filter(vendedor=self.request.user).prefetch_related("fotos")


# ------------------------------------------------------------- Favoritos
class FavoritoListView(LoginRequiredMixin, ListView):
    template_name = "cars/favoritos.html"
    context_object_name = "cars"

    def get_queryset(self):
        return Car.objects.filter(
            favoritado_por__usuario=self.request.user
        ).prefetch_related("fotos")


@login_required
@require_POST
def alternar_favorito(request, pk):
    """Favorita o carro; se já era favorito, remove."""
    carro = get_object_or_404(Car, pk=pk)
    favorito, criado = Favorito.objects.get_or_create(usuario=request.user, carro=carro)
    if not criado:
        favorito.delete()
    return redirect(request.META.get("HTTP_REFERER") or "car_list")


# ------------------------------------------------------------- Mensagens
class MensagemListView(LoginRequiredMixin, TemplateView):
    template_name = "cars/mensagens.html"

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        usuario = self.request.user

        recebidas = Mensagem.objects.filter(carro__vendedor=usuario).select_related(
            "carro", "remetente"
        )
        contexto["recebidas"] = list(recebidas)  # lê antes de marcar como lidas
        contexto["enviadas"] = Mensagem.objects.filter(remetente=usuario).select_related(
            "carro", "carro__vendedor"
        )
        recebidas.filter(lida=False).update(lida=True)
        return contexto


@login_required
@require_POST
def enviar_mensagem(request, pk):
    carro = get_object_or_404(Car, pk=pk)
    texto = request.POST.get("texto", "").strip()[:1000]

    if carro.vendedor == request.user:
        messages.error(request, "Você não pode enviar mensagem para o seu próprio anúncio.")
    elif not texto:
        messages.error(request, "Escreva uma mensagem antes de enviar.")
    else:
        Mensagem.objects.create(carro=carro, remetente=request.user, texto=texto)
        messages.success(request, "Mensagem enviada ao vendedor.")
    return redirect("car_detail", pk=pk)


# ---------------------------------------------------------------- Contas
class RegisterView(SuccessMessageMixin, CreateView):
    form_class = RegisterForm
    template_name = "cars/register.html"
    success_url = reverse_lazy("login")
    success_message = "Conta criada! Entre para continuar."
