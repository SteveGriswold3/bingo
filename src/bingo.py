"""Package to Run Virtual Bingo at US Foods."""

import numpy as np

def bingo_range(start):
    return [x for x in range(start,start+15)]

def bingo_numbers():
    bingo_nbrs = {}
    start = 1
    bingo_nbrs['b'] = bingo_range(start)
    start+=15
    bingo_nbrs['i'] = bingo_range(start)
    start+=15
    bingo_nbrs['n'] = bingo_range(start)
    start+=15
    bingo_nbrs['g'] = bingo_range(start)
    start+=15
    bingo_nbrs['o'] = bingo_range(start)
    return bingo_nbrs

bingo_nbrs = bingo_numbers()

class Bingo:
    def __init__(self):
        self.game_number = 0
        self.selected_numbers = []
        
    def picked_number(self, new_number):
        self.selected_numbers.append(new_number)
    
    def pick_random_number(self):
        return np.random.randint(1,36)

class Card:
    def __init__(self):
        self.card_id = 0
        self.card_numbers = self.generate_card(bingo_nbrs)
    
    def generate_card(self, bingo_nbrs):
        card = []
        for k in bingo_nbrs.keys():
            card.append(np.random.choice(bingo_nbrs[k],5,replace=False))
        return np.array(card)