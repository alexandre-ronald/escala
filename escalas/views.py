from django.shortcuts import render, redirect
from core.models import Escala, AtribuicaoEscala, Funcionario, TipoTurno, Unidade
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.shortcuts import render, get_object_or_404

from django.http import Http404
import calendar
from datetime import datetime, date, timedelta


def gerar_escala(request, unidade_id, mes, ano):
    
    try:
        unidade = Unidade.objects.get(id=unidade_id)
    except Unidade.DoesNotExist:
        raise Http404("A unidade solicitada não existe. Por favor, adicione uma unidade com ID {} no admin.".format(unidade_id))

    escala = get_object_or_404(Escala, unidade_id=unidade_id, mes=mes, ano=ano)
    atribuicoes = AtribuicaoEscala.objects.filter(escala=escala).select_related("funcionario", "tipo_turno")

    num_days = calendar.monthrange(ano, mes)[1]
    days = [date(ano, mes, d) for d in range(1, num_days + 1)]

    # Monta estrutura por funcionário
    funcionarios_dict = {}
    for atrib in atribuicoes:
        func = atrib.funcionario
        
        if func.id not in funcionarios_dict:
            funcionarios_dict[func.id] = {
                "funcionario": func,
                "dias": {d.day: "" for d in days},  # todos os dias em branco
                "total_horas": 0,
            }

        funcionarios_dict[func.id]["dias"][atrib.dia] = atrib.tipo_turno.codigo

        funcionarios_dict[func.id]["dias_list"] = [
            funcionarios_dict[func.id]["dias"][d.day] for d in days
        ]
        
        if hasattr(atrib.tipo_turno, "duracao_horas"):
            funcionarios_dict[func.id]["total_horas"] += int(atrib.tipo_turno.duracao_horas)

    funcionarios = list(funcionarios_dict.values())

    

    # totais por turno (igual já tínhamos)
    totals = {"matutino": [], "vespertino": [], "noturno": []}
    for day in days:
        totals["matutino"].append(
            atribuicoes.filter(dia=day.day, tipo_turno__codigo__startswith="M").count()
        )
        totals["vespertino"].append(
            atribuicoes.filter(dia=day.day, tipo_turno__codigo__startswith="T").count()
        )
        totals["noturno"].append(
            atribuicoes.filter(dia=day.day, tipo_turno__codigo__startswith="N").count()
        )

    context = {
        "escala": escala,
        "days": days,
        "funcionarios": funcionarios,  # <- agora passamos estruturado
        "totals": totals,
    }
    return render(request, "escalas/escala_detalhe.html", context)


def cadastrar_escala(request):
    unidades = Unidade.objects.all()
    tipo_turnos = TipoTurno.objects.all()

    mes_atual = 4  # Abril como exemplo
    ano_atual = 2025
    dias = range(1, calendar.monthrange(ano_atual, mes_atual)[1] + 1)
    
    cargos_unicos = Funcionario.objects.values_list('cargo', flat=True).distinct()

    if request.method == 'POST':
        unidade_id = request.POST.get('unidade')
        cargo = request.POST.get('cargo')
        mes = int(request.POST.get('mes', mes_atual))
        ano = int(request.POST.get('ano', ano_atual))
        dias = range(1, calendar.monthrange(ano, mes)[1] + 1)

        unidade = Unidade.objects.get(id=unidade_id)

        try:
            escala = Escala.objects.get(mes=mes, ano=ano, unidade=unidade)
        except Escala.DoesNotExist:
            escala = Escala.objects.create(mes=mes, ano=ano, unidade=unidade, observacoes=request.POST.get('observacoes', ''))
        
        funcionarios = Funcionario.objects.filter(unidade=unidade)
        if cargo:
            funcionarios = funcionarios.filter(cargo=cargo)

        for func in funcionarios:
            print(func.nome_completo)
            for dia in dias:
                turno_codigo = request.POST.get(f'turno_{func.id}_{dia}')

                if turno_codigo:
                    tipo_turno = TipoTurno.objects.get(codigo=turno_codigo)
                    AtribuicaoEscala.objects.create(escala=escala, funcionario=func, dia=dia, tipo_turno=tipo_turno, ch_mensal=0)

        messages.success(request, "Escala cadastrada com sucesso!")
        return redirect('escala_detalhe', unidade_id=unidade_id, mes=mes, ano=ano)

    return render(request, 'escalas/cadastrar_escala.html', {
        'unidades': unidades,
        'tipo_turnos': tipo_turnos,
        'mes_atual': mes_atual,
        'ano_atual': ano_atual,
        'dias': dias,
        'cargos_unicos': cargos_unicos
    })

