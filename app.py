from flask import Flask, request
import random
import sqlite3

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False


def convert_data(quote: tuple) -> dict:
    keys = ["id", "author", "text"]
    return dict(zip(keys, quote))


@app.route("/")
def hello_world():
    return "Hello, World!"


@app.route("/about")
def about():
    return about_me


@app.route("/quotes")
def get_quotes():
    select_quotes = "SELECT * from quotes"
    connection = sqlite3.connect("test.db")
    cursor = connection.cursor()
    cursor.execute(select_quotes)
    quotes = cursor.fetchall()
    quotes = map(convert_data, quotes)
    cursor.close()
    connection.close()
    return quotes


# quotes/1
# quotes/3
# quotes/5
# quotes/10
@app.route("/quotes/<int:quote_id>")
def get_quote_by_id(quote_id):
    select_quote = "SELECT * FROM quotes WHERE id=?;"
    connection = sqlite3.connect("test.db")
    cursor = connection.cursor()
    cursor.execute(select_quote, (quote_id,))
    quote = cursor.fetchone()
    if quote is None:
        return f"Quote with id={quote_id} not found", 404
    quote = convert_data(quote)
    cursor.close()
    connection.close()
    return quote, 200


#


@app.route("/quotes/random", methods=["GET"])
def random_quote():
    return random.choice(quotes)


@app.route("/quotes", methods=["POST"])
def create_quote():
    new_quote = request.json
    last_quote = quotes[-1]
    new_id = last_quote["id"] + 1
    new_quote["id"] = new_id
    quotes.append(new_quote)
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
