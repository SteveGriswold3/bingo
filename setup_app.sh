echo "copying source files..."
scp src/bingo.py macdevro:flaskapp/src/bingo.py
scp flaskapp.py macdevro:flaskapp/flaskapp.py

echo "copying web templates..."
scp static/css/calls.css macdevro:flaskapp/static/css/calls.css
scp static/img/USF_LOGO.jpg macdevro:flaskapp/static/img/USF_LOGO.jpg
scp static/img/usf-logo-scaled.png macdevro:flaskapp/static/img/usf-logo-scaled.png
scp static/calls.html macdevro:flaskapp/static/calls.html
scp static/login.html macdevro:flaskapp/static/login.html
scp templates/calls.html macdevro:flaskapp/templates/calls.html
scp templates/play.html macdevro:flaskapp/templates/play.html
scp templates/welcome.html macdevro:flaskapp/templates/welcome.html
