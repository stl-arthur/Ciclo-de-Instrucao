
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

def determinar_modo(operando_str):
    '''Determina o modo de enderecamento a partir da string do operando'''
    if operando_str[0] == 'M':
        return DIRETO
    elif operando_str[0] == '#':
        return IMEDIATO
    else:
        print('Modo invalido: ' + operando_str)
        return None

def buscar_valor(operando, modo):
    '''Busca o valor do operando conforme o modo de enderecamento'''
    global MAR, MBR

    if modo == IMEDIATO:
        return operando       # valor literal, sem acesso a memoria
    else:
        MAR = operando        # MAR recebe o endereco
        MBR = MEM[MAR]        # MBR recebe o valor armazenado
        return MBR

def atualizar_flags(valor):
    '''Atualiza as flags N e Z conforme o valor resultante'''
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
    '''Retorna True se houve overflow, False caso contrario'''
    if resultado > MAX_INT or resultado < MIN_INT:
        return True
    return False

# ======================== DECODE / EXECUTE ========================

def decodificar(IR):
    '''Decodifica a instrucao do IR em opcode, operando e modo'''
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
    '''Executa a instrucao decodificada'''
    global AC, M, R, C, N, Z, PC, MAR, MBR

    if opcode == 'LOAD':
        # Carrega operando no AC
        AC = buscar_valor(operando, modo)
        atualizar_flags(AC)

    elif opcode == 'STOR':
        # Armazena AC na posicao de memoria indicada (sempre direto)
        MEM[operando] = AC

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
        R = AC % valor     # resto
        AC = AC // valor   # quociente
        atualizar_flags(AC)

    elif opcode == 'JUMP':
        # Desvio incondicional: PC recebe o operando
        PC = operando

    elif opcode == 'JUMP+':
        # Desvio condicional: salta se AC >= 0 (N == 0)
        if N == 0:
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
        MEM[MBR] = AC    # armazena AC no endereco apontado

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
        sem_espaco     = sem_comentario.strip()
        linhas_limpas.append(sem_espaco)

    # Remove linhas vazias
    linhas_finais = []
    for l in linhas_limpas:
        if l:
            linhas_finais.append(l)

    # Encontra o endereco inicial (primeira linha que comeca com 0x ou 0X)
    end_inicial = None
    ind_inicio_instrucao = None

    for i in range(len(linhas_finais)):
        linha = linhas_finais[i]
        if linha.startswith('0x') or linha.startswith('0X'):
            end_inicial = int(linha, 16)
            ind_inicio_instrucao = i + 1
            break

    if end_inicial is None:
        print('Erro: Nao foi encontrado um endereco inicial no arquivo!')
        return False

    # Carrega dados em MEM[0], MEM[1], ...
    dados = linhas_finais[:ind_inicio_instrucao - 1]
    for i in range(len(dados)):
        MEM[i] = int(dados[i])

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
    '''Exibe o estado atual de todos os registradores'''
    if MAR is not None:
        mar_str = '0x' + format(MAR, '02X')
    else:
        mar_str = 'None'

    print('==================== Registradores ====================')
    print(' PC  = 0x' + format(PC, '02X') + '    IR  = ' + str(IR))
    print(' MAR = ' + mar_str + '    MBR = ' + str(MBR))
    print(' AC  = ' + str(AC) + '    M   = ' + str(M))
    print(' R   = ' + str(R)  + '    C   = ' + str(C))
    print(' N   = ' + str(N)  + '    Z   = ' + str(Z))
    print('=======================================================\n')


def ciclo_de_busca():
    '''Realiza o ciclo de busca: MAR<-PC, MBR<-MEM[MAR], IR<-MBR, PC<-PC+1'''
    global PC, IR, MAR, MBR

    MAR = PC
    MBR = MEM[MAR]
    IR  = MBR
    PC  = PC + 1

#LACO PRINCIPAL

def main():
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
