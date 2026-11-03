from .models import Car, Mensagem


def global_context(request):
    """Variáveis disponíveis em TODOS os templates (sidebar, navbar e botões de favorito)."""
    contexto = {
        "marcas": Car.Marca.choices,
        "favoritos_ids": set(),
        "mensagens_novas": 0,
    }
    if request.user.is_authenticated:
        contexto["favoritos_ids"] = set(
            request.user.favoritos.values_list("carro_id", flat=True)
        )
        contexto["mensagens_novas"] = Mensagem.objects.filter(
            carro__vendedor=request.user, lida=False
        ).count()
    return contexto
