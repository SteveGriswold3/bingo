from flask import Flask, request, render_template, url_for
from src.bingo import Card, bingoDB
import json

db = bingoDB()
app = Flask(__name__)

calls = [5,10,6]

@app.route('/')
def main_page():
    #return app.send_static_file('calls.html')
    return render_template('calls.html')

@app.route('/login')
def login():

    return app.send_static_file('login.html') 


@app.route('/<id>/<key>/check_user.json')
def valid_user(id, key):
    ret = db.validate_user(id, key)
    return json.dumps({'response': ret})


@app.route('/welcome')
def welcome():

    return render_template('welcome.html')


@app.route('/play')
def play():
    card = Card()
    return render_template('play.html', card=card.card_numbers.T)

@app.route('/check_calls')
def return_numbers():
    return calls

@app.route('/<nbr>/<option>/calls.json')
def update_calls(nbr, option):
    if option == '-':
        for i, x in enumerate(calls):
            if x==nbr:
                calls.remove(i)
    else:
        calls.append(nbr)
    
    print([c for c in calls])
    return json.dumps(calls)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8085, debug=True)