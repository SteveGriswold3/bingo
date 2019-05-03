from flask import Flask, request, render_template, url_for
from src.bingo import Card, bingoDB
import json

db = bingoDB()
app = Flask(__name__)

calls = [5,10,6]

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

@app.route('/play')
def play():
    card = Card()
    return render_template('play.html', card=card.card_numbers.T)


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

if __name__ == '__main__':
    #app.run(host='0.0.0.0', port=5000, debug=True)
    app.run(host='0.0.0.0')