import tkinter as tk
from tkinter import messagebox
import random
import math

# Класс для узла дерева данных, отображающего ход поиска
class TreeNode:
    def __init__(self, depth, move=None, sequence=None, human_score=0, computer_score=0, turn="", value=None):
        self.depth = depth          # текущая глубина узла
        self.move = move            # ход, приведший к этому состоянию (индекс объединяемой пары)
        self.sequence = sequence    # состояние последовательности в этом узле
        self.human_score = human_score
        self.computer_score = computer_score
        self.turn = turn            # чей ход в этом состоянии ("human" или "computer")
        self.value = value          # вычисленное значение (эвристика)
        self.children = []          # список кортежей: (ход, дочерний узел)

# Основной класс игры
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
        
        # Игровые переменные
        self.sequence = []
        self.human_score = 0
        self.computer_score = 0
        self.turn = "human"  # текущий ход: "human" или "computer"
        self.first_selection = None  # для хранения первого выбранного индекса при ходе человека
        self.search_tree = None      # для хранения дерева данных (результат поиска компьютера)
        
        # Игровой фрейм (отображение последовательности, очков и кнопок)
        self.game_frame = tk.Frame(master)
        
        # Фрейм для отображения последовательности – каждый элемент как кнопка
        self.sequence_frame = tk.Frame(self.game_frame)
        self.sequence_frame.pack(pady=10)
        
        # Метка для вывода информации об очках и текущем ходе
        self.score_label = tk.Label(self.game_frame, text="")
        self.score_label.pack(pady=10)
        
        # Кнопка для перезапуска игры после завершения
        self.restart_button = tk.Button(self.game_frame, text="Начать заново", command=self.restart_game)
        
        # Кнопка для отображения дерева данных (поиск), изначально неактивна
        self.tree_button = tk.Button(self.game_frame, text="Показать дерево данных", command=self.show_tree, state="disabled")
        self.tree_button.pack(pady=5)

    def start_game(self):
        # Инициализация состояния игры согласно выбранным параметрам
        length = self.seq_length.get()
        self.sequence = [random.randint(1, 9) for _ in range(length)]
        self.human_score = 0
        self.computer_score = 0
        self.first_selection = None
        self.search_tree = None

    # обнуляем дерево данных
        self.turn = self.start_choice.get()
        
        # Отображаем игровой фрейм, скрывая настройки
        self.settings_frame.pack_forget()
        self.game_frame.pack()
        self.update_display()
        
        # Если начинает компьютер, запускаем его ход
        if self.turn == "computer":
            self.master.after(500, self.computer_move)

    def update_display(self):
        # Обновление отображения последовательности
        for widget in self.sequence_frame.winfo_children():
            widget.destroy()
        
        for i, num in enumerate(self.sequence):
            btn = tk.Button(self.sequence_frame, text=str(num), command=lambda i=i: self.human_select(i), width=4)
            btn.grid(row=0, column=i, padx=2)
        
        self.score_label.config(text=f"Очки Человека: {self.human_score}   Очки Компьютера: {self.computer_score}\nТекущий ход: {self.turn}")
        
        # Если дерево данных сформировано, делаем кнопку активной
        if self.search_tree is not None:
            self.tree_button.config(state="normal")
        else:
            self.tree_button.config(state="disabled")

    def human_select(self, index):
        # Если сейчас не ход человека, игнорируем нажатие
        if self.turn != "human":
            return
        
        if self.first_selection is None:
            self.first_selection = index
        else:
            # Проверяем, что выбранные индексы соседние
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
                # Если не соседние – сбрасываем выбор
                self.first_selection = None

    def make_move(self, index1, index2, player):
        # Гарантируем, что index1 меньше index2
        if index2 < index1:
            index1, index2 = index2, index1
        a = self.sequence[index1]
        b = self.sequence[index2]
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
        else:  # s == 7
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

    # Эвристическая функция: оцениваем состояние как разность очков (с точки зрения компьютера)
    def heuristic(self, sequence, human_score, computer_score):
        return computer_score - human_score

    def generate_moves(self, sequence):
        return list(range(len(sequence) - 1))

    # Рекурсивная функция для преобразования дерева данных в строку с отступами
    def tree_to_string(self, node, indent=0):
        s = " " * indent
        s += f"Depth: {node.depth}, Turn: {node.turn}, Seq: {node.sequence}, Score: (human: {node.human_score}, comp: {node.computer_score}), Value: {node.value}\n"
        for move, child in node.children:
            s += " " * (indent + 2) + f"Move: {move}\n"
            s += self.tree_to_string(child, indent + 4)
        return s

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

    # Модифицированный minimax с построением дерева данных
    def minimax(self, sequence, human_score, computer_score, turn, depth, max_depth):
        node = TreeNode(depth, sequence=sequence, human_score=human_score, computer_score=computer_score, turn=turn)
        if len(sequence) == 1 or depth == max_depth:
            node.value = self.heuristic(sequence, human_score, computer_score)
            return node.value, None, node
        
        moves = self.generate_moves(sequence)
        if turn == "computer":
            best_val = -math.inf
            best_move = None
            for move in moves:
                new_seq, new_human, new_computer = self.simulate_move(sequence, human_score, computer_score, move, turn)
                child_val, _, child_node = self.minimax(new_seq, new_human, new_computer, "human", depth + 1, max_depth)
                node.children.append((move, child_node))
                if child_val > best_val:
                    best_val = child_val
                    best_move = move
            node.value = best_val
            return best_val, best_move, node
        else:
            best_val = math.inf
            best_move = None
            for move in moves:
                new_seq, new_human, new_computer = self.simulate_move(sequence, human_score, computer_score, move, turn)
                child_val, _, child_node = self.minimax(new_seq, new_human, new_computer, "computer", depth + 1, max_depth)
                node.children.append((move, child_node))
                if child_val < best_val:
                    best_val = child_val
                    best_move = move
            node.value = best_val
            return best_val, best_move, node

    # Модифицированный alfa-beta с построением дерева данных
    def alphabeta(self, sequence, human_score, computer_score, turn, depth, max_depth, alpha, beta):
        node = TreeNode(depth, sequence=sequence, human_score=human_score, computer_score=computer_score, turn=turn)
        if len(sequence) == 1 or depth == max_depth:
            node.value = self.heuristic(sequence, human_score, computer_score)
            return node.value, None, node
        
        moves = self.generate_moves(sequence)
        best_move = None
        if turn == "computer":
            value = -math.inf
            for move in moves:
                new_seq, new_human, new_computer = self.simulate_move(sequence, human_score, computer_score, move, turn)
                child_val, _, child_node = self.alphabeta(new_seq, new_human, new_computer, "human", depth + 1, max_depth, alpha, beta)
                node.children.append((move, child_node))
                if child_val > value:
                    value = child_val
                    best_move = move
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
            node.value = value
            return value, best_move, node
        else:
            value = math.inf
            for move in moves:
                new_seq, new_human, new_computer = self.simulate_move(sequence, human_score, computer_score, move, turn)
                child_val, _, child_node = self.alphabeta(new_seq, new_human, new_computer, "computer", depth + 1, max_depth, alpha, beta)
                node.children.append((move, child_node))
                if child_val < value:
                    value = child_val
                    best_move = move
                beta = min(beta, value)
                if beta <= alpha:
                    break

                node.value = value
            return value, best_move, node

    # Симуляция хода для вычисления нового состояния игры без изменения основного состояния
    def simulate_move(self, sequence, human_score, computer_score, move, turn):
        new_sequence = sequence[:]  # копия состояния
        a = new_sequence[move]
        b = new_sequence[move + 1]
        s = a + b
        if s > 7:
            new_val = 1
            if turn == "computer":
                computer_score += 1
            else:
                human_score += 1
        elif s < 7:
            new_val = 3
            if turn == "computer":
                human_score -= 1
            else:
                computer_score -= 1
        else:  # s == 7
            new_val = 2
            human_score += 1
            computer_score += 1
        new_sequence = new_sequence[:move] + [new_val] + new_sequence[move+2:]
        return new_sequence, human_score, computer_score

    def computer_move(self):
        max_depth = 4  # ограничение глубины поиска
        if self.algorithm_choice.get() == "minimax":
            _, best_move, tree = self.minimax(self.sequence, self.human_score, self.computer_score, "computer", 0, max_depth)
        else:
            _, best_move, tree = self.alphabeta(self.sequence, self.human_score, self.computer_score, "computer", 0, max_depth, -math.inf, math.inf)
        
        # Сохраняем дерево данных для последующего отображения
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

if __name__ == "__main__":
    root = tk.Tk()
    game = Game(root)
    root.mainloop()