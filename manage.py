import click
import os
import shutil
from pathlib import Path
from flask.cli import FlaskGroup
from app import create_app, db

@click.group()
def cli():
    """Management script for ChatGPT Scraper"""
    pass

@cli.command()
def clean():
    """Clean and organize project structure"""
    # Definisi struktur folder yang diinginkan
    structure = {
        'app': ['__init__.py', 'models.py', 'routes.py', 'utils.py'],
        'database': ['schema.sql'],
        'static/css': ['themes.css'],
        'templates': ['base.html', 'index.html', 'login.html', 'register.html', 'history.html'],
        '.': ['config.py', 'manage.py', 'manage_db.bat']
    }
    
    # Files to remove
    files_to_remove = [
        'database/clear.sql',
        'database/install.sql',
        'database/update_database.sql',
        'install.bat',
        'clear.bat',
        'reset_db.bat',
        'update_database.bat',
        'database.py',
        'auth.py'
    ]
    
    # Create new structure
    for folder, files in structure.items():
        Path(folder).mkdir(parents=True, exist_ok=True)
        for file in files:
            file_path = Path(folder) / file
            if not file_path.exists():
                file_path.touch()
    
    # Remove unnecessary files
    for file in files_to_remove:
        try:
            Path(file).unlink(missing_ok=True)
        except Exception as e:
            print(f"Warning: Could not remove {file}: {e}")
    
    print("Project structure has been cleaned and organized!")

@cli.command("init-db")
def init_db():
    """Initialize database"""
    db.drop_all()
    db.create_all()
    print("Database initialized!")

@cli.command("clear-db")
def clear_db():
    """Clear all data"""
    db.session.commit()
    db.drop_all()
    db.create_all()
    print("Database cleared!")

if __name__ == "__main__":
    cli() 