def calcular_ch_mensal(request, escala_id):
    if request.method == 'POST':
        escala = Escala.objects.get(id=escala_id)
        atribuicoes = AtribuicaoEscala.objects.filter(escala=escala)
        for atribuicao in atribuicoes:
            total_horas = sum(a.tipo_turno.duracao_horas for a in atribuicoes.filter(funcionario=atribuicao.funcionario))
            atribuicao.ch_mensal = total_horas
            atribuicao.save()
        return JsonResponse({'status': 'success', 'total_horas': total_horas})
    return JsonResponse({'status': 'error'})

def obter_dias_mes_completo(ano, mes):
    # Número de dias no mês atual
    num_days = calendar.monthrange(ano, mes)[1]
    # Primeiro dia do mês
    primeiro_dia = date(ano, mes, 1)
    # Dia da semana do primeiro dia do mês (0=segunda-feira, 6=domingo)
    primeiro_dia_semana = primeiro_dia.weekday()
    
    # Início da semana anterior (domingo)
    inicio_semana = primeiro_dia - timedelta(days=(primeiro_dia_semana + 1) % 7)
    
    # Lista de listas (semanas)
    semanas = []
    semana_atual = []
    dia_atual = inicio_semana

    while dia_atual.month == mes or (dia_atual < primeiro_dia and dia_atual.weekday() != 6):
        semana_atual.append({
            'data': dia_atual,
            'nomes': []  # Substitua pela lógica adequada para obter os nomes do plantão se necessário
        })
        if dia_atual.weekday() == 6:  # fim da semana (sábado)
            semanas.append(semana_atual)
            semana_atual = []
        
        dia_atual += timedelta(days=1)
    
    # Garantir que após o loop finalizemos a última semana
    if semana_atual:
        semanas.append(semana_atual)
    
    return semanas

def obter_dias_mes(ano, mes):
    # Número de dias no mês
    num_days = calendar.monthrange(ano, mes)[1]
    # Primeiro dia do mês
    primeiro_dia = date(ano, mes, 1)
    # Dia da semana do primeiro dia do mês (0=segunda-feira, 6=domingo)
    dia_da_semana = primeiro_dia.weekday()
    
    # Calcular o número de dias a adicionar do mês anterior
    inicio_semana = primeiro_dia - timedelta(days=(dia_da_semana + 1) % 7)
    
    # Lista completa de dias incluindo dias do mês anterior ou posterior
    days = []
    current_day = inicio_semana

    while current_day.month == mes or (current_day.month == mes - 1 or (mes == 1 and current_day.month == 12)):
        days.append(current_day)
        current_day += timedelta(days=1)
    
    # Preencher até o final da semana, se necessário
    while current_day.weekday() != 6:
        days.append(current_day)
        current_day += timedelta(days=1)
    
    return days

@csrf_exempt
def get_funcionarios(request):
    unidade_id = request.GET.get('unidade')
    cargo = request.GET.get('cargo')
    if not unidade_id:
        return JsonResponse({'error': 'Unidade não especificada'}, status=400)
    
    funcionarios = Funcionario.objects.filter(unidade_id=unidade_id).order_by('nome_completo')
    if cargo:
        funcionarios = funcionarios.filter(cargo=cargo)

    
    
    data = [{
        'id': f.id,
        'nome_completo': f.nome_completo,
        'siape': f.siape,
        'registro_conselho': f.registro_conselho,
        'cargo': f.cargo,
        'vinculo': f.vinculo,
        'ch_semanal': f.ch_semanal,
        'preferencias_turno': f.preferencias_turno
    } for f in funcionarios]
        
    return JsonResponse(data, safe=False)

