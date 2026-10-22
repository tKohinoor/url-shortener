from flask import Flask, request, jsonify, redirect, render_template
from sqlite3 import IntegrityError
from db import init_db, save_url, get_url, increment_clicks, get_stats
from shortener import generate_unique_code
from validators import normalize_url, is_valid_url, is_valid_alias
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.middleware.proxy_fix import ProxyFix


app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)
limiter = Limiter(get_remote_address, app=app, default_limits=[])
init_db()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/shorten", methods=["POST"])
@limiter.limit("10 per minute")
def shorten():
    data = request.get_json(silent=True) or {}
    raw_url = data.get("url", "")

    if not isinstance(raw_url, str) or not raw_url.strip():
        return jsonify(error="Missing 'url' field"), 400

    url = normalize_url(raw_url)
    if not is_valid_url(url):
        return jsonify(error="Invalid URL"), 400

    alias = data.get("alias")
    if alias:
        if not isinstance(alias, str) or not is_valid_alias(alias):
            return jsonify(
                error="Alias must be 3-32 characters: letters, digits, - or _"
            ), 400
        code = alias
    else:
        code = generate_unique_code()

    try:
        save_url(code, url)
    except IntegrityError:
        return jsonify(error="That alias is already taken"), 409

    return jsonify(
        code=code,
        short_url=request.host_url + code,
        original_url=url,
    ), 201


@app.route("/api/stats/<code>")
def stats(code):
    data = get_stats(code)
    if data is None:
        return jsonify(error="Short link not found"), 404
    return jsonify(data)


@app.route("/<code>")
def follow(code):
    row = get_url(code)
    if row is None:
        return jsonify(error="Short link not found"), 404

    increment_clicks(code)
    return redirect(row["original_url"], code=302)


if __name__ == "__main__":
    app.run(debug=True)