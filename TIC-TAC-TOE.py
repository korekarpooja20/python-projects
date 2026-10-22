import tkinter as tk
from tkinter import messagebox
import random
import math

HUMAN = "X"
AI = "O"
EMPTY = ""

WIN_LINES = [
    (0, 1, 2), (3, 4, 5), (6, 7, 8),
    (0, 3, 6), (1, 4, 7), (2, 5, 8),
    (0, 4, 8), (2, 4, 6)
]


def winner(board):
    for line in WIN_LINES:
        a, b, c = line
        if board[a] and board[a] == board[b] == board[c]:
            return board[a], line

    if EMPTY not in board:
        return "DRAW", None

    return None, None


def available_moves(board):
    return [i for i, value in enumerate(board) if value == EMPTY]


def minimax(board, depth, alpha, beta, maximizing):
    result, _ = winner(board)

    if result == AI:
        return 10 - depth, None

    if result == HUMAN:
        return depth - 10, None

    if result == "DRAW":
        return 0, None

    best_move = None

    if maximizing:
        best_score = -math.inf

        for move in available_moves(board):
            board[move] = AI
            score, _ = minimax(
                board, depth + 1, alpha, beta, False
            )
            board[move] = EMPTY

            if score > best_score:
                best_score = score
                best_move = move

            alpha = max(alpha, best_score)

            if beta <= alpha:
                break

        return best_score, best_move

    else:
        best_score = math.inf

        for move in available_moves(board):
            board[move] = HUMAN
            score, _ = minimax(
                board, depth + 1, alpha, beta, True
            )
            board[move] = EMPTY

            if score < best_score:
                best_score = score
                best_move = move

            beta = min(beta, best_score)

            if beta <= alpha:
                break

        return best_score, best_move


class TicTacToeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Tic-Tac-Toe AI")
        self.root.resizable(False, False)
        self.root.configure(bg="#111827")

        self.board = [EMPTY] * 9
        self.human_score = 0
        self.ai_score = 0
        self.draw_score = 0
        self.mode = tk.StringVar(value="Human vs AI")
        self.difficulty = tk.StringVar(value="Impossible")
        self.game_over = False

        self.build_ui()
        self.refresh()

    def build_ui(self):
        tk.Label(
            self.root,
            text="TIC-TAC-TOE AI",
            font=("Arial", 22, "bold"),
            bg="#111827",
            fg="white"
        ).pack(pady=(15, 3))

        tk.Label(
            self.root,
            text="Minimax + Alpha-Beta Pruning",
            font=("Arial", 10),
            bg="#111827",
            fg="#9ca3af"
        ).pack(pady=(0, 12))

        options = tk.Frame(self.root, bg="#111827")
        options.pack()

        tk.Label(
            options, text="Mode:", bg="#111827", fg="white"
        ).grid(row=0, column=0, padx=5)

        mode_menu = tk.OptionMenu(
            options, self.mode,
            "Human vs AI",
            "Human vs Human",
            command=lambda _: self.new_game()
        )
        mode_menu.grid(row=0, column=1, padx=5)

        tk.Label(
            options, text="AI Level:", bg="#111827", fg="white"
        ).grid(row=0, column=2, padx=5)

        difficulty_menu = tk.OptionMenu(
            options, self.difficulty,
            "Easy", "Medium", "Impossible"
        )
        difficulty_menu.grid(row=0, column=3, padx=5)

        self.status = tk.Label(
            self.root,
            text="Your turn (X)",
            font=("Arial", 12, "bold"),
            bg="#111827",
            fg="#fbbf24",
            pady=10
        )
        self.status.pack()

        board_frame = tk.Frame(self.root, bg="#111827")
        board_frame.pack(padx=12, pady=5)

        self.buttons = []

        for i in range(9):
            button = tk.Button(
                board_frame,
                text="",
                font=("Arial", 28, "bold"),
                width=4,
                height=2,
                bg="#1f2937",
                fg="white",
                activebackground="#374151",
                relief="flat",
                command=lambda index=i: self.human_move(index)
            )
            button.grid(
                row=i // 3,
                column=i % 3,
                padx=4,
                pady=4
            )
            self.buttons.append(button)

        self.score_label = tk.Label(
            self.root,
            text="",
            font=("Arial", 11),
            bg="#111827",
            fg="#d1d5db"
        )
        self.score_label.pack(pady=10)

        controls = tk.Frame(self.root, bg="#111827")
        controls.pack(pady=(0, 12))

        tk.Button(
            controls,
            text="New Game",
            command=self.new_game,
            font=("Arial", 10, "bold"),
            bg="#2563eb",
            fg="white",
            relief="flat",
            padx=15,
            pady=7
        ).grid(row=0, column=0, padx=5)

        tk.Button(
            controls,
            text="Reset Scores",
            command=self.reset_scores,
            font=("Arial", 10, "bold"),
            bg="#4b5563",
            fg="white",
            relief="flat",
            padx=15,
            pady=7
        ).grid(row=0, column=1, padx=5)

    def refresh(self, winning_line=None):
        for i, button in enumerate(self.buttons):
            value = self.board[i]
            color = "#1f2937"
            text_color = "white"

            if value == HUMAN:
                text_color = "#60a5fa"
            elif value == AI:
                text_color = "#f87171"

            if winning_line and i in winning_line:
                color = "#166534"
                text_color = "white"

            button.config(
                text=value,
                bg=color,
                fg=text_color,
                state="disabled" if value or self.game_over else "normal"
            )

        self.score_label.config(
            text=f"Player X: {self.human_score}   "
                 f"Player O / AI: {self.ai_score}   "
                 f"Draws: {self.draw_score}"
        )

    def human_move(self, index):
        if self.game_over or self.board[index] != EMPTY:
            return

        if self.mode.get() == "Human vs AI":
            self.board[index] = HUMAN
        else:
            self.board[index] = (
                HUMAN
                if self.board.count(HUMAN) == self.board.count(AI)
                else AI
            )

        self.refresh()

        if self.check_end():
            return

        if self.mode.get() == "Human vs AI":
            self.status.config(text="AI is thinking...")
            self.root.after(250, self.ai_move)
        else:
            self.status.config(
                text=f"Player {AI if self.board.count(HUMAN) > self.board.count(AI) else HUMAN}'s turn"
            )

    def ai_move(self):
        if self.game_over:
            return

        moves = available_moves(self.board)

        if not moves:
            return

        level = self.difficulty.get()

        if level == "Easy":
            move = random.choice(moves)

        elif level == "Medium":
            if random.random() < 0.35:
                move = random.choice(moves)
            else:
                _, move = minimax(
                    self.board, 0, -math.inf, math.inf, True
                )

        else:
            _, move = minimax(
                self.board, 0, -math.inf, math.inf, True
            )

        if move is not None:
            self.board[move] = AI

        self.refresh()

        if not self.check_end():
            self.status.config(text="Your turn (X)")

    def check_end(self):
        result, line = winner(self.board)

        if result is None:
            return False

        self.game_over = True

        if result == HUMAN:
            self.human_score += 1
            self.status.config(text="Player X wins!", fg="#86efac")

        elif result == AI:
            self.ai_score += 1

            message = (
                "Player O wins!"
                if self.mode.get() == "Human vs Human"
                else "AI wins!"
            )

            self.status.config(text=message, fg="#fca5a5")

        else:
            self.draw_score += 1
            self.status.config(text="It's a draw!", fg="#fbbf24")

        self.refresh(winning_line=line)
        return True

    def new_game(self):
        self.board = [EMPTY] * 9
        self.game_over = False
        self.status.config(fg="#fbbf24", text="Your turn (X)")
        self.refresh()

    def reset_scores(self):
        self.human_score = 0
        self.ai_score = 0
        self.draw_score = 0
        self.new_game()


if __name__ == "__main__":
    root = tk.Tk()
    app = TicTacToeApp(root)
    root.mainloop()
