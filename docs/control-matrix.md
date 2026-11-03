# Matriz de controle — Mini-8

| Sinal | ADD | LD | ST | BEQZ |
|---|:---:|:---:|:---:|:---:|
| BZero | 0 | 1 | 1 | 1 |
| EscReg | 1 | 1 | 0 | 0 |
| LerMem | 0 | 1 | 0 | 0 |
| EscMem | 0 | 0 | 1 | 0 |
| MemParaReg | 0 | 1 | X | X |
| DvC | 0 | 0 | 0 | 1 |

- BZero: seleciona o valor de R[B] (0) ou zero (1) como segundo operando.
- EscReg: habilita escrita em R[B], mas o registrador R0 é imutável.
- LerMem / EscMem: habilitam leitura / escrita na RAM.
- MemParaReg: valor escrito vem da ULA (0) ou RAM (1).
- DvC: identifica BEQZ.
- Zero: sinal produzido pela ULA quando o resultado é zero.
- FontePC = DvC AND Zero.

**X** = indiferente porque EscReg=0.
**Observação:** esta é a matriz da ISA Mini-8, não a matriz MIPS original.
