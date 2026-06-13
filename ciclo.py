import execute_decode

# ==================== Vetor de Memória, Armazena os dados e instruções ====================
MEM = [None] * 256

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

        opcode, operando, modo = execute_decode.decodificar(IR)
        execute_decode.executar(opcode, operando, modo)

        mostraRegistradores()
        input("Pressione ENTER para continuar")

if __name__ == "__main__":
    main()
