from flask import Blueprint, request, session, redirect, url _for
from flask.db import get_db
import secrets

cart_bp = Blueprint('cart', __name__, url_prefix = '/cart')
@cart_bp.route('/')
def view_cart():
    """show all item in cart during the user's session"""
    if 'cart id' not in session:
        #if no cart id, create one 
