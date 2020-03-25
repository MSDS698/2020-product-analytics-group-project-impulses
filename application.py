from flask import Flask, render_template

application = Flask(__name__)

@application.route("/")
def print_hello():
    """Show a list of article titles"""
    return render_template('articles.html')

if __name__ == '__main__':
    application.jinja_env.auto_reload = True
    application.config['TEMPLATES_AUTO_RELOAD'] = True
    application.debug = True
    application.run()