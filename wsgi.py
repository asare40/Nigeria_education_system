# wsgi.py
from dashboard.app import server as application

if __name__ == "__main__":
    application.run()
