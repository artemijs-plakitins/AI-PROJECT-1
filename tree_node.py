class TreeNode:
    def init(self, depth, move=None, sequence=None, human_score=0, computer_score=0, turn="", value=None):
        self.depth = depth
        self.move = move
        self.sequence = sequence
        self.human_score = human_score
        self.computer_score = computer_score
        self.turn = turn
        self.value = value
        self.children = []