from datetime import date
import calendar
from django.shortcuts import render
from core.models import AtribuicaoEscala, Escala
from core.models import Unidade  # ajuste se necessário

def cobertura1(request):
    import datetime

    # Pega mês e ano do POST ou atual
    mes = int(request.POST.get("mes", datetime.datetime.now().month))
    ano = int(request.POST.get("ano", datetime.datetime.now().year))

    # Unidade selecionada
    unidade_selecionada = request.POST.get("unidade")
    unidades = Unidade.objects.all()

    # Pegar a escala do mês/ano/unidade
    escala = None
    nome_unidade = ""
    if unidade_selecionada:
        escala = Escala.objects.filter(mes=mes, ano=ano, unidade_id=unidade_selecionada).first()
        if escala:
            nome_unidade = escala.unidade.nome

    # Número de dias do mês
    num_days = calendar.monthrange(ano, mes)[1]

    # Lista de dias do mês
    days = [date(ano, mes, d) for d in range(1, num_days + 1)]

    days = obter_dias_mes_completo(ano, mes)

    # Dias da semana em português
    dias_semana_pt = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]

    # Preparando dias com nome do dia e funcionários
    dias_mes = []
    semana_atual = []
    for day in days:
        nomes = []
        if escala:
            atribuicoes = AtribuicaoEscala.objects.filter(escala=escala, dia=day.day)
            nomes = [a.funcionario.nome_completo for a in atribuicoes]

        # Cria objeto simples para template
        dia_obj = type('Dia', (), {})()
        dia_obj.data = day
        dia_obj.nome_dia = dias_semana_pt[day.weekday()]
        dia_obj.nomes = nomes

        semana_atual.append(dia_obj)

        # Quebra semana a cada domingo
        if day.weekday() == 6:
            dias_mes.append(semana_atual)
            semana_atual = []

    # Adiciona última semana se tiver dias restantes
    if semana_atual:
        dias_mes.append(semana_atual)

    # Meses e anos para filtros
    meses = [(i, calendar.month_name[i]) for i in range(1, 13)]
    anos = [ano-1, ano, ano+1]

    MESES_PT = [
        "", "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
        "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
    ]
    meses = [(i, MESES_PT[i]) for i in range(1, 13)]

   

    context = {
        "dias_mes": dias_mes,
        "mes": mes,
        "ano": ano,
        "meses": meses,
        "anos": anos,
        "unidades": unidades,
        "unidade_selecionada": int(unidade_selecionada) if unidade_selecionada else None,
        "nome_unidade": nome_unidade,
    }

    return render(request, "escalas/cobertura.html", context)



def cobertura(request):

    atribuicoes = ''
    nome_unidade = ''
    

    ano = int(request.POST.get("ano", datetime.now().year))
    mes = int(request.POST.get("mes", datetime.now().month))
    unidade_id = request.POST.get("unidade")
    

    anos = [ano for ano in range(2023, ano + 2)]  # exemplo

    if request.method == 'POST':
        if unidade_id :
            unidade_id = int(unidade_id)
            escala = Escala.objects.filter(ano=ano, mes=mes, unidade_id = unidade_id).first()
            if escala: 
                escala_id = escala.id
                nome_unidade = escala.unidade.nome 
                # buscar atribuições no banco (ajuste conforme seus models)
                atribuicoes = AtribuicaoEscala.objects.filter(escala_id=escala_id)


    # montar matriz de dias do mês (semanas completas)
    cal = calendar.Calendar(firstweekday=6)  # domingo
    dias_mes = list(cal.monthdatescalendar(ano, mes))
    

    # dicionário dia -> nomes
    cobertura_dict = {}

    for atrib in atribuicoes:
        d = atrib.dia
        if d not in cobertura_dict:
            cobertura_dict[d] = []
        cobertura_dict[d].append(atrib.funcionario.nome_completo)

    # agora monta matriz com nomes já prontos
    dias_com_cobertura = []
    for semana in dias_mes:
        semana_lista = []
        for dia in semana:
            nomes = cobertura_dict.get(dia.day, []) if dia.month == mes else []
            semana_lista.append({
                "data": dia,
                "nomes": nomes
            })
        semana_lista = semana_lista
        dias_com_cobertura.append(semana_lista)

    MESES_PT = [
        "", "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
        "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
    ]
    meses = [(i, MESES_PT[i]) for i in range(1, 13)]
   

    return render(request, "escalas/cobertura.html", {
        "nome_unidade":nome_unidade,
        "ano": ano,
        "mes": mes,
        "anos":anos,
        "dias_mes": dias_com_cobertura,
        "meses": meses,
        "unidade_selecionada": unidade_id,
        "unidades": Unidade.objects.all(),
        
    })

