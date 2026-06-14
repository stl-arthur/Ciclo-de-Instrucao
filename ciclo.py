# ==================== Vetor de Memória, Armazena os dados e instruções ====================
MEM = [None] * 512

# ==================== Registradores de Uso Geral ====================
A = None
B = None

# ==================== Registradores Especiais ====================
PC = 0
IR = None
MAR = None
MBR = None
AC = None
M = None
R = None
C = None
N = None
Z = None

# ============================ DECODE E EXECUTE =======================================
# CONSTANTES DOS MODOS DE ENDEREÇAMENTO
IMEDIATO = 0 # valor literal      ex: ADD #5
DIRETO = 1 # M(endereco)          ex: LOAD M(0x101)

# LIMITES DE INTEIRO DO IAS => PLAVARAS DE 40bits
MAX_INT =  549755813887   # 2^39 - 1
MIN_INT = -549755813888   # -2^39

# Instrução: LOAD M(0x101)
# LOAD => opcode          0x101 => operando

#----------------------- FUNÇÕES AUXILIARES ------------------------------
def determinar_modo(operando) -> None|int:
    '''Determina o modo de endereçamento'''
    
    if operando[0] == "M":
        return DIRETO
    elif operando[0] == "#":
        return IMEDIATO
    else:
        print(f"Modo inválido: {operando}")

def buscar_valor(operando, modo) -> int:
    '''Busca o valor do operando conforme o modo de endereçamento'''

    global MAR, MBR

    if modo == IMEDIATO: # valor direto, sem acessar memória
        return operando
    else:
        MAR = operando   # MAR recebe o endereço
        MBR = MEM[MAR]   # MBR recebe o valor na memória
        return MBR
    
def atualizar_flags(valor) -> None:
    '''Atualiza as falgs N e Z conforme o valor resultante'''

    global Z, N

    if valor == 0:
        Z = 1
    else:
        Z = 0

    if valor < 0:
        N = 1
    else: 
        N = 0

def verifivcar_overflow(resultado) -> bool:
    '''Retorna True se houve overflow, False caso contrário'''

    if resultado > MAX_INT or resultado < MIN_INT:
        return True
    return False

################### DECODE / EXECUTE ######################

def decodificar(IR) -> None:
    '''Decodifica a instrução do IR em opcode, operando e modo'''

    partes = IR.split() # ex: ["LOAD", "M(0x101)"]
    opcode = partes[0]  # "LOAD"

    tam_partes = len(partes)

    if tam_partes > 1:
        operando_str = partes[1]
        modo = determinar_modo(operando_str)
        if modo == DIRETO:
            conteudo = operando_str[2:-1]
            if conteudo.startswith('0x') or conteudo.startswith('0X'):
                operando = int(conteudo, 16)
            else:
                operando = int(conteudo)
        elif modo == IMEDIATO:
            operando = int(operando_str[1:])

    return opcode, operando, modo


def executar(opcode: int, operando, modo) -> None:
    '''Função responsável por executar cada instrução decodificada, do conjunto (LOAD, STOR, ADD, SUB, MULT, DIV, JUMP, JUMP+, LOADI, STORI) incluindo os modos de endereçamento imediato, direto e indireto'''
    
    global AC, M, R, C, N, Z, PC, MAR, MBR

    if opcode == "LOAD":
        # Busca operando e coloca no AC
        AC = buscar_valor(operando, modo)
        atualizar_flags(AC)

    elif opcode == "STOR":
        # Sempre direto, não existe STOR imediato
        MEM[operando] = AC

    elif opcode == "ADD":
        valor = buscar_valor(operando, modo)
        resultado = AC + valor
        C = verifivcar_overflow(resultado)
        AC = resultado
        atualizar_flags(AC)

    elif opcode == "SUB":
        valor = buscar_valor(operando, modo)
        resultado = AC - valor
        C = verifivcar_overflow(resultado)
        AC = resultado
        atualizar_flags(AC)

    elif opcode == "MULT":
        valor = buscar_valor(operando, modo)
        M = valor
        AC *= M
        atualizar_flags(AC)

    elif opcode == "DIV":
        valor = buscar_valor(operando, modo)
        R = AC % valor
        AC //= valor
        atualizar_flags(AC)

    elif opcode == "JUMP":
        # operando é sempre endereço direto
        PC = operando

    elif opcode == "JUMP+":
        # salta se AC >= 0 (N == 0)
        if N == 0:
            PC = operando

    elif opcode == "LOADI":
        # operando aponta para a célula que contém o endereço final
        MAR = operando
        MBR = MEM[MAR] # MBR = endereço apontado
        MAR = MBR
        MBR = MEM[MAR] # MBR = valor final
        AC = MBR
        atualizar_flags(AC)

    elif opcode == "STORI":
        # operando aponta para a célula que contém o endereço final
        MAR = operando
        MBR = MEM[MAR]
        MEM[MBR] = AC # MBR = endereço apontado

    else:
        print("opcode inválido: " + opcode)

