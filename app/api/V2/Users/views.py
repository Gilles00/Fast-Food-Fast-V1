from flask import Blueprint, request, make_response
import datetime

from app.api.V2.Auth.helper import token_require

user = Blueprint('users', __name__, url_prefix='/api/v2')


@user.route('/users/orders', methods=['POST', 'GET'])
@token_require
def make_order(current_user):
	if request.method == 'POST':
		if not current_user:
			return make_response("Please login to order")
		user_data = request.get_json()

		meal_id = user_data.get('meal_id')
		user_id = current_user[0]
		time = datetime.datetime.now()

		from .models import place_order
		return place_order(meal_id, user_id, time)

	if not current_user:
		return make_response("Login to view order history")
	from app.api.V2.Users.models import get_history
	return get_history(current_user[0])
