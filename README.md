# Mini-8 — Processador didático de 8 bits

**CPU uniciclo com ISA própria, datapath, matriz de controle e simulação funcional.**

**Autores:** Ezequias Ferreira e Marcelo Barbosa  
**Disciplina:** Arquitetura e Organização de Computadores — PPCA/UFRR  
**Professor:** Herbert Oliveira Rocha · **Data:** 03/11/2026

> **Validação:** o modelo funcional Python passou nos testes previstos. O VHDL é uma implementação proposta, cuja compilação/simulação no GHDL ainda precisa ser confirmada. Este projeto não é compatível binariamente com a ISA MIPS de 32 bits.

## Proposta

Projetar um processador didático com instruções e dados de 8 bits, explicitando as escolhas e limitações arquiteturais. A entrega está organizada em três frentes: **datapath**, **matriz de controle** e **simulação**.

| Recurso | Mini-8 |
|---|---|
| Formato de instrução | `opcode[7:6] · A[5:3] · B[2:0]` |
| Registradores | R0–R7, 8 bits; R0 é zero constante |
| Memórias | ROM 256 × 8 bits; RAM 256 × 8 bits |
| PC | 8 bits; incremento de 1 por instrução |
| Execução | Uniciclo, sem pipeline |
| Desvio | Imediato de 3 bits, complemento de dois (−4 a +3) |

## ISA

| Opcode | Instrução | Efeito |
|---|---|---|
| `00` | `ADD Rd,Rs` | `Rd ← (Rd + Rs) mod 256` |
| `01` | `LD Rd,[Ra]` | `Rd ← RAM[Ra]` |
| `10` | `ST Rs,[Ra]` | `RAM[Ra] ← Rs` |
| `11` | `BEQZ Rn,off` | desvia se Rn = 0 |

Os campos A e B identificam registradores na maioria das instruções; em BEQZ, B é um deslocamento com sinal. **Exemplo:** `ADD R5,R2` → `00 010 101` = `0x15`.

## Execução do modelo Python

Pré-requisito: **Python 3.10+**, sem bibliotecas externas.

```bash
python -m unittest discover -s tests -v
python src/mini8.py examples/soma.asm --data examples/soma_data.json --steps 7
python src/mini8.py examples/laco.asm --data examples/laco_data.json --steps 18
```

O programa `soma` resulta em **5**; o programa `laco` resulta em **6**. A versão anterior do modelo aprovou 19 testes funcionais.

## Entregáveis

- **Datapath:** organização dos registradores, ULA, RAM, multiplexadores e controle do PC.
- **Matriz de controle:** valores de `BZero`, `EscReg`, `LerMem`, `EscMem`, `MemParaReg` e `DvC` para cada instrução.
- **Simulação:** assembler e CPU em Python, programas demonstrativos e testes.

## Status de verificação

| Etapa | Estado |
|---|---|
| Especificação da ISA e matriz | Documentadas |
| Modelo Python e testes funcionais | Testados |
| Validação do VHDL com GHDL | Pendente |
| Síntese em FPGA / temporização / consumo | Não realizada |

**Nota:** mini-ISA própria para fins educacionais; não executa código MIPS nativo.
