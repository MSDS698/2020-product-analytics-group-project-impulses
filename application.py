"""Python Flask WebApp Auth0 integration example
"""
from functools import wraps
import json
from os import environ as env
from werkzeug.exceptions import HTTPException

from dotenv import load_dotenv, find_dotenv
from flask import Flask
from flask import jsonify
from flask import redirect
from flask import render_template
from flask import session
from flask import url_for
from authlib.flask.client import OAuth
from six.moves.urllib.parse import urlencode

import constants

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

AUTH0_CALLBACK_URL = env.get(constants.AUTH0_CALLBACK_URL)
AUTH0_CLIENT_ID = env.get(constants.AUTH0_CLIENT_ID)
AUTH0_CLIENT_SECRET = env.get(constants.AUTH0_CLIENT_SECRET)
AUTH0_DOMAIN = env.get(constants.AUTH0_DOMAIN)
AUTH0_BASE_URL = 'https://' + AUTH0_DOMAIN
AUTH0_AUDIENCE = env.get(constants.AUTH0_AUDIENCE)

application = Flask(__name__, static_url_path='/public', static_folder='./public')
application.secret_key = constants.SECRET_KEY
application.debug = True


@application.errorhandler(Exception)
def handle_auth_error(ex: Exception) -> jsonify:
    """
    Handle authentication error
    :param ex: Exception
    :return: A json type of response
    """
    response = jsonify(message=str(ex))
    response.status_code = (ex.code if isinstance(ex, HTTPException) else 500)
    return response


oauth = OAuth(application)

auth0 = oauth.register(
    'auth0',
    client_id=AUTH0_CLIENT_ID,
    client_secret=AUTH0_CLIENT_SECRET,
    api_base_url=AUTH0_BASE_URL,
    access_token_url=AUTH0_BASE_URL + '/oauth/token',
    authorize_url=AUTH0_BASE_URL + '/authorize',
    client_kwargs={
        'scope': 'openid profile email',
    },
)


def requires_auth(f):
    @wraps(f)
    def decorated(*args: str, **kwargs: int) -> f:
        """
        If PROFILE_KEY is not in session, redirect to login page
        If PROFILE_KEY is in session, return function f
        :param args: *args
        :param kwargs: *kwargs
        :return: function f(*args, **kwargs)
        """
        if constants.PROFILE_KEY not in session:
            return redirect('/login')
        return f(*args, **kwargs)

    return decorated


# Controllers API
@application.route('/')
def home() -> render_template:
    """
    Render to home.html
    :return: render_template('home.html')
    """
    return render_template('home.html')


@application.route('/callback')
def callback_handling() -> redirect:
    """
    Handle Auth0's callback, and redirect to dashboard.html
    :return: function redirect('/dashboard')
    """
    auth0.authorize_access_token()
    resp = auth0.get('userinfo')
    userinfo = resp.json()

    session[constants.JWT_PAYLOAD] = userinfo
    session[constants.PROFILE_KEY] = {
        'user_id': userinfo['sub'],
        'name': userinfo['name'],
        'picture': userinfo['picture']
    }
    return redirect('/dashboard')


@application.route('/login')
def login() -> auth0.authorize_redirect:
    """
    Redirect to Auth0's login page
    :return: method auth0.authorize_redirect(redirect_uri=AUTH0_CALLBACK_URL, audience=AUTH0_AUDIENCE)
    """
    return auth0.authorize_redirect(redirect_uri=AUTH0_CALLBACK_URL, audience=AUTH0_AUDIENCE)


@application.route('/logout')
def logout() -> redirect:
    """
    Clear the session and redirect to home.html
    :return: function redirect(auth0.api_base_url + '/v2/logout?' + urlencode(params))
    """
    session.clear()
    params = {'returnTo': url_for('home', _external=True), 'client_id': AUTH0_CLIENT_ID}
    return redirect(auth0.api_base_url + '/v2/logout?' + urlencode(params))


@application.route('/dashboard')
@requires_auth
def dashboard() -> render_template:
    """
    Render to dashboard.html
    :return: function render_template('dashboard.html', userinfo, userinfo_pretty)
    """
    return render_template('dashboard.html',
                           userinfo=session[constants.PROFILE_KEY],
                           userinfo_pretty=json.dumps(session[constants.JWT_PAYLOAD], indent=4))


if __name__ == "__main__":
    # testing local
    # application.run(host='0.0.0.0', port=env.get('PORT', 3000))

    # deployment
    application.run(debug=True, port=5000)

