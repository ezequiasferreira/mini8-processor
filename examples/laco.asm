; Soma 3+2+1=6 com contador decrescente.
; M[0]=1, M[1]=3 e M[3]=255 (representacao de -1 em 8 bits).
LD R1,[R0]
LD R2,[R1]
LD R3,[R2]
laco: BEQZ R2,saida
ADD R4,R2
ADD R2,R3
BEQZ R0,laco
saida: ST R4,[R1]
fim: BEQZ R0,fim
