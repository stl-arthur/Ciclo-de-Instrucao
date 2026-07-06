
# Vetor de Memoria (256 posicoes)
MEM = [None] * 256

# Registradores de Uso Geral
A = None
B = None

#Registradores Especiais
PC  = 0
IR  = None
MAR = None
MBR = None
AC  = None
M   = None
R   = None
C   = None
N   = None
Z   = None

#CONSTANTES DE MODO
IMEDIATO = 0  # valor literal      ex: ADD #5
DIRETO   = 1  # M(endereco)        ex: LOAD M(0x101)

# Limites de inteiro do IAS (palavras de 40 bits)
MAX_INT =  549755813887   #  2^39 - 1
MIN_INT = -549755813888   # -2^39

# ======================== FUNCOES AUXILIARES ========================
def eh_numero(linha):
    '''Verifica se a linha representa um numero (decimal ou hexadecimal)
 
    >>> eh_numero("15")
    True
    >>> eh_numero("0x110")
    True
    >>> eh_numero("-42")
    True
    >>> eh_numero("LOAD M(0x07)")
    False
    ''' 
    try:
        if linha.lower().startswith('0x'):
            int(linha, 16)
        else:
            int(linha)
        return True
    except ValueError:
        return False

def determinar_modo(operando_str):
    '''Determina o modo de enderecamento a partir da string do operando
 
    >>> determinar_modo("M(0x07)") == DIRETO
    True
    >>> determinar_modo("#5") == IMEDIATO
    True
    >>> determinar_modo("X(0x07)")
    Modo invalido: X(0x07)
    '''   
    if operando_str[0] == 'M':
        return DIRETO
    elif operando_str[0] == '#':
        return IMEDIATO
    else:
        print('Modo invalido: ' + operando_str)
        return None

def buscar_valor(operando, modo):
    '''Busca o valor do operando conforme o modo de enderecamento
 
    >>> import sys; m = sys.modules[__name__]
    >>> m.MEM[0x07] = 15
    >>> buscar_valor(0x07, DIRETO)
    15
    >>> m.MAR
    7
    >>> m.MBR
    15
    >>> buscar_valor(5, IMEDIATO)
    5
    '''
    global MAR, MBR

    if modo == IMEDIATO:
        return operando       # valor literal, sem acesso a memoria
    else:
        MAR = operando        # MAR recebe o endereco
        MBR = MEM[MAR]        # MBR recebe o valor armazenado
        return MBR

def atualizar_flags(valor):
    '''Atualiza as flags N e Z conforme o valor resultante
 
    >>> import sys; m = sys.modules[__name__]
    >>> atualizar_flags(0)
    >>> m.Z
    1
    >>> m.N
    0
    >>> atualizar_flags(-3)
    >>> m.Z
    0
    >>> m.N
    1
    >>> atualizar_flags(7)
    >>> m.Z
    0
    >>> m.N
    0
    '''    
    global Z, N

    if valor == 0:
        Z = 1
    else:
        Z = 0

    if valor < 0:
        N = 1
    else:
        N = 0

def verificar_overflow(resultado):
    '''Retorna True se houve overflow, False caso contrario
 
    >>> verificar_overflow(100)
    False
    >>> verificar_overflow(MAX_INT + 1)
    True
    >>> verificar_overflow(MIN_INT - 1)
    True
    '''
    if resultado > MAX_INT or resultado < MIN_INT:
        return True
    return False

# ======================== DECODE / EXECUTE ========================

def decodificar(IR):
    '''Decodifica a instrucao do IR em opcode, operando e modo
 
    >>> decodificar("LOAD M(0x07)")
    ('LOAD', 7, 1)
    >>> decodificar("ADD #5")
    ('ADD', 5, 0)
    >>> decodificar("JUMP M(0xAF)")
    ('JUMP', 175, 1)
    '''
    partes = IR.split()       # ex: ["LOAD", "M(0x101)"]
    opcode = partes[0]        # "LOAD"

    operando = None
    modo = None

    if len(partes) > 1:
        operando_str = partes[1]
        modo = determinar_modo(operando_str)

        if modo == DIRETO:
            # extrai o endereco de dentro de M(...)
            conteudo = operando_str[2:-1]
            if conteudo.startswith('0x') or conteudo.startswith('0X'):
                operando = int(conteudo, 16)
            else:
                operando = int(conteudo)

        elif modo == IMEDIATO:
            operando = int(operando_str[1:])

    return opcode, operando, modo


