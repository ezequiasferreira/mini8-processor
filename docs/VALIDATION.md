# Evidências e limitações de validação

## Modelo funcional

O simulador Python representa o estado do Mini-8 após cada borda ativa de clock. Ele permite verificar decodificação, soma módulo 256, RAM, desvio condicional e proteção de R0.

Execute:

\`\`\`sh
python -m unittest discover -s tests -v
python src/mini8.py examples/soma.asm --data examples/soma_data.json --steps 7
\`\`\`

Resultados esperados para soma: R4=5 e RAM[2]=5.

## Escopo ainda pendente

- As fontes e testbenches VHDL do pacote original ainda **não foram executados em GHDL** neste ambiente.
- Não foram efetuadas síntese física, validação em FPGA, nem medições de clock, potência ou área.
- Verificação funcional do modelo Python **não comprova equivalência RTL**.
