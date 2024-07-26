from func import *

while True:

    print("--------------------  Menu de Opções  --------------------")
    print("1. Estatísticas de Aces")
    print("2. Porcentagem de Primeiro serviço")
    print("3. Porcentagem de Pontos Ganhos com Primeiro Saque")
    print("4. Média Dupla Falta por jogo")
    print("5. Média de Segundo Serviço Ganhos")
    print("6. Porcentagem Serviços Ganhos")
    print("7. Sair")
    print()
    choice = int(input("Selecione um Número: "))
    clear_screen()

    if choice == 1:
        clear_screen()
        print("1. Aces média por jogo")
        print("2. Média de aces por partida")
        print("3. Voltar Ao Menu Principal")
        sub_choice = input("Selecione uma subopção: ")
        
        if sub_choice == '1':
            aces_avg()
        elif sub_choice == '2':
            aces()
        elif sub_choice == '3':
            continue  
        else:
            print("Subopção inválida.")
    elif choice == 2:
        first_serve()
    elif choice == 3:
        first_serve_pct()
    elif choice == 4:
        double_fault()
    elif choice == 5:
        second_service()   
    elif choice == 6:
        servicewon()
    elif choice == 7:
        print("Saindo...")
        break
    else:
        print("Opção inválida. Por favor, selecione uma opção válida.")