# Trabalho da Diciplina de Arquidetura e Organização de Computadores I
====================================================================
SIMULADOR DE CICLO DE INSTRUCAO - ARQUITETURA IAS
Arquitetura e Organizacao de Computadores - Prof. Rodrigo Calvo
====================================================================

Alunos: Arthur Henrique da Silva, Cintia da Silva Bulcão e Giovana da Silva Bulcão

O presente trabalho tem como objetivo desenvolver um programa que simule o comportamento dos registradores de um processador 
em um ciclo de instrução ao executar uma sequência de comandos de linguagem de
máquina. O simulador desenvolvido deve executar operações básicas de linguagem de máquina,
como adição, subtração, divisão, multiplicação, transferência de dados, e desvio de fluxo. Todas as
instruções do algoritmo e os dados contidos nele devem estar armazenados em memória RAM. As
instruções devem ser armazenadas sequencialmente na RAM e em local distinto do armazenamento
de dados. 

--------------------------------------------------------------------
1. ARQUIVOS DO PROJETO
--------------------------------------------------------------------
- simulador.py       -> script principal do simulador
- mdc_input.txt       -> arquivo de entrada do algoritmo de MDC (Euclides)
- selection_sort_input.txt -> arquivo de entrada do Selection Sort
- relatorio_tecnico.docx   -> relatorio tecnico do projeto
- readme.txt          -> este arquivo
  
--------------------------------------------------------------------
3. COMO EXECUTAR
--------------------------------------------------------------------
1. Coloque o script principal (simulador.py) e os arquivos de entrada
   (mdc_input.txt e selection_sort_input.txt) na mesma pasta.

2. Abra um terminal nessa pasta.

3. Execute um dos comandos abaixo:

   Para o algoritmo de MDC (Euclides):
   > python simulador.py mdc_input.txt

   Para o algoritmo de Selection Sort:
   > python simulador.py selection_sort_input.txt

4. Antes da execucao da primeira instrucao, o simulador exibe o
   estado inicial dos registradores (somente o PC valido nesse
   momento).

5. Pressione <ENTER> a cada passo para avancar a execucao. A cada
   instrucao executada, o estado atualizado de todos os
   registradores (A, B, PC, IR, MAR, MBR, AC, M, R, C, N, Z) e
   exibido em tela.

6. A execucao termina automaticamente ao alcancar o fim do
   programa (rotulo FIM).

--------------------------------------------------------------------
4. FORMATO DO ARQUIVO DE ENTRADA
--------------------------------------------------------------------
Cada arquivo de entrada (.txt) e dividido em tres blocos:

  a) Secao de dados: valores iniciais de memoria, um por linha,
     podendo conter comentarios iniciados por "#". Cada linha
     ocupa um endereco de memoria, comecando em 0x00.

  b) Endereco inicial da primeira instrucao, em hexadecimal
     (0xA0 nos programas entregues).

  c) Secao de instrucoes, carregadas sequencialmente a partir
     desse endereco.

--------------------------------------------------------------------
5. RESULTADOS ESPERADOS
--------------------------------------------------------------------
- MDC: com a=48 e b=18, o resultado final e MDC = 6
  (armazenado nos enderecos 0x00 e 0x01 da memoria).

- Selection Sort: com o vetor de entrada [1, 0, 3, 7, 2, 8],
  o vetor de saida esperado e [0, 1, 2, 3, 7, 8].

====================================================================
