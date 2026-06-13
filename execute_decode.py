# CONSTANTES DOS MODOS DE ENDEREÇAMENTO
IMEDIATO = 0 # valor literal      ex: ADD #5
DIRETO = 1 # M(endereco)          ex: LOAD M(0x101)

# LIMITES DE INTEIRO DO IAS => PLAVARAS DE 40bits
MAX_INT =  549755813887   # 2^39 - 1
MIN_INT = -549755813888   # -2^39

MEM = [0] * 256
PC = 0
IR = -1
MAR = -1
MBR = -1
AC = -1
A = -1
B = -1
M = -1
R = -1
C = -1
N = -1
Z = -1

# Instrução: LOAD M(0x101)
# LOAD => opcode          0x101 => operando

#################### FUNÇÕES AUXILIARES #############################
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

################### DECODE / EXECUTE #######################

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
            operando = int(operando[1:])

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
