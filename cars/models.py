from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

#usuário:
class Perfil(models.Model):
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="perfil"
    )
    cpf = models.CharField(verbose_name="CPF", max_length=11)
    cep = models.CharField(verbose_name="CEP", max_length=8)
    telefone = models.CharField(verbose_name="Telefone", max_length=11)

    class Meta:
        verbose_name = "Perfil"
        verbose_name_plural = "Perfis"

    def __str__(self):
        return self.usuario.get_username()


#modelos de carros:
class Car(models.Model):

    class Marca(models.TextChoices):
        CHEVROLET = "chevrolet", "Chevrolet"
        FIAT = "fiat", "Fiat"
        FORD = "ford", "Ford"
        HONDA = "honda", "Honda"
        HYUNDAI = "hyundai", "Hyundai"
        TOYOTA = "toyota", "Toyota"
        VOLKSWAGEN = "volkswagen", "Volkswagen"

    vendedor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="carros"
    )
    marca = models.CharField(verbose_name="Marca", max_length=20, choices=Marca.choices)
    modelo = models.CharField(verbose_name="Modelo", max_length=50)
    ano = models.PositiveIntegerField(verbose_name="Ano")
    preco = models.DecimalField(verbose_name="Preço", max_digits=10, decimal_places=2)
    usado = models.BooleanField(verbose_name="Usado", default=False)
    km_rodado = models.PositiveIntegerField(
        verbose_name="Km rodados", null=True, blank=True
    )
    aceita_troca = models.BooleanField(verbose_name="Aceita troca", default=False)
    descricao = models.TextField(verbose_name="Descrição", blank=True)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)


    #Abaixo, sistema pra perguntar a quilometragem se o carro for usado:
    def clean(self):
        if self.usado and self.km_rodado is None:
            raise ValidationError({"km_rodado": "Informe a quilometragem do carro usado."})
        if not self.usado:
            self.km_rodado = None


    #Abaixo, configuração pros nomes aparecerem corretamente no admin:
    class Meta:
        verbose_name = "Carro"
        verbose_name_plural = "Carros"
        ordering = ["-criado_em"]


    def __str__(self):
        return f"{self.get_marca_display()} {self.modelo} {self.ano}"


#Abaixo, tabela pras fotos dos carros
class FotoCarro(models.Model):
    carro = models.ForeignKey(Car, on_delete=models.CASCADE, related_name="fotos")
    imagem = models.ImageField(upload_to="carros/")

    class Meta:
        verbose_name = "Foto"
        verbose_name_plural = "Fotos"

    def __str__(self):
        return f"Foto de {self.carro}"


#Abaixo, tabela pras fotos dos favoritos do usuário 
class Favorito(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="favoritos"
    )
    carro = models.ForeignKey(Car, on_delete=models.CASCADE, related_name="favoritado_por")
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["usuario", "carro"], name="favorito_unico")
        ]

    def __str__(self):
        return f"{self.usuario} favoritou {self.carro}"


#Abaixo, tabela de mensagens do usuário
class Mensagem(models.Model):
    carro = models.ForeignKey(Car, on_delete=models.CASCADE, related_name="mensagens")
    remetente = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="mensagens_enviadas"
    )
    texto = models.TextField(verbose_name="Mensagem")
    enviada_em = models.DateTimeField(auto_now_add=True)
    lida = models.BooleanField(default=False)

    class Meta:
        ordering = ["-enviada_em"]

    def __str__(self):
        return f"{self.remetente} sobre {self.carro}"
