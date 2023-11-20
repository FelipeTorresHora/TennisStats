from funcoes_tenis import *

print("############ Estatisticas Tênis ############")
print("1 = Breaks Convertidos\n2 = Serviços ganhos\n3 = Aces\n4 = 1 Saque Porcentagem")
while True:
    ope = input ("Digite o número para visualizar a respectiva estatistica : ")
    if ope == "1":
        print(break_points_converted())
        break
    elif ope == "2":
        print(saques_vencidos())
        break
    elif ope == "3":
        print(aces())
        break
    elif ope == "4":
        print(primeiro_servico())
        break
    else:
        print("Operação Inválida")