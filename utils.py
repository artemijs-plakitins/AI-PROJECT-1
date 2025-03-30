def heuristic(sequence, human_score, computer_score):
    return computer_score - human_score

def generate_moves(sequence):
    return list(range(len(sequence) - 1))

def simulate_move(sequence, human_score, computer_score, move, turn):
    new_sequence = sequence[:]
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