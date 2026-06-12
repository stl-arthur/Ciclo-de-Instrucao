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


def cicloInstrucao():
    MAR = PC
    MBR = MEM[MAR]
    IR = MBR
    PC += 1
    #executaInstrucao(IR)

def main():
    arquivo = input("Qual arquivo a ser trabalhado?\n>>> ")
    with open(arquivo, 'r') as arq:
        linha = arq.readline()
        print("linha:", linha)
        arq.close()
    print("testando git")


if __name__ == "__main__":
    main()
