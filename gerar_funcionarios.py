import os
import django
import random

# Configura o ambiente Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'escala_trabalho.settings')  # Ajuste para o nome do seu projeto
django.setup()

from core.models import Funcionario, Unidade  # Ajuste o import conforme o nome do seu app

# Listas de nomes e sobrenomes comuns brasileiros para gerar nomes fictícios
nomes = [
    'João', 'Maria', 'Ana', 'Pedro', 'José', 'Paula', 'Carlos', 'Fernanda', 'Lucas', 'Juliana',
    'Rafael', 'Camila', 'Gabriel', 'Larissa', 'Felipe', 'Beatriz', 'Matheus', 'Isabela', 'Bruno', 'Letícia',
    'Diego', 'Vitória', 'Thiago', 'Sophia', 'Rodrigo', 'Amanda', 'Gustavo', 'Laura', 'Eduardo', 'Bianca',
    'Ricardo', 'Natália', 'Henrique', 'Alícia', 'André', 'Gabriela', 'Vinícius', 'Luana', 'Leonardo', 'Carolina',
    'Alexandre', 'Manuela', 'Fábio', 'Valentina', 'Roberto', 'Helena', 'Sérgio', 'Clara', 'Antônio', 'Elisa',
    'Miguel', 'Alice', 'Arthur', 'Heloísa', 'Samuel', 'Lívia', 'Davi', 'Yasmin', 'Lorenzo', 'Mirella',
    'Benjamin', 'Rebeca', 'Heitor', 'Stella', 'Enzo', 'Luna', 'Joaquim', 'Maya', 'Valentim', 'Aurora',
    'Theo', 'Melissa', 'Lucca', 'Cecília', 'César', 'Eloá', 'Isaac', 'Esther', 'Bernardo', 'Sarah',
    'Daniel', 'Olívia', 'Murilo', 'Liz', 'Luan', 'Antonella', 'Otávio', 'Allana', 'Cauê', 'Milena',
    'Ian', 'Lavínia', 'Levi', 'Maria Eduarda', 'Noah', 'Maria Clara', 'Bento', 'Maria Julia', 'Vicente', 'Maria Luiza'
]

sobrenomes = [
    'Silva', 'Santos', 'Oliveira', 'Souza', 'Rodrigues', 'Ferreira', 'Alves', 'Pereira', 'Lima', 'Costa',
    'Ribeiro', 'Carvalho', 'Gomes', 'Martins', 'Araújo', 'Melo', 'Barbosa', 'Cardoso', 'Nunes', 'Dias',
    'Rocha', 'Marques', 'Vieira', 'Castro', 'Machado', 'Fernandes', 'Mendes', 'Freitas', 'Monteiro', 'Moreira',
    'Correia', 'Cavalcanti', 'Batista', 'Moura', 'Cavalcante', 'Lopes', 'Miranda', 'Gonçalves', 'Borges', 'Teixeira',
    'Reis', 'Pinto', 'Ramos', 'Tavares', 'Bezerra', 'Farias', 'Magalhães', 'Dantas', 'Leite', 'Peixoto',
    'Barros', 'Campos', 'Viana', 'Andrade', 'Nogueira', 'Xavier', 'Pires', 'Duarte', 'Figueiredo', 'Sousa',
    'Braga', 'Macedo', 'Pinheiro', 'Moraes', 'Queiroz', 'Garcia', 'Almeida', 'Fonseca', 'Cruz', 'Brito',
    'Guimarães', 'Aguiar', 'Rezende', 'Sales', 'Furtado', 'Siqueira', 'Medeiros', 'Paiva', 'Morais', 'Azevedo',
    'Amaral', 'Franco', 'Cunha', 'Sampaio', 'Assis', 'Neves', 'Mesquita', 'Domingues', 'Coelho', 'Rego',
    'Guedes', 'Pessoa', 'Saraiva', 'Lins', 'Pontes', 'Nascimento', 'Fagundes', 'Matos', 'Dutra', 'Guerra'
]

# Lista de opções para campos
cargos = ['TE', 'ENF', 'AE']
vinculos = ['EBSERH', 'UFMA', 'MS']
grupos = ['TÉCNICOS EM ENFERMAGEM', 'ENFERMEIROS', 'AUXILIARES']
ch_semanais = [36, 40]
turnos_preferidos = ['M6', 'T6', 'N12', 'M12', 'T12', '']

# Função para criar unidades de exemplo, se necessário
def criar_unidades():
    unidades_nomes = ['UTI Adulto', 'Clínica Médica', 'Emergência', 'Pediatria', 'Centro Cirúrgico']
    unidades = []
    for nome in unidades_nomes:
        unidade, created = Unidade.objects.get_or_create(nome=nome)
        unidades.append(unidade)
    return unidades

# Função para gerar nome completo aleatório
def gerar_nome_completo():
    nome = random.choice(nomes)
    sobrenome1 = random.choice(sobrenomes)
    sobrenome2 = random.choice(sobrenomes)
    return f"{nome} {sobrenome1} {sobrenome2}"

# Função para gerar matrícula SIAPE (7 dígitos)
def gerar_siape():
    return str(random.randint(1000000, 9999999))

# Função para gerar registro do conselho (ex.: COREN-123456)
def gerar_registro_conselho():
    if random.choice([True, False]):
        return f"COREN-{random.randint(100000, 999999)}"
    return ""

# Função para gerar classe (ex.: A, B, C, ou vazio)
def gerar_classe():
    if random.choice([True, False]):
        return random.choice(['A', 'B', 'C'])
    return ""

# Gera 100 funcionários
def gerar_funcionarios(n=100):
    # Cria ou obtém unidades
    unidades = criar_unidades()
    
    # Lista para garantir SIAPEs únicos
    siapes_usados = set()

    for _ in range(n):
        # Gera SIAPE único
        siape = gerar_siape()
        while siape in siapes_usados:
            siape = gerar_siape()
        siapes_usados.add(siape)

        # Cria o funcionário
        Funcionario.objects.create(
            nome_completo=gerar_nome_completo(),
            siape=siape,
            registro_conselho=gerar_registro_conselho(),
            classe=gerar_classe(),
            cargo=random.choice(cargos),
            vinculo=random.choice(vinculos),
            ch_semanal=random.choice(ch_semanais),
            unidade=random.choice(unidades),
            grupo=random.choice(grupos),
            preferencias_turno=random.choice(turnos_preferidos)
        )
    print(f"{n} funcionários criados com sucesso!")

if __name__ == "__main__":
    gerar_funcionarios(100)