from django.contrib import admin

# Register your models here.
# Register your models here.
from django.contrib import admin
from cars.models import Car, Perfil, FotoCarro, Favorito, Mensagem  # import absoluto: "cars"


# Cada ModelAdmin configura como o model aparece no painel
class CarAdmin(admin.ModelAdmin):
    # colunas exibidas na listagem
    list_display = ("marca", "modelo", "ano", "preco", "usado", "vendedor")
    # campos usados na barra de busca ("vendedor__username" busca pelo usuário)
    search_fields = ("modelo", "vendedor__username")
    # filtros na lateral
    list_filter = ("marca", "usado", "ativo")


class PerfilAdmin(admin.ModelAdmin):
    list_display = ("usuario", "cpf", "cep", "telefone")
    search_fields = ("usuario__username", "cpf")  # atenção à vírgula


class MensagemAdmin(admin.ModelAdmin):
    list_display = ("carro", "remetente", "enviada_em", "lida")
    list_filter = ("lida",)  # vírgula obrigatória: ("lida",)


class FavoritoAdmin(admin.ModelAdmin):
    list_display = ("usuario", "carro", "criado_em")


# Liga cada model à sua configuração no admin
admin.site.register(Car, CarAdmin)
admin.site.register(Perfil, PerfilAdmin)
admin.site.register(Mensagem, MensagemAdmin)
admin.site.register(Favorito, FavoritoAdmin)
admin.site.register(FotoCarro)  # sem ModelAdmin