from .models import User


def handle_authorize(remote, token, user_info):
    if user_info:
        if token:
            user = UserModel.find_by_email(user_info['email'])
            is_new_user = (user is None)
            if is_new_user:
                user = UserModel(user_info['email'], user_info['family_name'],
                                 user_info['given_name'], user_info['picture'],
                                 token['access_token'])
                try:
                    user.save_to_db()
                except:
                    return jsonify({
                        'message': 'An error occured adding user.'
                    }), 500
            response = user.json()
            response['is_new_user'] = is_new_user
            # return redirect("myd2si://login.com", code=302)
            return jsonify(response), 201
    return jsonify({"message": "Google Authentication error."}), 401
