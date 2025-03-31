import tkinter as tk
from tkinter import messagebox
import random
import math

# Datu koka mezgla klase, kas parāda meklēšanas progresu
class TreeNode:
    def __init__(self, depth, move=None, sequence=None, human_score=0, computer_score=0, turn="", value=None):
        self.depth = depth          # pašreizējais mezgla dziļums
        self.move = move            # gājiens, kas noveda pie šī stāvokļa (apvienotā pāra indekss)
        self.sequence = sequence    # šī mezgla secības stāvoklis
        self.human_score = human_score
        self.computer_score = computer_score
        self.turn = turn            # kura kārta ir šajā stāvoklī (“cilvēks” vai “dators”)
        self.value = value          # aprēķinātā vērtība (heiristisks)
        self.children = []          # tuples saraksts: (move, child mezgls)

# Spēles galvenā klase
class Game:
    def __init__(self, master):
        self.master = master
        self.master.title("Sequence game (Numbers game)")

        # Iestatījumu rāmis (atlase: kas sākas, algoritms, secības garums)
        self.settings_frame = tk.Frame(master)
        self.settings_frame.pack(pady=10)

        # Izvēlieties, kurš sāks spēli
        self.start_choice = tk.StringVar(value="human")
        tk.Label(self.settings_frame, text="Who starts the game?").pack()
        tk.Radiobutton(self.settings_frame, text="Human", variable=self.start_choice, value="human").pack()
        tk.Radiobutton(self.settings_frame, text="AI", variable=self.start_choice, value="computer").pack()

        # Datora algoritma izvēle
        self.algorithm_choice = tk.StringVar(value="minimax")
        tk.Label(self.settings_frame, text="Which algorithm to use?").pack()
        tk.Radiobutton(self.settings_frame, text="Minimax", variable=self.algorithm_choice, value="minimax").pack()
        tk.Radiobutton(self.settings_frame, text="Alpha-Beta", variable=self.algorithm_choice, value="alphabeta").pack()

        # Izvēlieties sekvences garumu (15 līdz 25)
        tk.Label(self.settings_frame, text="Select the length of the sequence (15-25):").pack()
        self.seq_length = tk.IntVar(value=15)
        self.seq_length_spin = tk.Spinbox(self.settings_frame, from_=15, to=25, textvariable=self.seq_length)
        self.seq_length_spin.pack()


        # Spēles sākuma poga
        tk.Button(self.settings_frame, text="Start the game", command=self.start_game).pack(pady=10)

        # Spēles mainīgie
        self.sequence = []
        self.sequence_buttons = []
        self.human_score = 0
        self.computer_score = 0
        self.turn = "human"          # pašreizējais gājiens: “cilvēks” vai “dators”
        self.first_selection = None  # lai saglabātu pirmo izvēlēto indeksu cilvēka progresa laikā
        self.search_tree = None      # lai saglabātu datu koku (datora meklēšanas rezultātu)   


        # spēles rāmis (frame) (displeja secība, punkti un pogas)
        self.game_frame = tk.Frame(master)
        self.sequence_frame = tk.Frame(self.game_frame)
        self.sequence_frame.pack(pady=10)

        # Rāmis sekvences attēlošanai - katrs elements kā poga
        self.score_label = tk.Label(self.game_frame, text="")
        self.score_label.pack(pady=10)

        # Poga, lai restartētu spēli pēc tās pabeigšanas
        self.restart_button = tk.Button(self.game_frame, text="Restart", command=self.restart_game)

        # Poga datu koka parādīšanai (meklēšana), sākotnēji neaktīva
        self.tree_button = tk.Button(self.game_frame, text="Show data tree", command=self.show_tree, state="disabled")
        self.tree_button.pack(pady=5)


    def start_game(self):
        # Spēles stāvokļa inicializēšana atbilstoši izvēlētajiem parametriem
        length = self.seq_length.get()
        self.sequence = [random.randint(1, 9) for _ in range(length)]
        self.human_score = 0
        self.computer_score = 0
        self.first_selection = None
        self.search_tree = None

        # datu koka atiestatīšana
        self.turn = self.start_choice.get()

        # Rādīt spēles rāmi, paslēpjot iestatījumus
        self.settings_frame.pack_forget()
        self.game_frame.pack()
        self.update_display()

        # Ja dators ieslēdzas, palaidiet to darboties
        if self.turn == "computer":
            self.master.after(500, self.computer_move)

    def update_display(self):
        # Sekvences displeja atjaunināšana
        for widget in self.sequence_frame.winfo_children():
            widget.destroy()

        self.sequence_buttons = []
        for i, num in enumerate(self.sequence):
            btn = tk.Button(self.sequence_frame, text=str(num), command=lambda i=i: self.human_select(i), width=4)
            btn.grid(row=0, column=i, padx=2)
            btn.config(bg="lightgray")
            self.sequence_buttons.append(btn)

        self.score_label.config(text=f"Human score: {self.human_score}   Ai score: {self.computer_score}\nCurrent move by: {self.turn}")

        # Ja datu koks ir izveidots, padariet pogu aktīvu
        if self.search_tree is not None:
            self.tree_button.config(state="normal")
        else:
            self.tree_button.config(state="disabled")

    def human_select(self, index):
        # Ja tas nav cilvēka gājiens, ignorējiet presi
        if self.turn != "human":
            return

        # Сброс цвета
        for btn in self.sequence_buttons:
            btn.config(bg="lightgray")

        if self.first_selection is None:
            self.first_selection = index
            self.sequence_buttons[index].config(bg="lightblue")
        else:
            # Pārbaudiet, vai atlasītie indeksi atrodas blakus viens otram
            if abs(index - self.first_selection) == 1:
                # Подсветка обеих кнопок
                self.sequence_buttons[self.first_selection].config(bg="lightgreen")
                self.sequence_buttons[index].config(bg="lightgreen")

                self.make_move(self.first_selection, index, "human")
                self.first_selection = None
                if not self.is_game_over():
                    self.turn = "computer"
                    self.update_display()
                    self.master.after(500, self.computer_move)
                else:
                    self.end_game()
            else:
                # Ja nav blakus, atceliet atlasi
                self.first_selection = None

    def make_move(self, index1, index2, player):
        # Garantē, ka indekss1 ir mazāks par indeksu2
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
            result = "Draw!"
        elif self.human_score > self.computer_score:
            result = "Human win!"
        else:
            result = "AI win!"
        messagebox.showinfo("Game end", result)
        self.restart_button.pack(pady=10)

    def restart_game(self):
        self.game_frame.pack_forget()
        self.settings_frame.pack(pady=10)
        self.restart_button.pack_forget()

    # Heiristiskā funkcija: novērtē stāvokli kā punktu starpību (no datora viedokļa).
    def heuristic(self, sequence, human_score, computer_score):
        return computer_score - human_score

    def generate_moves(self, sequence):
        return list(range(len(sequence) - 1))

    # Rekursīvā funkcija, lai datu koku pārvērstu ievilktā virknē
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
        tree_window.title("Data tree")
        text = tk.Text(tree_window, wrap="none")
        text.insert("end", tree_str)
        text.pack(expand=True, fill="both")

    # Modificēts minimax ar datu koka konstrukciju
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

    # Modificēta alfa-beta ar datu koka konstrukciju
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

    # Pārvietot simulāciju, lai aprēķinātu jaunu spēles stāvokli, nemainot pamatstāvokli
    def simulate_move(self, sequence, human_score, computer_score, move, turn):
        new_sequence = sequence[:] # sequence kopija
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
        else:
            new_val = 2
            human_score += 1
            computer_score += 1
        new_sequence = new_sequence[:move] + [new_val] + new_sequence[move+2:]
        return new_sequence, human_score, computer_score

    def computer_move(self):
        max_depth = 4 # meklēšanas dziļuma ierobežojums
        if self.algorithm_choice.get() == "minimax":
            _, best_move, tree = self.minimax(self.sequence, self.human_score, self.computer_score, "computer", 0, max_depth)
        else:
            _, best_move, tree = self.alphabeta(self.sequence, self.human_score, self.computer_score, "computer", 0, max_depth, -math.inf, math.inf)

        # Saglabāt datu koku vēlākai attēlošanai
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