def executar(opcode, operando, modo):
    '''Executa a instrucao decodificada
 
    >>> import sys; m = sys.modules[__name__]
 
    >>> m.MEM[0x07] = 15
    >>> executar('LOAD', 0x07, DIRETO)
    >>> m.AC
    15
 
    >>> m.AC = 20
    >>> executar('STOR', 0x08, DIRETO)
    >>> m.MEM[0x08]
    20
 
    >>> m.AC = 10
    >>> m.MEM[0x05] = 4
    >>> executar('ADD', 0x05, DIRETO)
    >>> m.AC
    14
 
    >>> m.AC = 10
    >>> executar('SUB', 3, IMEDIATO)
    >>> m.AC
    7
 
    >>> m.AC = 6
    >>> executar('MULT', 7, IMEDIATO)
    >>> m.AC
    42
 
    >>> m.AC = 7
    >>> executar('DIV', 2, IMEDIATO)
    >>> m.AC
    3
    >>> m.R
    1
 
    >>> m.AC = -7
    >>> executar('DIV', 2, IMEDIATO)
    >>> m.AC
    -3
    >>> m.R
    -1
 
    >>> executar('DIV', 0, IMEDIATO)
    Erro: divisao por zero!
 
    >>> executar('JUMP', 0xB5, DIRETO)
    >>> m.PC
    181
 
    >>> m.N = 0
    >>> m.PC = 0
    >>> executar('JUMP+', 0x10, DIRETO)
    >>> m.PC
    16
 
    >>> m.N = 1
    >>> m.PC = 5
    >>> executar('JUMP+', 0x10, DIRETO)
    >>> m.PC
    5
 
    >>> m.MEM[0x20] = 0x30
    >>> m.MEM[0x30] = 99
    >>> executar('LOADI', 0x20, DIRETO)
    >>> m.AC
    99
 
    >>> m.AC = 55
    >>> m.MEM[0x21] = 0x40
    >>> executar('STORI', 0x21, DIRETO)
    >>> m.MEM[0x40]
    55
 
    >>> m.AC = MAX_INT
    >>> executar('ADD', 1, IMEDIATO)
    >>> m.C
    True
 
    >>> executar('XYZ', None, None)
    Opcode invalido: XYZ
    '''

    global AC, M, R, C, N, Z, PC, MAR, MBR

    if opcode == 'LOAD':
        # Carrega operando no AC
        AC = buscar_valor(operando, modo)
        atualizar_flags(AC)

    elif opcode == 'STOR':
        # Armazena AC na posicao de memoria indicada (sempre direto)
        # Armazena AC na posicao de memoria indicada (sempre direto)
        MAR = operando
        MBR = AC
        MEM[MAR] = MBR


    elif opcode == 'ADD':
        valor = buscar_valor(operando, modo)
        resultado = AC + valor
        C = verificar_overflow(resultado)
        AC = resultado
        atualizar_flags(AC)

    elif opcode == 'SUB':
        valor = buscar_valor(operando, modo)
        resultado = AC - valor
        C = verificar_overflow(resultado)
        AC = resultado
        atualizar_flags(AC)

    elif opcode == 'MULT':
        valor = buscar_valor(operando, modo)
        M = valor
        resultado = AC * M
        C = verificar_overflow(resultado)
        AC = resultado
        atualizar_flags(AC)

    elif opcode == 'DIV':
        valor = buscar_valor(operando, modo)
        if valor == 0:
            raise ValueError('Divisao por zero!')
        else:
            # Divisao inteira truncada (trunca em direcao ao zero),
            # em vez do // do Python que arredonda para baixo.
            quociente = abs(AC) // abs(valor)
            if (AC < 0) != (valor < 0):
                quociente = -quociente
            resto = AC - (quociente * valor) 
            AC = quociente
            R  = resto
            atualizar_flags(AC)

    elif opcode == 'JUMP':
        # Desvio incondicional: PC recebe o operando
        PC = operando

    elif opcode == 'JUMP+':
        # Desvio condicional: salta se AC >= 0 (N == 0)
        if N == 0:
            PC = operando
    elif opcode == 'JUMPZ':
        # Desvio condicional: salta se AC == 0 (Z == 1)
        if Z == 1:
            PC = operando

    elif opcode == 'LOADI':
        # Enderecamento indireto: operando aponta para celula que contem o endereco final
        MAR = operando
        MBR = MEM[MAR]   # MBR = endereco intermediario
        MAR = MBR
        MBR = MEM[MAR]   # MBR = valor final
        AC  = MBR
        atualizar_flags(AC)

    elif opcode == 'STORI':
        # Enderecamento indireto para escrita
        MAR = operando
        MBR = MEM[MAR]   # MBR = endereco intermediario
        MAR = MBR        # MAR = endereco final
        MBR = AC         # MBR = valor a ser armazenado
        MEM[MAR] = MBR   # armazena no endereco apontado
 
    else:
        print('Opcode invalido: ' + opcode)

