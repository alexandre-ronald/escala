from django.db import models
from dateutil.relativedelta import relativedelta
import datetime

class Unidade(models.Model):
    nome = models.CharField(max_length=200)  # ex.: UNIDADE DE OBSTETRÍCIA - CCOG
    portaria = models.CharField(max_length=50, blank=True)  # ex.: 1192/2023

class Turno(models.Model):
    sigla = models.CharField(max_length=10)  # ex.: M6, N2, FO
    descricao = models.CharField(max_length=100)  # ex.: Matutino 07:00-13:00
    hora_inicio = models.TimeField(null=True)
    hora_fim = models.TimeField(null=True)
    horas = models.FloatField()  # ex.: 6.0
    periodo = models.CharField(max_length=20)  # matutino, vespertino, noturno, folga

    def __str__(self):
        return f"{self.sigla} - Horas {self.horas}"

class Funcionario(models.Model):
    nome_completo = models.CharField(max_length=200)
    siape = models.CharField(max_length=20)
    registro_conselho = models.CharField(max_length=20, blank=True)
    classe = models.CharField(max_length=10, blank=True)
    cargo = models.CharField(max_length=50)  # ex.: TE, ENF, AE
    vinculo = models.CharField(max_length=50)  # ex.: EBSERH, UFMA, MS
    ch_semanal = models.IntegerField()  # ex.: 36, 40
    unidade = models.ForeignKey(Unidade, on_delete=models.CASCADE)
    grupo = models.CharField(max_length=50, blank=True)  # ex.: TÉCNICOS EM ENFERMAGEM
    preferencias_turno = models.CharField(max_length=100, blank=True)  # ex.: M6, T6

class Feriado(models.Model):
    data = models.DateField()
    tipo = models.CharField(max_length=10)  # FD, PF

class Ferias(models.Model):
    funcionario = models.ForeignKey(Funcionario, on_delete=models.CASCADE)
    data_inicio = models.DateField()
    data_fim = models.DateField()

class Escala(models.Model):
    mes = models.IntegerField()
    ano = models.IntegerField()
    unidade = models.ForeignKey(Unidade, on_delete=models.CASCADE)
    gerada_em = models.DateTimeField(auto_now_add=True)
    observacoes = models.TextField(blank=True)  # ex.: Férias de X de Y a Z

class AtribuicaoEscala(models.Model):
    escala = models.ForeignKey('Escala', on_delete=models.CASCADE)
    funcionario = models.ForeignKey('core.Funcionario', on_delete=models.CASCADE)
    dia = models.PositiveSmallIntegerField()
    tipo_turno = models.ForeignKey(Turno, on_delete=models.CASCADE)
    # Campo para carga horária mensal (calculado)
    ch_mensal = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.funcionario.nome_completo} - Dia {self.dia} - {self.tipo_turno.codigo}"