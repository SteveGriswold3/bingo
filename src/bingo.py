"""Package to Run Virtual Bingo at US Foods."""

import numpy as np
from datetime import datetime
from pymongo import MongoClient
from string import ascii_lowercase as letters

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
        card = np.array(card)
        card[2][2] = 0
        return card

class bingoDB:
    def __init__(self):
        self.con  = MongoClient()
        self.db = self.con['bingo']
        self.players = self.db.players
    
    def generateCardCode(self, times=100, code_len=6):
        code_list = []
        for t in range(0, times):
            code = ""
            for n in range(0,code_len):
                nl = np.random.randint(0,2)
                if nl==0:
                #number
                    num = np.random.randint(0,10)
                    code+=str(num)
                elif nl==1:
                    let = np.random.randint(0,26)
                    code+=letters[let]
            code_list.append(code)
        return code_list

    def validate_user(self, user_id, secret_key):
        res = self.players.find_one({'user_id': user_id, 'secret_key': secret_key})
        if res==None:
            res = self.players.find_one({'user_id': user_id})
            if res==None:
                print('Player Not Registered.')
                return 'id'
            else:
                print('Incorrect Secret Key.')
                return 'key'
        else:
            keys = self.generateCardCode(1, 32)
            self.players.update_one(
                {'user_id': user_id, 'secret_key': secret_key},
                {'$set': {'temp_key': keys[0], 'start_time': datetime.now()}})
            return keys[0]  