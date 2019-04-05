from flask import Flask, request, render_template, url_for
from src.bingo import Card 

app = Flask(__name__)

@app.route('/')
def main_page():
    #return app.send_static_file('calls.html')
    return render_template('calls.html')


@app.route('/play')
def play():
    card = Card()
    return render_template('play.html', card=card.card_numbers.T)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8085, debug=True)