# OPERACOES DE SUPORTE

def carregar_arquivo(arquivo):
    '''
    Le o arquivo e carrega dados e instrucoes no vetor MEM.
    Formato esperado:
      - Linhas de dados (inteiros) antes do endereco inicial
      - Uma linha com o endereco inicial (ex: 0xA0)
      - Linhas de instrucoes a partir do endereco inicial
    Comentarios comecam com # e sao ignorados. Linhas vazias sao ignoradas.

    >>> import tempfile, os, sys
    >>> m = sys.modules[__name__]
    >>> conteudo = "5\\n1\\n0xA0\\nLOAD M(0x07)\\n"
    >>> f = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
    >>> _ = f.write(conteudo)
    >>> f.close()
    >>> carregar_arquivo(f.name)
    [Parser] 2 dados carregados a partir de 0x00
    [Parser] 1 instrucoes carregadas a partir de 0xA0
    [Parser] PC inicial = 0xA0
    True
    >>> m.MEM[0]
    5
    >>> m.MEM[1]
    1
    >>> m.MEM[0xA0]
    'LOAD M(0x07)'
    >>> m.PC
    160
    >>> os.remove(f.name)
 
    >>> carregar_arquivo("arquivo_que_nao_existe.txt")
    Erro: Arquivo arquivo_que_nao_existe.txt nao encontrado!
    False
    '''

    global PC

    try:
        with open(arquivo, 'r') as arq:
            linhas = arq.readlines()
    except IOError:
        print('Erro: Arquivo ' + arquivo + ' nao encontrado!')
        return False

    # Remove comentarios e espacos
    linhas_limpas = []
    for l in linhas:
        sem_comentario = l.split('#')[0]
        sem_espaco = sem_comentario.strip()
        linhas_limpas.append(sem_espaco)

    # Remove linhas vazias
    linhas_finais = []
    for l in linhas_limpas:
        if l:
            linhas_finais.append(l)

    # Encontra o endereco inicial (primeira linha que comeca com 0x ou 0X)
    end_inicial = None
    ind_inicio_instrucao = None

    ind_inicio_instrucao = None
    for i in range(len(linhas_finais)):
        if not eh_numero(linhas_finais[i]):
            ind_inicio_instrucao = i
            break
 
    if ind_inicio_instrucao is None or ind_inicio_instrucao == 0:
        print('Erro: Nao foi encontrado um endereco inicial no arquivo!')
        return False
 
    # O endereco inicial e a linha numerica IMEDIATAMENTE ANTES da primeira
    linha_endereco = linhas_finais[ind_inicio_instrucao - 1]
    if linha_endereco.lower().startswith('0x'):
        end_inicial = int(linha_endereco, 16)
    else:
        end_inicial = int(linha_endereco)

    # Carrega dados em MEM[0], MEM[1], ...
    dados = linhas_finais[:ind_inicio_instrucao - 1]
    for i in range(len(dados)):
        valor = dados[i]
        if valor.lower().startswith('0x'):
            MEM[i] = int(valor, 16)
        else:
            MEM[i] = int(valor)

    # Carrega instrucoes a partir do endereco inicial
    instrucoes = linhas_finais[ind_inicio_instrucao:]
    for i in range(len(instrucoes)):
        MEM[end_inicial + i] = instrucoes[i]

    PC = end_inicial

    print('[Parser] ' + str(len(dados)) + ' dados carregados a partir de 0x00')
    print('[Parser] ' + str(len(instrucoes)) + ' instrucoes carregadas a partir de 0x' + format(end_inicial, '02X'))
    print('[Parser] PC inicial = 0x' + format(PC, '02X'))
    return True


