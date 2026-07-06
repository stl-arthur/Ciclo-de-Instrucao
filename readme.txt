AVALIAÇÃO 3 - SIMULAÇÃO DO CICLO DE INSTRUÇÃO (IAS)
Arquitetura e Organização de Computadores - Prof. Rodrigo Calvo

Aluno: Arthur Henrique da Silva Ra: 14
Aluna: Cintia da Silva Bulcão   Ra: 145107
Aluna: Giovana da Silva Bulcão  Ra: 144325

------------------------------------------------------------
ARQUIVOS
------------------------------------------------------------
- ciclo.py                  -> simulador do ciclo de instrução do IAS
- selection.txt             -> Selection Sort (algoritmo 1), corrigido
                                para caber na memória de 256 posições
- crivoEratostenes.txt      -> Crivo de Eratóstenes (algoritmo 2)
- readme.txt                -> relatório técnico do projeto

------------------------------------------------------------
COMO EXECUTAR
------------------------------------------------------------
1. Abra um terminal na pasta que contém ciclo.py e os arquivos .txt.
2. Execute:

       python3 ciclo.py

3. Quando solicitado, informe o nome do arquivo de entrada, por
   exemplo:

       Qual arquivo a ser executado?
       >>> selection.txt

   ou

       >>> crivoEratostenes.txt

4. O simulador exibirá o estado inicial dos registradores e, a cada
   tecla ENTER pressionada, executará e mostrará o resultado de uma
   instrução do programa, até o fim da execução.

------------------------------------------------------------
OBSERVAÇÃO SOBRE O ARQUIVO selection.txt
------------------------------------------------------------
O arquivo selection.txt original (fornecido no enunciado) usava
endereços de memória de 0x100 a 0x131, fora do intervalo válido do
simulador (0x00 a 0xFF, memória de 256 posições), e por isso não
podia ser executado. O novo arquivo selection.txt reorganiza os
mesmos dados e o mesmo algoritmo dentro do intervalo válido de
memória, além de corrigir dois desvios (JUMP+) que apontavam para
instruções incorretas no arquivo original. Os detalhes de cada
correção estão descritos na seção 4.1 do relatório técnico.