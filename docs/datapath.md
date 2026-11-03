# Datapath Mini-8

O diagrama em [assets/datapath.svg](../assets/datapath.svg) apresenta o fluxo conceitual da CPU.

1. O **PC** aponta para a posição na ROM.
2. A **ROM** entrega a instrução de 8 bits.
3. A **Unidade de Controle** interpreta os dois bits de opcode e produz sinais.
4. O **banco de registradores** fornece operandos identificados pelos campos A e B.
5. A **ULA** soma os operandos ou utiliza um operando zero para fornecer o endereço.
6. Em **LD**, o dado da RAM retorna ao registrador. Em **ST**, a RAM recebe o valor de R[B].
7. O **PC** avança uma posição, exceto quando BEQZ realiza o desvio.

**Nota de engenharia:** o diagrama ilustra as conexões funcionalmente relevantes, não todos os multiplexadores, sinais elétricos, portas, ou temporizações reais. Consulte a matriz de controle.
