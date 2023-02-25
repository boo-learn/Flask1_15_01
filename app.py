from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import random
import sqlite3
from pathlib import Path
from flask import g

BASE_DIR = Path(__file__).parent
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{BASE_DIR / 'main.db'}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.app_context().push()
db = SQLAlchemy(app)
migrate = Migrate(app, db)


class AuthorModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), unique=True)
    quotes = db.relationship('QuoteModel', backref='author', lazy='dynamic')

    def __init__(self, name):
        self.name = name

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name
        }


class QuoteModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey(AuthorModel.id))
    text = db.Column(db.String(255), unique=False)

    def __init__(self, author, text):
        self.author_id = author.id
        self.text = text

    def to_dict(self):
        return {
            "id": self.id,
            "text": self.text,
            "author": self.author.to_dict()
        }


# Сериализация:
# Object --> dict --> JSON

@app.route("/quotes")
def get_quotes():
    quotes = QuoteModel.query.all()
    quotes_dict = [quote.to_dict() for quote in quotes]
    return quotes_dict


# quotes/1
# quotes/3
# quotes/5
# quotes/10
@app.route("/quotes/<int:quote_id>")
def get_quote_by_id(quote_id):
    quote = QuoteModel.query.get(quote_id)
    if quote is None:
        return f"Quote with id={quote_id} not found", 404
    return quote.to_dict(), 200


@app.route("/quotes/random", methods=["GET"])
def random_quote():
    return random.choice(quotes)


@app.route("/quotes", methods=["POST"])
def create_quote():
    new_quote = request.json
    quote = QuoteModel(**new_quote)
    db.session.add(quote)
    db.session.commit()
    return quote.to_dict(), 201


@app.route("/quotes/<int:quote_id>", methods=['PUT'])
def edit_quote(quote_id):
    quote = QuoteModel.query.get(quote_id)
    if quote is None:
        return f"Quote with id={quote_id} not found", 404
    new_data = request.json
    if 'text' in new_data:
        ...
    if 'author' in new_data:
        ...
    db.session.commit()
    return quote, 200


@app.route("/quotes/<int:quote_id>", methods=['DELETE'])
def delete_quote(quote_id):
    for quote in quotes:
        if quote["id"] == quote_id:
            # TODO: реализовать удаление цитаты из списка
            return "", 204
    return f"Quote with id={quote_id} not found", 404


if __name__ == "__main__":
    app.run(debug=True)
