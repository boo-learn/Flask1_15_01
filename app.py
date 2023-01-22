from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
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


class QuoteModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(32), unique=False)
    text = db.Column(db.String(255), unique=False)

    def __init__(self, author, text):
        self.author = author
        self.text = text

    def to_dict(self):
        return {
            "id": self.id,
            "author": self.author,
            "text": self.text
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
    select_quote = "SELECT * FROM quotes WHERE id=?;"
    cursor = get_db().cursor()
    cursor.execute(select_quote, (quote_id,))
    quote = cursor.fetchone()
    if quote is None:
        return f"Quote with id={quote_id} not found", 404
    quote = convert_data(quote)
    return quote, 200


@app.route("/quotes/random", methods=["GET"])
def random_quote():
    return random.choice(quotes)


@app.route("/quotes", methods=["POST"])
def create_quote():
    new_quote = request.json
    create_quote_sql = """
    INSERT INTO
    quotes (author,text)
    VALUES
    (?, ?);
    """
    cursor = get_db().cursor()
    cursor.execute(create_quote_sql, (new_quote['author'], new_quote['text']))
    new_quote["id"] = cursor.lastrowid
    return new_quote, 201


@app.route("/quotes/<int:quote_id>", methods=['PUT'])
def edit_quote(quote_id):
    for quote in quotes:
        if quote["id"] == quote_id:
            new_data = request.json
            if 'text' in new_data:
                quote['text'] = new_data['text']
            if 'author' in new_data:
                quote['author'] = new_data['author']
            return quote, 200
    return f"Quote with id={quote_id} not found", 404


@app.route("/quotes/<int:quote_id>", methods=['DELETE'])
def delete_quote(quote_id):
    for quote in quotes:
        if quote["id"] == quote_id:
            # TODO: реализовать удаление цитаты из списка
            return "", 204
    return f"Quote with id={quote_id} not found", 404


if __name__ == "__main__":
    app.run(debug=True)
