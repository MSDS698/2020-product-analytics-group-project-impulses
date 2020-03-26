from flask import Flask, render_template

application = Flask(__name__)

@application.route("/")
def print_hello():
    """Show a list of article titles"""
    return render_template('articles.html')

if __name__ == '__main__':
    application.run(debug=True, port=5000)
