import os
from flask_migrate import Migrate, upgrade
from app import create_app, db
from app.models import User, Track

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Track=Track)


if __name__ == "__main__":
    app.run()