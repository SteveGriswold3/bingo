"""
TODO: Login for Calls.
TODO: Additional Patterns
TODO: Call Bingo.
"""
from flask import Flask, request, render_template, url_for
from src.bingo import Card, bingoDB
import json

db = bingoDB()
app = Flask(__name__)

calls = []

@app.route('/')
def main_page():
    return render_template('calls.html')
    
@app.route('/login')
def login():

    return app.send_static_file('login.html') 


@app.route('/<id>/<key>/check_user.json')
def valid_user(id, key):
    ret = db.validate_user(id, key)
    return json.dumps({'response': ret})


@app.route('/<id>/<key>/welcome')
def welcome(id, key):
    """
    """
    user = db.welcome(id, key)
    
    cards = db.get_card_codes(user['user_id'])         
    
    if 'nickname' in user.keys():
        nickname = user['nickname']
    else:
        nickname = None

    return render_template(
        'welcome.html',
        temp_key = user['temp_key'],
        player_name = nickname,
        player_cards=cards
        )

@app.route('/<temp_key>/<nickname>/update_nickname.json')
def update_nickname(temp_key, nickname):
    try:
        db.setnickname(temp_key, nickname)
        return json.dumps({'response': 'successful'})
    except:
        return json.dumps({'response': 'failed'})

@app.route('/<temp_key>/<new_code>/add_card_code.json')
def add_card_code(temp_key, new_code):
    ret, card_count = db.add_card_code(temp_key, new_code)
    
    return json.dumps({'response': ret, 'card_count': card_count})

@app.route('/<temp_key>/<code>/random_card.json')
def random_card(temp_key, code):
    card = Card()
    rand_card={}
    rand_card['card'] = card.card_numbers.T
    rand_card['card'] = rand_card['card'].tolist()
    db.save_number(temp_key, code, rand_card)
    print(rand_card)
    return json.dumps(rand_card)

@app.route('/<temp_key>/<code>/get_numbers.json')
def get_number(temp_key, code):
    card = db.get_numbers(temp_key, code)
    return json.dumps(card['numbers'])

@app.route('/play', methods=['POST'])
def play():
    code_list = request.form['play_list_values']
    temp_key = request.form['temp_key']
    
    code_list = code_list.split(',')
    print(code_list)
    cards = []
    for card in code_list:
        card_numbers = db.get_numbers(temp_key, card)
        print(card_numbers['numbers']['card'])
        cards.append(card_numbers['numbers']['card'])

    return render_template('play.html', cards=cards)


@app.route('/<nbr>/<option>/add_call.json')
def add_calls(nbr, option):
    if option == '-':
        for x in calls:
            if x==nbr:
                calls.remove(x)
    else:
        calls.append(nbr)
    return 'success'

@app.route('/calls.json')
def update_calls():
  return json.dumps(calls)

@app.route('/reset_calls.json')
def reset_calls():
    while len(calls)>0:
        calls.pop()
    db.reset_winning_patterns()
    return json.dumps({'reset': 'successful'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
    #app.run(host='0.0.0.0')