def ver_escalas(request):

    atribuicoes = []
    nome_unidade = ''

    ano = int(request.POST.get("ano", datetime.now().year))
    mes = int(request.POST.get("mes", datetime.now().month))
    unidade_id = int(request.POST.get("unidade",0))

    try:
        unidade = Unidade.objects.get(id=unidade_id)    
        nome_unidade = unidade.nome
    except Unidade.DoesNotExist:
        nome_unidade =''
        unidade = []
    
    escala = Escala.objects.filter(ano=ano, mes=mes, unidade_id = unidade_id).first()

    atribuicoes = AtribuicaoEscala.objects.filter(escala=escala)

    
    num_days = calendar.monthrange(ano, mes)[1]
    days = [date(ano, mes, d) for d in range(1, num_days + 1)]
        
    dias_com_cobertura = []

    cal = calendar.Calendar(firstweekday=6)  # domingo
    dias_mes = list(cal.monthdatescalendar(ano, mes))

    # dicionário dia -> nomes
    cobertura_dict = {}

    for semana in dias_mes:
        semana_lista = []
        for dia in semana:
            nomes = cobertura_dict.get(dia.day, []) if dia.month == mes else []
            semana_lista.append({
                "data": dia,
                "nomes": nomes
            })
        semana_lista = semana_lista
        dias_com_cobertura.append(semana_lista)

    funcionarios_dict = {}
    for atrib in atribuicoes:
        func = atrib.funcionario
        
        if func.id not in funcionarios_dict:
            funcionarios_dict[func.id] = {
                "funcionario": func,
                "dias": {d.day: "" for d in days},  # todos os dias em branco
                "total_horas": 0,
            }

        funcionarios_dict[func.id]["dias"][atrib.dia] = atrib.tipo_turno.codigo

        funcionarios_dict[func.id]["dias_list"] = [
            funcionarios_dict[func.id]["dias"][d.day] for d in days
        ]
        
        if hasattr(atrib.tipo_turno, "duracao_horas"):
            funcionarios_dict[func.id]["total_horas"] += int(atrib.tipo_turno.duracao_horas)

    funcionarios = list(funcionarios_dict.values())

    MESES_PT = [
        "", "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
        "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
    ]
    meses = [(i, MESES_PT[i]) for i in range(1, 13)]


    anos = [ano for ano in range(2023, ano + 2)]  # exemplo

    # totais por turno (igual já tínhamos)
    totals = {"matutino": [], "vespertino": [], "noturno": []}
    for day in days:
        totals["matutino"].append(
                atribuicoes.filter(dia=day.day, tipo_turno__codigo__startswith="M").count()
        )
        totals["vespertino"].append(
            atribuicoes.filter(dia=day.day, tipo_turno__codigo__startswith="T").count()
        )
        totals["noturno"].append(
            atribuicoes.filter(dia=day.day, tipo_turno__codigo__startswith="N").count()
        )

    return render(request, "escalas/ver_escala.html",{
        "ano": ano,
        "mes": mes,
        "anos":anos,
        "meses": meses,
        "days": days,
        "funcionarios": funcionarios, 
        "dias_mes": dias_com_cobertura,
        'nome_unidade': nome_unidade,
        "unidade_selecionada": unidade_id,
        "unidades": Unidade.objects.all(),
        'totals':totals,
    })