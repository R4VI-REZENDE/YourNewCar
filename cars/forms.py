from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import Car, FotoCarro


class BootstrapMixin:
    """Aplica as classes do Bootstrap em todos os campos do formulário."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for campo in self.fields.values():
            widget = campo.widget
            if isinstance(widget, forms.CheckboxInput):
                widget.attrs["class"] = "form-check-input"
            elif isinstance(widget, forms.Select):
                widget.attrs["class"] = "form-select"
            else:
                widget.attrs["class"] = "form-control"


# --- Upload de várias fotos (padrão da documentação do Django) ---
class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleImageField(forms.ImageField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput(attrs={"accept": "image/*"}))
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        limpar = super().clean
        if isinstance(data, (list, tuple)):
            return [limpar(arquivo, initial) for arquivo in data]
        return [limpar(data, initial)]


class CarForm(BootstrapMixin, forms.ModelForm):
    fotos = MultipleImageField(
        label="Fotos",
        required=False,
        help_text="Você pode selecionar várias fotos de uma vez.",
    )

    class Meta:
        model = Car
        fields = [
            "marca", "modelo", "ano", "preco",
            "usado", "km_rodado", "aceita_troca", "descricao",
        ]
        widgets = {"descricao": forms.Textarea(attrs={"rows": 4})}

    def save(self, commit=True):
        carro = super().save(commit)
        if commit:
            for arquivo in self.cleaned_data["fotos"]:
                if arquivo:
                    FotoCarro.objects.create(carro=carro, imagem=arquivo)
        return carro


class LoginForm(BootstrapMixin, AuthenticationForm):
    pass


class RegisterForm(BootstrapMixin, UserCreationForm):
    pass
