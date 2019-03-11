#!/usr/bin/python3

import time
import random 
# O metodo input() nao gosta muito das setas do teclado, entao estou usando window.getch() do curses
import curses 
import os
import signal
import sys

# Funcao para tratar o SIGINT e fazer com que o programa encerre graciosamente.
def signal_handler(sig, frame):
    endwin()
    print(chr(27) + "[2J")

    if os.name == "posix": # Desesconde cursor
        os.system('tput cnorm')
    print('SIGINT/SIGTERM received, exiting now...')
    sys.exit(0)

# Registra SIGINT e associa a signal_handler.
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# Linux aceita as sequencias ANSI por padrao, mas o windows precisa usar o modulo colorama
if os.name != "posix":
    from colorama import init
    init(convert=True) # Inicializa o modulo
else:
    os.system('tput civis') # Esconde cursor no linux para ficar mais bonitinho

def endwin():
    screen.erase()
    curses.nocbreak()
    curses.echo()
    screen.keypad(0)
    curses.endwin()
    return 0

# Move o cursor para uma posicao especifica.
def cursor_to(x, y): 
    print("\033[%d;%dH" % (x, y), end='')
    return 0

# Move o cursor em N linhas ou colunas para qualquer lado.
def move_cursor(direction, qtd): 
    if direction == "up":
        ch = 'A'
    elif direction == "down":
        ch = 'B'
    elif direction == "forward":
        ch = 'C'
    elif direction == "backward":
        ch = 'D'
    else:
        print("Invalid direction!")
        return 1
        
    print("\033[%d%c" % (qtd, ch),end='') 
    return 0


def set_table(deck, rows):
    for i in range(10): # Inicializa cada coluna como uma lista
        rows[i] = []

    # Distribui as cartas para cada coluna
    for i in range(0, 4):
        for j in range(0, 10):
            rows[j].append(deck.pop())

    for i in range(4):
        rows[i].append(deck.pop())

    return 0

# Funcao responsavel por imprimir a mesa com as cartas na tela. Uma bagunca mas funciona.
def print_table(rows, hidden, arrow, old_arrow):
    card_placeholder = "┌────┐\033[1B\033[6D|10 \u2660|\033[1B\033[6D|    |\033[1B\033[6D|    |\033[1B\033[6D└────┘"
    card_back = "┌────┐\033[1B\033[6D| /\ |\033[1B\033[6D| -- |\033[1B\033[6D| \/ |\033[1B\033[6D└────┘"

    card_bottom = "|    |\033[1B\033[6D|    |\033[1B\033[6D└────┘"

    card_back_top = "┌────┐\033[1B\033[6D| /\ |\033[1B\033[6D"
    card_back_bottom = "| -- |\033[1B\033[6D| \/ |\033[1B\033[6D└────┘"

    cursor_to(2, 8)

    for i in range(0,10):
        for j in range(0,len(rows[i])):
            if j < hidden[i]:
                print(card_back_top, end='')
                continue

            if arrow[0] == i and arrow[1] == j: # Imprime seta de selecao

                move_cursor("backward", 2)
                move_cursor("down", 1)

                print("->", end='')
                move_cursor("up", 1)

            # Apaga seta antiga.
            if old_arrow[0] == i and old_arrow[1] == j: 

                move_cursor("backward", 2)
                move_cursor("down", 1)
                
                print("  ", end='')
                move_cursor("up", 1)

            value = rows[i][j]
            if value == '10':
                card_top = "┌────┐\033[1B\033[6D|10 \u2660|\033[1B\033[6D"
            else:
                card_top = "┌────┐\033[1B\033[6D|{}  \u2660|\033[1B\033[6D".format(value)
            print(card_top, end='')

        print(card_bottom, end='')
        move_cursor("up", 2 + 2 * len(rows[i]))
        move_cursor("forward", 6)

    return 0


def check_arrow(rows, arrow, direction):
    if direction == "left":
        if arrow[0] > 0:
            return True
    elif direction == "right":
        if arrow[0] < 9:
            return True
    elif direction == "up":
        if arrow[1] > 0:
            return True
    elif direction == "down":
        if arrow[1] < len(rows[arrow[0]]) - 1:
            return True


    return False

# Verifica se a proxima carta na coluna faz parte da sequencia, para que possa ser selecionada tambem caso positivo.
def check_cards(row, arrow):
    current_card = row[arrow[0]][arrow[1]]
    next_card = row[arrow[0]][arrow[1]-1]

    try:
        if int(next_card) == int(current_card) + 1:
            return True
    except ValueError:
        if current_card == '10' and next_card == 'J':
            return True
        elif current_card == 'J' and next_card == 'Q':
            return True
        elif current_card == 'Q' and next_card == 'K':
            return True
        elif current_card == 'A' and next_card == '2':
            return True

    return False


def draw_cards(rows, deck, arrow):
    if len(deck) > 0:
        for i in range(10):
            rows[i].append(deck.pop())
        arrow[1] += 1

    return 0

# Limpa a tela.
def clear_screen():
    if os.name == "posix": 
        os.system('clear') 
    else:
        os.system('cls') 

# Inicializa e configura curses
screen = curses.initscr()
curses.cbreak()
curses.noecho()
screen.timeout(10)
screen.keypad(True)
screen.leaveok(0)


random.seed() # Inicializa o estado interno do gerador de numeros aleatorios com o tempo atual do sistema.


deck = 8 * ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"] # Cria o baralho.
rows = 10 * [None] # Cria as dez colunas.
hidden_cards = [4, 4, 4, 4, 3, 3, 3, 3, 3, 3] # Quantidade de cartas viradas para baixo em cada coluna.
arrow = [0, 4] # Posicao x e y da seta de selecao
old_arrow = [0, 0] # Coordenadas da seta na tela


# Embaralha o baralho de 5 a 8 vezes.
for i in range(random.randint(5,8)): 
    random.shuffle(deck)

# Distribui as cartass
set_table(deck, rows)

#Loop principal.
while True:
    char = screen.getch()
    if char == ord('q') or char == 27: # q ou ESC para sair. ESC tem um delay por algum motivo
        break
    elif char == curses.KEY_LEFT:
        if check_arrow(rows, arrow, "left"):
            old_arrow = arrow.copy()
            cursor_to(20, 30)
            arrow[0] -= 1
            arrow[1] = len(rows[arrow[0]]) - 1

    elif char == curses.KEY_UP:
        if check_arrow(rows, arrow, "up"):
            if check_cards(rows, arrow) and (len(rows[arrow[0]]) - hidden_cards[arrow[0]]) > 1:
                old_arrow = arrow.copy()
                arrow[1] -= 1
    elif char == curses.KEY_RIGHT:
        if check_arrow(rows, arrow, "right"):
            old_arrow = arrow.copy()
            arrow[0] += 1
            arrow[1] = len(rows[arrow[0]]) - 1

    elif char == curses.KEY_DOWN:
        if check_arrow(rows, arrow, "down"):
            old_arrow = arrow.copy()
            arrow[1] += 1
    elif char == ord('s'):
        if len(deck) > 0:
            old_arrow = arrow.copy()
            draw_cards(rows, deck, arrow)

    print_table(rows, hidden_cards, arrow, old_arrow)

endwin()

print(chr(27) + "[2J")
os.system('clear')

if os.name == "posix": # Desesconde cursor
    os.system('tput cnorm')
