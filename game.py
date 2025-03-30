import tkinter as tk
from tkinter import messagebox
import random
from tree_node import TreeNode
from algorithms import minimax, alphabeta
from utils import simulate_move

class Game:
    def __init__(self, master):
        self.master = master
        self.master.title("Skaitļu spēle (Игра с числами)")

        # Фрейм настроек (выбор: кто начинает, алгоритм, длина последовательности)
        self.settings_frame = tk.Frame(master)
        self.settings_frame.pack(pady=10)

        # Выбор, кто начинает игру
        self.start_choice = tk.StringVar(value="human")
        tk.Label(self.settings_frame, text="Кто начинает игру?").pack()
        tk.Radiobutton(self.settings_frame, text="Человек", variable=self.start_choice, value="human").pack()
        tk.Radiobutton(self.settings_frame, text="Компьютер", variable=self.start_choice, value="computer").pack()

        # Выбор алгоритма для компьютера
        self.algorithm_choice = tk.StringVar(value="minimax")
        tk.Label(self.settings_frame, text="Какой алгоритм использовать?").pack()
        tk.Radiobutton(self.settings_frame, text="Minimax", variable=self.algorithm_choice, value="minimax").pack()
        tk.Radiobutton(self.settings_frame, text="Alpha-Beta", variable=self.algorithm_choice, value="alphabeta").pack()

        # Выбор длины последовательности (от 15 до 25)
        tk.Label(self.settings_frame, text="Выберите длину последовательности (15-25):").pack()
        self.seq_length = tk.IntVar(value=15)
        self.seq_length_spin = tk.Spinbox(self.settings_frame, from_=15, to=25, textvariable=self.seq_length)
        self.seq_length_spin.pack()

        # Кнопка начала игры
        tk.Button(self.settings_frame, text="Начать игру", command=self.start_game).pack(pady=10)

        self.sequence = []
        self.human_score = 0
        self.computer_score = 0
        self.turn = "human"
        self.first_selection = None
        self.search_tree = None

        self.game_frame = tk.Frame(master)
        self.sequence_frame = tk.Frame(self.game_frame)
        self.sequence_frame.pack(pady=10)
        self.score_label = tk.Label(self.game_frame, text="")
        self.score_label.pack(pady=10)
        self.restart_button = tk.Button(self.game_frame, text="Начать заново", command=self.restart_game)
        self.tree_button = tk.Button(self.game_frame, text="Показать дерево данных", command=self.show_tree, state="disabled")
        self.tree_button.pack(pady=5)

    def start_game(self):
        length = self.seq_length.get()
        self.sequence = [random.randint(1, 9) for _ in range(length)]
        self.human_score = 0
        self.computer_score = 0
        self.first_selection = None
        self.search_tree = None
        self.turn = self.start_choice.get()

        self.settings_frame.pack_forget()
        self.game_frame.pack()
        self.update_display()

        if self.turn == "computer":
            self.master.after(500, self.computer_move)

    def update_display(self):
        for widget in self.sequence_frame.winfo_children():
            widget.destroy()

        for i, num in enumerate(self.sequence):
            btn = tk.Button(self.sequence_frame, text=str(num), command=lambda i=i: self.human_select(i), width=4)
            btn.grid(row=0, column=i, padx=2)

        self.score_label.config(text=f"Очки Человека: {self.human_score}   Очки Компьютера: {self.computer_score}\nТекущий ход: {self.turn}")
        self.tree_button.config(state="normal" if self.search_tree else "disabled")

    def human_select(self, index):
        if self.turn != "human":
            return
        if self.first_selection is None:
            self.first_selection = index
        else:
            if abs(index - self.first_selection) == 1:
                self.make_move(self.first_selection, index, "human")
                self.first_selection = None
                if not self.is_game_over():
                    self.turn = "computer"
                    self.update_display()
                    self.master.after(500, self.computer_move)
                else:
                    self.end_game()
            else:
                self.first_selection = None

    def make_move(self, index1, index2, player):
        if index2 < index1:
            index1, index2 = index2, index1
        a, b = self.sequence[index1], self.sequence[index2]
        s = a + b
        if s > 7:
            new_val = 1
            if player == "human":
                self.human_score += 1
            else:
                self.computer_score += 1
        elif s < 7:
            new_val = 3
            if player == "human":
                self.computer_score -= 1
            else:
                self.human_score -= 1
        else:
            new_val = 2
            self.human_score += 1
            self.computer_score += 1
        self.sequence = self.sequence[:index1] + [new_val] + self.sequence[index2+1:]

    def is_game_over(self):
        return len(self.sequence) == 1

    def end_game(self):
        self.update_display()
        if self.human_score == self.computer_score:
            result = "Ничья!"
        elif self.human_score > self.computer_score:
            result = "Человек победил!"
        else:
            result = "Компьютер победил!"
        messagebox.showinfo("Конец игры", result)
        self.restart_button.pack(pady=10)

    def restart_game(self):
        self.game_frame.pack_forget()
        self.settings_frame.pack(pady=10)
        self.restart_button.pack_forget()

    def show_tree(self):
        if self.search_tree is None:
            messagebox.showinfo("Информация", "Дерево данных ещё не сформировано.")
            return
        tree_str = self.tree_to_string(self.search_tree)
        tree_window = tk.Toplevel(self.master)
        tree_window.title("Дерево данных")
        text = tk.Text(tree_window, wrap="none")
        text.insert("end", tree_str)
        text.pack(expand=True, fill="both")

    def tree_to_string(self, node, indent=0):
        s = " " * indent + f"Depth: {node.depth}, Turn: {node.turn}, Seq: {node.sequence}, Score: (human: {node.human_score}, comp: {node.computer_score}), Value: {node.value}\n"
        for move, child in node.children:
            s += " " * (indent + 2) + f"Move: {move}\n"
            s += self.tree_to_string(child, indent + 4)
        return s

    def computer_move(self):
        max_depth = 4
        if self.algorithm_choice.get() == "minimax":
            _, best_move, tree = minimax(self.sequence, self.human_score, self.computer_score, "computer", 0, max_depth)
        else:
            _, best_move, tree = alphabeta(self.sequence, self.human_score, self.computer_score, "computer", 0, max_depth, float('-inf'), float('inf'))
        self.search_tree = tree
        if best_move is not None:
            self.make_move(best_move, best_move + 1, "computer")
            if not self.is_game_over():
                self.turn = "human"
                self.update_display()
            else:
                self.end_game()
        else:
            self.end_game()