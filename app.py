"""Compatibility entry point for the Flask application."""
from scrapenews.web import app


if __name__ == "__main__":
    debug = __import__("os").environ.get("FLASK_DEBUG", "1") != "0"
    app.run(debug=debug, port=int(__import__("os").environ.get("PORT", 5050)))
