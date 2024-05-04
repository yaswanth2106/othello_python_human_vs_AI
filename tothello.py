import numpy as np
import math
import random
import tkinter as tk
from tkinter import messagebox

ROWS = 8
COLUMNS = 8
EMPTY = 0
PLAYER1 = 1
PLAYER2 = 2

class OthelloGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Othello (Reversi)")
        self.board = create_board()
        self.turn = PLAYER1
        self.create_widgets()
        self.update_board()

    def create_widgets(self):
        self.canvas = tk.Canvas(self.master, width=400, height=400, bg="green")
        self.canvas.pack()

        self.canvas.bind("<Button-1>", self.on_click)

        self.update_board()

    def on_click(self, event):
        col = event.x // 50
        row = event.y // 50
        self.make_move(row, col)

    def update_board(self):
        self.canvas.delete("pieces")
        for r in range(ROWS):
            for c in range(COLUMNS):
                x0, y0 = c * 50, r * 50
                x1, y1 = x0 + 50, y0 + 50
                color = "green" if (r + c) % 2 == 0 else "dark green"
                self.canvas.create_rectangle(x0, y0, x1, y1, fill=color, tag="board")

                if self.board[r][c] == PLAYER1:
                    self.canvas.create_oval(x0 + 5, y0 + 5, x1 - 5, y1 - 5, fill="black", tag="pieces")
                elif self.board[r][c] == PLAYER2:
                    self.canvas.create_oval(x0 + 5, y0 + 5, x1 - 5, y1 - 5, fill="white", tag="pieces")

    def make_move(self, row, col):
        if is_valid_move(self.board, row, col, self.turn):
            make_move(self.board, row, col, self.turn)
            self.update_board()
            if is_game_over(self.board):
                self.show_result()
            else:
                self.switch_turn()

    def switch_turn(self):
        self.turn = PLAYER1 if self.turn == PLAYER2 else PLAYER2
        if self.turn == PLAYER2:
            self.master.after(1000, self.make_ai_move)

    def make_ai_move(self):
        move, _ = ai_move(self.board, 5, -math.inf, math.inf, True)
        if move:
            self.make_move(move[0], move[1])
        else:
            print("No valid moves. Skipping AI's turn.")
            self.switch_turn()

    def show_result(self):
        count_player1, count_player2 = count_pieces(self.board)
        if count_player1 > count_player2:
            result = "Player 1 wins!"
        elif count_player1 < count_player2:
            result = "AI wins!"
        else:
            result = "It's a draw!"
        print(result)
        tk.messagebox.showinfo("Game Over", result)

def create_board():
    board = np.zeros((ROWS, COLUMNS), dtype=int)
    board[3][3] = PLAYER1
    board[3][4] = PLAYER2
    board[4][3] = PLAYER2
    board[4][4] = PLAYER1
    return board

def is_valid_move(board, row, col, player):
    if board[row][col] != EMPTY:
        return False
    other_player = PLAYER1 if player == PLAYER2 else PLAYER2
    directions = [(0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1)]
    for dr, dc in directions:
        r, c = row + dr, col + dc
        if 0 <= r < ROWS and 0 <= c < COLUMNS and board[r][c] == other_player:
            r += dr
            c += dc
            while 0 <= r < ROWS and 0 <= c < COLUMNS and board[r][c] == other_player:
                r += dr
                c += dc
            if 0 <= r < ROWS and 0 <= c < COLUMNS and board[r][c] == player:
                return True
    return False

def make_move(board, row, col, player):
    if not is_valid_move(board, row, col, player):
        return False
    board[row][col] = player
    other_player = PLAYER1 if player == PLAYER2 else PLAYER2
    directions = [(0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1)]
    for dr, dc in directions:
        r, c = row + dr, col + dc
        flipped = []
        while 0 <= r < ROWS and 0 <= c < COLUMNS and board[r][c] == other_player:
            flipped.append((r, c))
            r += dr
            c += dc
        if 0 <= r < ROWS and 0 <= c < COLUMNS and board[r][c] == player:
            for fr, fc in flipped:
                board[fr][fc] = player
    return True

def count_pieces(board):
    count_player1 = np.sum(board == PLAYER1)
    count_player2 = np.sum(board == PLAYER2)
    return count_player1, count_player2

def is_game_over(board):
    return (not any(is_valid_move(board, r, c, PLAYER1) or is_valid_move(board, r, c, PLAYER2) for r in range(ROWS) for c in range(COLUMNS)))

def evaluate_board(board, player):
    count_player1, count_player2 = count_pieces(board)
    if player == PLAYER1:
        return count_player1 - count_player2
    else:
        return count_player2 - count_player1

def ai_move(board, depth, alpha, beta, maximizing_player):
    valid_moves = [(r, c) for r in range(ROWS) for c in range(COLUMNS) if is_valid_move(board, r, c, PLAYER2 if maximizing_player else PLAYER1)]
    if depth == 0 or not valid_moves:
        return None, evaluate_board(board, PLAYER2)
    
    if maximizing_player:
        value = -math.inf
        best_move = random.choice(valid_moves)
        for move in valid_moves:
            temp_board = np.copy(board)
            make_move(temp_board, move[0], move[1], PLAYER2)
            new_score = ai_move(temp_board, depth-1, alpha, beta, False)[1]
            if new_score > value:
                value = new_score
                best_move = move
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return best_move, value
    else:
        value = math.inf
        best_move = random.choice(valid_moves)
        for move in valid_moves:
            temp_board = np.copy(board)
            make_move(temp_board, move[0], move[1], PLAYER1)
            new_score = ai_move(temp_board, depth-1, alpha, beta, True)[1]
            if new_score < value:
                value = new_score
                best_move = move
            beta = min(beta, value)
            if alpha >= beta:
                break
        return best_move, value

def main():
    root = tk.Tk()
    app = OthelloGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
