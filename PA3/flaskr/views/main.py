# from flask import Blueprint, render_template

# main_bp = Blueprint('main', __name__)

# @main_bp.route('/')
# def index():
#     return render_template('index.html')

# @main_bp.route('/dashboard')
# def dashboard():
#     return render_template('dashboard.html')


from flask import Blueprint, render_template
from typing import Any

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index() -> Any:
    return render_template('index.html')

@main_bp.route('/dashboard')
def dashboard() -> Any:
    return render_template('dashboard.html')