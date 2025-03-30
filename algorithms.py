import math
from tree_node import TreeNode
from utils import simulate_move, heuristic, generate_moves

def minimax(sequence, human_score, computer_score, turn, depth, max_depth):
    node = TreeNode(depth, sequence=sequence, human_score=human_score, computer_score=computer_score, turn=turn)
    if len(sequence) == 1 or depth == max_depth:
        node.value = heuristic(sequence, human_score, computer_score)
        return node.value, None, node

    moves = generate_moves(sequence)
    if turn == "computer":
        best_val = -math.inf
        best_move = None
        for move in moves:
            new_seq, new_human, new_computer = simulate_move(sequence, human_score, computer_score, move, turn)
            childval, child_node = minimax(new_seq, new_human, new_computer, "human", depth + 1, max_depth)
            node.children.append((move, child_node))
            if childval > best_val:
                best_val = childval
                best_move = move
        node.value = best_val
        return best_val, best_move, node
    else:
        best_val = math.inf
        best_move = None
        for move in moves:
            new_seq, new_human, new_computer = simulate_move(sequence, human_score, computer_score, move, turn)
            childval, child_node = minimax(new_seq, new_human, new_computer, "computer", depth + 1, max_depth)
            node.children.append((move, child_node))
            if childval < best_val:
                best_val = childval
                best_move = move
        node.value = best_val
        return best_val, best_move, node

def alphabeta(sequence, human_score, computer_score, turn, depth, max_depth, alpha, beta):
    node = TreeNode(depth, sequence=sequence, human_score=human_score, computer_score=computer_score, turn=turn)
    if len(sequence) == 1 or depth == max_depth:
        node.value = heuristic(sequence, human_score, computer_score)
        return node.value, None, node

    moves = generate_moves(sequence)
    best_move = None
    if turn == "computer":
        value = -math.inf
        for move in moves:
            new_seq, new_human, new_computer = simulate_move(sequence, human_score, computer_score, move, turn)
            childval, child_node = alphabeta(new_seq, new_human, new_computer, "human", depth + 1, max_depth, alpha, beta)
            node.children.append((move, child_node))
            if childval > value:
                value = childval
                best_move = move
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        node.value = value
        return value, best_move, node
    else:
        value = math.inf
        for move in moves:
            new_seq, new_human, new_computer = simulate_move(sequence, human_score, computer_score, move, turn)
            childval, child_node = alphabeta(new_seq, new_human, new_computer, "computer", depth + 1, max_depth, alpha, beta)
            node.children.append((move, child_node))
            if childval < value:
                value = childval
                best_move = move
            beta = min(beta, value)
            if beta <= alpha:
                break
        node.value = value
        return value, best_move, node