import logging

from app import create_app

# Show INFO-level log lines (such as notifications) in the server terminal.
logging.basicConfig(level=logging.INFO)

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5001)
