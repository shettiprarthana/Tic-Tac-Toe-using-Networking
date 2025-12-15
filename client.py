import socket
import threading
import tkinter as tk
from tkinter import messagebox

SERVER_IP = "SERVER IP ADDRESS"
PORT = 5000

current_player = "O"
my_turn = False
sock = None

# -------- SCOREBOARD --------
score_x = 0
score_o = 0
score_draw = 0

def update_scoreboard():
    scoreboard_label.config(
        text=f"X Wins: {score_x}   |   O Wins: {score_o}   |   Draws: {score_draw}"
    )


# ---------------- NETWORK RECEIVE THREAD ----------------
def listen_for_moves():
    global my_turn, score_x, score_o, score_draw

    while True:
        try:
            data = sock.recv(1024).decode()
            index = int(data)

            buttons[index]["text"] = "X"
            my_turn = True

            if check_winner():
                score_x += 1
                update_scoreboard()
                messagebox.showinfo("Game Over", "Player X wins!")
                reset_board()

            elif check_draw():
                score_draw += 1
                update_scoreboard()
                messagebox.showinfo("Game Over", "It's a draw!")
                reset_board()

        except:
            messagebox.showerror("Error", "Server disconnected.")
            root.quit()
            break


# ---------------- BUTTON CLICK ----------------
def on_button_click(i):
    global my_turn, score_x, score_o, score_draw

    if not my_turn:
        return
    if buttons[i]["text"] != "":
        return

    buttons[i]["text"] = "O"
    sock.send(str(i).encode())
    my_turn = False

    if check_winner():
        score_o += 1
        update_scoreboard()
        messagebox.showinfo("Game Over", "Player O wins!")
        reset_board()

    elif check_draw():
        score_draw += 1
        update_scoreboard()
        messagebox.showinfo("Game Over", "It's a draw!")
        reset_board()


# ---------------- GAME LOGIC ----------------
def check_winner():
    win_patterns = [
        (0, 1, 2), (3, 4, 5), (6, 7, 8),
        (0, 3, 6), (1, 4, 7), (2, 5, 8),
        (0, 4, 8), (2, 4, 6)
    ]
    for a, b, c in win_patterns:
        if buttons[a]["text"] != "" and buttons[a]["text"] == buttons[b]["text"] == buttons[c]["text"]:
            return True
    return False


def check_draw():
    return all(btn["text"] != "" for btn in buttons)


def reset_board():
    global my_turn
    my_turn = False
    for btn in buttons:
        btn["text"] = ""


# ---------------- BEAUTIFUL GUI ----------------
root = tk.Tk()
root.title("Tic Tac Toe - Client (Player O)")
root.geometry("900x700")
root.configure(bg="#fde2e4")

title_label = tk.Label(
    root, text="Tic Tac Toe - Player O (Client)",
    font=("Poppins", 26, "bold"),
    bg="#fde2e4", fg="#8a2846"
)
title_label.pack(pady=10)

# -------- SCOREBOARD LABEL --------
scoreboard_label = tk.Label(
    root,
    text="X Wins: 0   |   O Wins: 0   |   Draws: 0",
    font=("Poppins", 20, "bold"),
    bg="#fde2e4",
    fg="#8a2846"
)
scoreboard_label.pack(pady=10)

frame = tk.Frame(root, bg="#fde2e4")
frame.pack()

buttons = []
BTN_BG = "#ffffff"
BTN_ACTIVE = "#f7cad0"
BTN_BORDER = "#f4a6b8"

for i in range(9):
    btn = tk.Button(
        frame,
        text="",
        font=("Poppins", 32, "bold"),
        width=5,
        height=2,
        fg="#8a2846",
        bg=BTN_BG,
        activebackground=BTN_ACTIVE,
        bd=4,
        relief="ridge",
        highlightthickness=3,
        highlightbackground=BTN_BORDER,
        highlightcolor=BTN_BORDER,
        command=lambda i=i: on_button_click(i)
    )
    btn.grid(row=i // 3, column=i % 3, padx=12, pady=12)
    buttons.append(btn)

reset_btn = tk.Button(
    root, text="RESET BOARD",
    font=("Poppins", 18, "bold"),
    fg="#ffffff",
    bg="#d74d6a",
    activebackground="#f07c93",
    width=15,
    bd=0,
    relief="ridge",
    command=reset_board
)
reset_btn.pack(pady=25)


# ---------------- CONNECT ----------------
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((SERVER_IP, PORT))

threading.Thread(target=listen_for_moves, daemon=True).start()

root.mainloop()
