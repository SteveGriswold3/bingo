"""Package to Run Virtual Bingo at US Foods."""

import numpy as np
from datetime import datetime
from pymongo import MongoClient
from string import ascii_lowercase as letters
import pickle

def get_winning_patterns():
    with open('patterns.pkl', 'rb') as pat:
        return pickle.load(pat)

def bingo_range(start):
    """Create bingo range for each starting point.

    :return: list of range of 15 number in a sequence.
    """
    return [x for x in range(start,start+15)]

def bingo_numbers():
    """Initialize the Numbers Available in Bingo.
    
    :return: dictionary of bingo letters with possible numbers.
    """
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
        self._game_number = 0
        self.selected_numbers = []
    
    @property
    def game_number(self):
        return self._game_number

    @game_number.setter
    def game_number(self, value):
        if self._game_number <= value:
            self._game_number = value
        else:
            raise ValueError("game_number can not go backwards.")
        
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
        #self.con  = MongoClient("mongodb://localhost:27017/")
        self.con = MongoClient()
        self.db = self.con['bingo']
        self.players = self.db.players
        self.cards = self.db.card_ids
        self.winner_patterns = get_winning_patterns()
    
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
    
    def getStamp(self, temp_key):
        res =self.players.find_one({'temp_key': temp_key})
        if res!=None:
            time = res['start_time']
            time_diff = datetime.now() - time
            if (time_diff.total_seconds()/60/60) > 2:
                print("time out")
                return False
            else:
                return True

    def welcome(self, user_id, secret_key):
        res = self.players.find_one(
            {'user_id': user_id, 'secret_key': secret_key},
            {'user_id': True,
            'temp_key': True,
            'nickname': True}
            )
        return res

    def setnickname(self, temp_key, nickname):
        if self.getStamp(temp_key):
            self.players.update_one(
                {'temp_key': temp_key},
                {'$set': {'nickname': nickname}})
            print('Updated nickname:', nickname)
        else:
            print('Inactive: Login Again')

    def add_card_code(self, temp_key, new_code):
        """
        TODO: link to generated card codes.
        """
        try:
            user_id = self.get_user_id(temp_key)
            #card_code
            ret = self.db.card_ids.find_one({'card_code': new_code})
            if ret == None:
                # Card code not found log attempt
                self.db.card_error.insert_one(
                    {'time_stamp': datetime.now(),
                    'user_id': user_id,
                    'issue': 'User Entered Incorrect Code',
                    'wrong_code': new_code
                    }
                )
                return 'Code Not Found', 0
            else:
                # Card Code Found
                if ret['used']==True:
                    # log already used code
                    if ret['user_id']==user_id:
                        return 'You have Already Added This Code'
                    else:
                        self.db.card_error.insert_one(
                            {'time_stamp': datetime.now(),
                            'user_id': user_id,
                            'issue': 'Another Player has code',
                            'other_id': ret['user_id']
                            }
                        )
                        return 'Code Used by Another Player', 0
                else:
                    # Success
                    card_count = self.cards.count_documents({'user_id': user_id})
                    card_count+=1
                    self.cards.update_one(
                        {'card_code': new_code},
                        {'$set': {'used': True, 'user_id': user_id, 'nbr': card_count}}
                        )
                    return 'successful', card_count
        except:
            return 'Code could not be added.  Try again later.', 0

    def save_number(self, temp_key, card_code, numbers):
        self.cards.update_one(
            {'card_code': card_code},
            {'$set': {'numbers': numbers}}
            )

    def get_numbers(self, temp_key, card_code):
        user_id = self.get_user_id(temp_key)
        numbers = self.cards.find_one(
            {'user_id': user_id, 'card_code': card_code}, 
            {'_id': False, 'numbers': True}
            )
        return numbers

    def get_card_codes(self, user_id):
        ret = self.db.card_ids.find({'user_id': user_id}, {'_id': False})
        player_cards = [card for card in ret]
        return player_cards

    def getTempKey(self, user_id, secret_key):
        res = self.players.find_one(
            {'user_id': user_id, 'secret_key': secret_key},
            {'temp_key': True}
            )
        return res['temp_key']

    def get_user_id(self, temp_key):
        res = self.players.find_one(
            {'temp_key': temp_key},
            {'user_id': True}
        )
        return res['user_id']
    
    def add_winning_pattern(self, new_pattern):
        self.winner_patterns.append(new_pattern)
    
    def reset_winning_patterns(self):
        self.winner_patterns = get_winning_patterns()
    