import socket
import threading
import tkinter as tk
from tkinter import messagebox

HOST = "0.0.0.0"
PORT = 5000

current_player = "X"
my_turn = True
conn = None

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
            data = conn.recv(1024).decode()
            index = int(data)

            buttons[index]["text"] = "O"
            my_turn = True

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

        except:
            messagebox.showerror("Error", "Client disconnected.")
            root.quit()
            break


# ---------------- BUTTON CLICK ----------------
def on_button_click(i):
    global my_turn, score_x, score_o, score_draw

    if not my_turn:
        return
    if buttons[i]["text"] != "":
        return

    buttons[i]["text"] = "X"
    conn.send(str(i).encode())
    my_turn = False

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
    my_turn = True
    for btn in buttons:
        btn["text"] = ""


# ---------------- AESTHETIC GUI ----------------
root = tk.Tk()
root.title("Tic Tac Toe - Server (Player X)")
root.geometry("900x700")
root.configure(bg="#d6e6f2")

title_label = tk.Label(
    root, text="Tic Tac Toe - Player X (Server)",
    font=("Poppins", 26, "bold"),
    bg="#d6e6f2", fg="#2b3a55"
)
title_label.pack(pady=10)

# -------- SCOREBOARD LABEL --------
scoreboard_label = tk.Label(
    root,
    text="X Wins: 0   |   O Wins: 0   |   Draws: 0",
    font=("Poppins", 20, "bold"),
    bg="#d6e6f2",
    fg="#2b3a55"
)
scoreboard_label.pack(pady=10)

frame = tk.Frame(root, bg="#d6e6f2")
frame.pack()

buttons = []
BTN_BG = "#ffffff"
BTN_ACTIVE = "#b8d8e3"
BTN_BORDER = "#9bbccc"

for i in range(9):
    btn = tk.Button(
        frame,
        text="",
        font=("Poppins", 32, "bold"),
        width=5,
        height=2,
        fg="#2b3a55",
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
    bg="#4c74af",
    activebackground="#678dc8",
    width=15,
    bd=0,
    relief="ridge",
    command=reset_board
)
reset_btn.pack(pady=25)


# ---------------- SOCKET SETUP ----------------
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(1)
print("Waiting for client...")

conn, addr = server.accept()
print("Connected:", addr)

threading.Thread(target=listen_for_moves, daemon=True).start()

root.mainloop()