def mostrar_registradores():
    '''Exibe o estado atual de todos os registradores
 
    >>> import sys; m = sys.modules[__name__]
    >>> m.PC=0xA1; m.IR="LOAD M(0x07)"; m.MAR=0x07; m.MBR=0
    >>> m.AC=0; m.M=None; m.R=None; m.C=None; m.N=0; m.Z=1
    >>> mostrar_registradores()
    ==================== Registradores ====================
     PC  = 0xA1          IR  = LOAD M(0x07)
     MAR = 0x07          MBR = 0
     AC  = 0             M   = None
     R   = None          C   = None
     N   = 0             Z   = 1
    =======================================================
    <BLANKLINE>
    '''
    if MAR is not None:
        mar_str = '0x' + format(MAR, '02X')
    else:
        mar_str = 'None'

    LARGURA = 14

    print('==================== Registradores ====================')
    print(' PC  = ' + ('0x' + format(PC, '02X')).ljust(LARGURA) + 'IR  = ' + str(IR))
    print(' MAR = ' + mar_str.ljust(LARGURA)                    + 'MBR = ' + str(MBR))
    print(' AC  = ' + str(AC).ljust(LARGURA)                    + 'M   = ' + str(M))
    print(' R   = ' + str(R).ljust(LARGURA)                     + 'C   = ' + str(C))
    print(' N   = ' + str(N).ljust(LARGURA)                     + 'Z   = ' + str(Z))
    print('=======================================================\n')


def ciclo_de_busca():
    '''Realiza o ciclo de busca: 
    MAR<-PC, 
    MBR<-MEM[MAR], 
    IR<-MBR, 
    PC<-PC+1
 
    >>> import sys; m = sys.modules[__name__]
    >>> m.PC = 0xA0
    >>> m.MEM[0xA0] = "LOAD M(0x07)"
    >>> ciclo_de_busca()
    >>> m.MAR
    160
    >>> m.MBR
    'LOAD M(0x07)'
    >>> m.IR
    'LOAD M(0x07)'
    >>> m.PC
    161
    '''
    global PC, IR, MAR, MBR

    MAR = PC
    MBR = MEM[MAR]
    IR  = MBR
    PC  = PC + 1

# LACO PRINCIPAL

def main():
    '''Laco principal do simulador: pede o arquivo, carrega o programa e
    executa instrucao por instrucao ate o fim, mostrando os registradores
    a cada passo (pausando em ENTER).
 
    Nao possui doctest: depende de input() interativo e de um arquivo real
    no disco. Testado manualmente executando `python3 ciclo.py`.
    '''
    
    arquivo = input('Qual arquivo a ser executado?\n>>> ')
    if not carregar_arquivo(arquivo):
        return

    print('\nEstado Inicial (antes das instrucoes):')
    mostrar_registradores()

    while True:
        # Para se PC sair do intervalo valido ou apont ar para area sem instrucao
        if PC < 0 or PC > 0xFF:
            print('Fim do programa (PC fora do intervalo).')
            break
        if MEM[PC] is None:
            print('Fim do programa (posicao vazia em 0x' + format(PC, '02X') + ').')
            break
        if not isinstance(MEM[PC], str):
            print('Fim do programa (dado em lugar de instrucao em 0x' + format(PC, '02X') + ').')
            break

        ciclo_de_busca()

        opcode, operando, modo = decodificar(IR)
        executar(opcode, operando, modo)

        mostrar_registradores()
        input('Pressione ENTER para continuar...')


if __name__ == '__main__':
    main()