# ======================================== OPERAÇÕES ========================================

def carregaArquivo(arquivo: str):
    '''
    Função que lê e carrega o arquivo para o vetor 'MEM' com somente as informações válidas para a execução do programa
    '''
    global PC

    try:
        with open(arquivo, 'r') as arq:
            linhas = arq.readlines()
    except FileNotFoundError:
        print(f"Erro: Arquivo {arquivo} não encontrado!")
        return False
    
    linhas_limpas = []
    for l in linhas:
        #Remove os comentarios e espaços nas linhas do arquivo
        
        sem_comentario = l.split("#")[0]
        sem_espaco = sem_comentario.strip()
        linhas_limpas.append(sem_espaco)

    linhas_finais = []
    for l in linhas_limpas:
        #Remove as linhas vazias do linhas_limpas
    
        if l:
            linhas_finais.append(l)

    linhas = linhas_finais

    end_inicial = None
    ind_inicio_instrucao = None

    i = 0
    for linha in linhas:
        #Encontra a linha de endereço inicial 0xNN

        if linha.startswith('0x') or linha.startswith('0X'):
            end_inicial = int(linha, 16)
            ind_inicio_instrucao = i + 1
            break
        i += 1

    if end_inicial is None:
        print("Erro: Não foi encontrado um endereço inicial no arquivo!")
        return False
    
    dados = linhas[:ind_inicio_instrucao - 1]
    i = 0
    for valor in dados:
        MEM[i] = int(valor)
        i += 1

    instrucoes = linhas[ind_inicio_instrucao:]
    i = 0
    for instrucao in instrucoes:
        MEM[end_inicial + i] = instrucao
        i += 1

    PC = end_inicial

    print(f"[Parser] {len(dados)} dados carregados a partir de 0x00")
    print(f"[Parser] {len(instrucoes)} instruções carregadas a partir de 0x{end_inicial:02X}")
    print(f"[Parser] PC inicial = 0x{PC:02X}")
    return True


def mostraRegistradores():
    '''
    Procedimento que printa estado dos resgistradores desde que eles tenham valor válido
    '''
    if MAR != None:
        mar_str = f"0x{MAR:02X}" 
    else:
        mar_str = "None"


    print("==================== Registradores ====================")
    print(f" PC = 0x{PC:02X} IR  = {IR}")
    print(f" MAR = {mar_str} MBR = {MBR}")
    print(f" AC = {AC} M = {M}")
    print(f" R = {R} C = {C}")
    print(f" N = {N} Z = {Z}")
    print("=======================================================\n")


def cicloDeBusca():
    '''
    Realiza o ciclo de busca 
    '''

    global PC, IR, MAR, MBR

    MAR = PC
    MBR = MEM[MAR]
    IR = MBR
    PC += 1

# ======================================== Laço Principal ========================================

def main():
    arquivo = input("Qual arquivo a ser trabalhado?\n>>> ")
    if not carregaArquivo(arquivo):
        return
    
    print("\nEstado Inicial (antes das instruções):")
    mostraRegistradores()

    while True:
        if PC > 0XFF or MEM[PC] is None or not isinstance(MEM[PC], str):
            print("Fim do programa.")
            break

        cicloDeBusca()

        opcode, operando, modo = decodificar(IR)
        executar(opcode, operando, modo)

        mostraRegistradores()
        input("Pressione ENTER para continuar")

if __name__ == "__main__":
    main()
