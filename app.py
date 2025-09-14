
from flask import Flask, redirect, url_for, session, render_template
from authlib.integrations.flask_client import OAuth
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("APP_SECRET_KEY")

oauth = OAuth(app)

auth0 = oauth.register(
    'auth0',
    client_id=os.getenv("AUTH0_CLIENT_ID"),
    client_secret=os.getenv("AUTH0_CLIENT_SECRET"),
    api_base_url=f'https://{os.getenv("AUTH0_DOMAIN")}',
    access_token_url=f'https://{os.getenv("AUTH0_DOMAIN")}/oauth/token',
    authorize_url=f'https://{os.getenv("AUTH0_DOMAIN")}/authorize',
    server_metadata_url=f'https://{os.getenv("AUTH0_DOMAIN")}/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid profile email',
    },
)

@app.route('/')
def index():
    return 'Welcome to our project. We will help you demystify legal documents <a href="/login">Login</a>'

@app.route('/login')
def login():
    return auth0.authorize_redirect(redirect_uri=url_for('callback', _external=True))

@app.route('/callback')
def callback():
    token = auth0.authorize_access_token()
    session['user'] = token['userinfo']
    return redirect('/dashboard')

@app.route('/dashboard')
def dashboard():
    user = session.get('user')
    if not user:
        return redirect('/login')
    return render_template('dashboard.html', user=user)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(
        f'https://{os.getenv("AUTH0_DOMAIN")}/v2/logout?' +
        'returnTo=' + url_for('index', _external=True) +
        '&client_id=' + os.getenv("AUTH0_CLIENT_ID")
    )

if __name__ == '__main__':
    app.run(debug=True)
