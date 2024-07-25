from func import *
# print("--------------------  Menu de Opções  --------------------")
# print("1. Aces média")
# print("2. Média de aces por partida")
# print("3. First Serve")
# print("4. Porcentagem de Primeiro serviço")
# print("5. Média Dupla Falta por jogo")
# print("6. Média de Segundo Serviço Ganhos")
# print("7. Porcentagem Serviços Ganhos")
# print("8. Sair")
# print()
while True:
    clear_screen()

    print("--------------------  Menu de Opções  --------------------")
    print("1. Aces média")
    print("2. Média de aces por partida")
    print("3. First Serve")
    print("4. Porcentagem de Primeiro serviço")
    print("5. Média Dupla Falta por jogo")
    print("6. Média de Segundo Serviço Ganhos")
    print("7. Porcentagem Serviços Ganhos")
    print("8. Sair")
    print()
    choice = int(input("Selecione um Número "))
    clear_screen()
    if choice == 1:
        aces_avg()
    elif choice == 2:
        aces()
    elif choice == 3:
        first_serve()
    elif choice == 4:
        first_serve_pct()
    elif choice == 5:
        double_fault()
    elif choice == 6:
        second_service()    
    elif choice == 7:
        servicewon()
    elif choice == 8:
        print("Saindo...")
        break
    else:
        print("Opção inválida. Por favor, selecione uma opção válida.")
    # except ValueError:
    #     print("Erro: Por favor, insira um número válido.")
    
    # input("\nPressione Enter para voltar ao menu principal...")