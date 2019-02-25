from src.server import app, server
from src import callbacks

if __name__ == "__main__":
    app.run_server(debug=False)
