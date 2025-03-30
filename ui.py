import tkinter as tk
from game import Game

def start_game_ui():
    root = tk.Tk()
    game = Game(root)
    root.mainloop()