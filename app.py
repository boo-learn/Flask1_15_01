from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import random
import sqlite3
from pathlib import Path
from flask import g
from sqlalchemy.sql import func

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
    surname = db.Column(db.String(32))
    quotes = db.relationship('QuoteModel', backref='author', lazy='dynamic')

    def __init__(self, name, surname):
        self.name = name
        self.surname = surname

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "surname": self.surname,
        }


class QuoteModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey(AuthorModel.id))
    text = db.Column(db.String(255), unique=False)
    rate = db.Column(db.Integer, server_default="1", default="1", nullable=False)
    created_date = db.Column(db.DateTime(timezone=True), server_default=func.now())

    def __init__(self, author, text, rate=1):
        self.author_id = author.id
        self.text = text
        self.rate = rate

    def to_dict(self):
        return {
            "id": self.id,
            "text": self.text,
            "author": self.author.to_dict(),
            "rate": self.rate,
            "created_date": self.created_date.strftime("%d.%m.%Y")
        }


# AUTHORS
# /authors  <--- all authors
# /authors?surname=Ivanov  <-- authors with filter
@app.route("/authors")
def get_authors():
    surname = request.args.get("surname")
    if surname:
        authors = AuthorModel.query.filter_by(surname=surname)
    else:
        authors = AuthorModel.query.all()

    authors_dict = [author.to_dict() for author in authors]
    return authors_dict


@app.route("/authors/<int:author_id>")
def get_author_by_id(author_id):
    author = AuthorModel.query.get(author_id)
    if author is None:
        return f"Author with id={author_id} not found", 404
    return author.to_dict(), 200


@app.route("/authors", methods=["POST"])
def create_author():
    new_author = request.json
    author = AuthorModel(**new_author)
    db.session.add(author)
    db.session.commit()
    return author.to_dict(), 201


# QUOTES

# ????????????????????????:
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


@app.route("/authors/<int:author_id>/quotes", methods=["POST"])
def create_quote(author_id):
    author = AuthorModel.query.get(author_id)
    new_quote = request.json
    quote = QuoteModel(author, **new_quote)
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
            # TODO: ?????????????????????? ???????????????? ???????????? ???? ????????????
            return "", 204
    return f"Quote with id={quote_id} not found", 404


if __name__ == "__main__":
    app.run(debug=True)
