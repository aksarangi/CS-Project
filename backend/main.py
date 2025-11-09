from flask import Flask
from api.books import books_bp
# import other blueprints as we implement them

app = Flask(__name__)

# Register blueprints
app.register_blueprint(books_bp)

if __name__ == '__main__':
    app.run(debug=True)
