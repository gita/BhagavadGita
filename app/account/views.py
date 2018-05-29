import os

from flask import (current_app, flash, jsonify, redirect, render_template,
                   request, session, url_for)
from flask_login import current_user, login_required, login_user, logout_user
from flask_rq import get_queue
from werkzeug.security import gen_salt

from . import account
from .. import db, oauthclient
# from .. import github_blueprint, google_blueprint, facebook_blueprint
from ..email import send_email
from ..models import App, Client, User, Token
from .forms import (ChangeEmailForm, ChangePasswordForm, CreateAppForm,
                    CreatePasswordForm, LoginForm, RegistrationForm,
                    RequestResetPasswordForm, ResetPasswordForm, UpdateAppForm)
from flask_mail import Mail, Message
from .. import mail
# from flask_dance.consumer import oauth_authorized, oauth_error
# from sqlalchemy.orm.exc import NoResultFound
# from flask_dance.contrib.github import github
# from flask_dance.contrib.google import google
# from flask_dance.contrib.facebook import facebook


# create/login local user on successful OAuth login
# @oauth_authorized.connect_via(github_blueprint)
# def github_logged_in(blueprint, token):
#     if not token:
#         flash("Failed to log in with GitHub.", category="error")
#         return False

#     resp = blueprint.session.get("/user")
#     if not resp.ok:
#         msg = "Failed to fetch user info from GitHub."
#         flash(msg, category="error")
#         return False

#     github_info = resp.json()
#     github_user_id = str(github_info["id"])

#     # Find this OAuth token in the database, or create it
#     query = OAuth.query.filter_by(
#         provider=blueprint.name,
#         provider_user_id=github_user_id,
#     )
#     try:
#         oauth = query.one()
#     except NoResultFound:
#         oauth = OAuth(
#             provider=blueprint.name,
#             provider_user_id=github_user_id,
#             token=token,
#         )

#     user = User.query.filter_by(email=github_info["email"]).first()

#     if oauth.user:
#         login_user(oauth.user)
#         flash('You are now logged in. Welcome back!', 'success')
#         return redirect(request.args.get('next') or url_for('main.index'))

#     elif user:
#         login_user(user, True)
#         flash('You are now logged in. Welcome back!', 'success')
#         return redirect(request.args.get('next') or url_for('main.index'))

#     else:
#         # Create a new local user account for this user
#         max_id = db.session.query(db.func.max(User.id)).scalar()
#         user = User(
#             id=max_id+1,
#             email=github_info["email"],
#             social_id=github_info["id"],
#             social_provider="github",
#             username=github_info["login"],
#             first_name=github_info["name"],
#             confirmed=True)
#         # Associate the new local user account with the OAuth token
#         oauth.user = user
#         # Save and commit our database models
#         db.session.add_all([user, oauth])
#         db.session.commit()
#         # Log in the new local user account
#         login_user(user, True)
#         flash('You are now logged in. Welcome!', 'success')
#         return redirect(request.args.get('next') or url_for('main.index'))

#     # Disable Flask-Dance's default behavior for saving the OAuth token
#     return False


# @oauth_error.connect_via(github_blueprint)
# def github_error(blueprint, error, error_description=None, error_uri=None):
#     msg = (
#         "OAuth error from {name}! "
#         "error={error} description={description} uri={uri}"
#     ).format(
#         name=blueprint.name,
#         error=error,
#         description=error_description,
#         uri=error_uri,
#     )
#     flash(msg, category="error")


# @oauth_authorized.connect_via(google_blueprint)
# def google_logged_in(blueprint, token):
#     if not token:
#         flash("Failed to log in with Google.", category="error")
#         return False
#
#     resp = blueprint.session.get("/oauth2/v2/userinfo")
#     if not resp.ok:
#         msg = "Failed to fetch user info from Google."
#         flash(msg, category="error")
#         return False
#
#     google_info = resp.json()
#     google_user_id = str(google_info["id"])
#
#     # Find this OAuth token in the database, or create it
#     query = OAuth.query.filter_by(
#         provider=blueprint.name,
#         provider_user_id=google_user_id,
#     )
#     try:
#         oauth = query.one()
#     except NoResultFound:
#         oauth = OAuth(
#             provider=blueprint.name,
#             provider_user_id=google_user_id,
#             token=token,
#         )
#
#     user = User.query.filter_by(email=google_info["email"]).first()
#
#     if oauth.user:
#         login_user(oauth.user)
#         flash('You are now logged in. Welcome back!', 'success')
#         return redirect(request.args.get('next') or url_for('main.index'))
#
#     elif user:
#         login_user(user, True)
#         flash('You are now logged in. Welcome back!', 'success')
#         return redirect(request.args.get('next') or url_for('main.index'))
#
#     else:
#         # Create a new local user account for this user
#         max_id = db.session.query(db.func.max(User.id)).scalar()
#         user = User(
#             id=max_id+1,
#             email=google_info["email"],
#             social_id=google_info["id"],
#             social_provider="google",
#             first_name=google_info["name"],
#             confirmed=True)
#         # Associate the new local user account with the OAuth token
#         oauth.user = user
#         # Save and commit our database models
#         db.session.add_all([user, oauth])
#         db.session.commit()
#         # Log in the new local user account
#         login_user(user, True)
#         flash('You are now logged in. Welcome!', 'success')
#         return redirect(request.args.get('next') or url_for('main.index'))
#
#     # Disable Flask-Dance's default behavior for saving the OAuth token
#     return False


# @oauth_error.connect_via(google_blueprint)
# def google_error(blueprint, error, error_description=None, error_uri=None):
#     msg = (
#         "OAuth error from {name}! "
#         "error={error} description={description} uri={uri}"
#     ).format(
#         name=blueprint.name,
#         error=error,
#         description=error_description,
#         uri=error_uri,
#     )
#     flash(msg, category="error")


# @oauth_authorized.connect_via(facebook_blueprint)
# def facebook_logged_in(blueprint, token):
#     if not token:
#         flash("Failed to log in with Facebook.", category="error")
#         return False

#     resp = blueprint.session.get("/me?fields=name,email,id")
#     if not resp.ok:
#         msg = "Failed to fetch user info from Facebook."
#         flash(msg, category="error")
#         return False

#     facebook_info = resp.json()
#     facebook_user_id = str(facebook_info["id"])

#     # Find this OAuth token in the database, or create it
#     query = OAuth.query.filter_by(
#         provider=blueprint.name,
#         provider_user_id=facebook_user_id,
#     )
#     try:
#         oauth = query.one()
#     except NoResultFound:
#         oauth = OAuth(
#             provider=blueprint.name,
#             provider_user_id=facebook_user_id,
#             token=token,
#         )

#     user = User.query.filter_by(email=facebook_info["email"]).first()

#     if oauth.user:
#         login_user(oauth.user)
#         flash('You are now logged in. Welcome back!', 'success')
#         return redirect(request.args.get('next') or url_for('main.index'))

#     elif user:
#         login_user(user, True)
#         flash('You are now logged in. Welcome back!', 'success')
#         return redirect(request.args.get('next') or url_for('main.index'))

#     else:
#         # Create a new local user account for this user
#         max_id = db.session.query(db.func.max(User.id)).scalar()
#         user = User(
#             id=max_id+1,
#             email=facebook_info["email"],
#             social_id=facebook_info["id"],
#             social_provider="facebook",
#             first_name=facebook_info["name"],
#             confirmed=True)
#         # Associate the new local user account with the OAuth token
#         oauth.user = user
#         # Save and commit our database models
#         db.session.add_all([user, oauth])
#         db.session.commit()
#         # Log in the new local user account
#         login_user(user, True)
#         flash('You are now logged in. Welcome!', 'success')
#         return redirect(request.args.get('next') or url_for('main.index'))

#     # Disable Flask-Dance's default behavior for saving the OAuth token
#     return False


# @oauth_error.connect_via(facebook_blueprint)
# def facebook_error(blueprint, error, error_description=None, error_uri=None):
#     msg = (
#         "OAuth error from {name}! "
#         "error={error} description={description} uri={uri}"
#     ).format(
#         name=blueprint.name,
#         error=error,
#         description=error_description,
#         uri=error_uri,
#     )
#     flash(msg, category="error")


google = oauthclient.remote_app(
    'google',
    consumer_key=os.environ.get('GOOGLE_KEY'),
    consumer_secret=os.environ.get('GOOGLE_SECRET'),
    request_token_params={
        'scope': 'email'
    },
    base_url='https://www.googleapis.com/oauth2/v1/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
)

github = oauthclient.remote_app(
    'github',
    consumer_key=os.environ.get('GITHUB_KEY'),
    consumer_secret=os.environ.get('GITHUB_SECRET'),
    request_token_params={'scope': 'user:email'},
    base_url='https://api.github.com/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://github.com/login/oauth/access_token',
    authorize_url='https://github.com/login/oauth/authorize')

facebook = oauthclient.remote_app(
    'facebook',
    consumer_key=os.environ.get('FACEBOOK_KEY'),
    consumer_secret=os.environ.get('FACEBOOK_SECRET'),
    request_token_params={'scope': 'email'},
    base_url='https://graph.facebook.com',
    request_token_url=None,
    access_token_url='/oauth/access_token',
    access_token_method='GET',
    authorize_url='https://www.facebook.com/dialog/oauth')


@account.route('/google-login-krishna')
def google_login():
    return google.authorize(
        callback=url_for('account.google_authorized', _external=True))

@account.route('/google/authorized')
@google.authorized_handler
def google_authorized(resp):
    if resp is None:
        flash("Failed to log in with Google.", category="error")
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    session['google_token'] = (resp['access_token'], '')
    user_google = google.get('userinfo').data

    # Check if user already exists, else update
    user = User.query.filter_by(email=user_google["email"]).first()

    session['google_token'] = (resp['access_token'], '')
    user_google = google.get('userinfo').data

    # Check if user already exists, else update
    user = User.query.filter_by(email=user_google["email"]).first()

    if user:
        login_user(user, True)
        flash('You are now logged in. Welcome back!', 'success')
        return redirect(request.args.get('next') or url_for('main.index'))

    else:
        # Create a new local user account for this user
        max_id = db.session.query(db.func.max(User.id)).scalar()
        user = User(
            id=max_id+1,
            email=user_google["email"],
            social_id=user_google["id"],
            social_provider="google",
            first_name=user_google["name"],
            confirmed=True)

        # Save and commit our database models
        db.session.add(user)
        db.session.commit()

        session['user_id'] = user.id
        login_user(user, True)
        flash('You are now logged in. Welcome!', 'success')
        return redirect(request.args.get('next') or url_for('main.index'))

    return False
    

@google.tokengetter
def get_google_oauth_token():
    return session.get('google_token')

@account.route('/github-login')
def github_login():
    if 'github_token' in session:
        me = github.get('user')
        email = me.data.get('email')
        name = me.data.get('name')
        user = User.query.filter_by(email=email).first()
        if user is not None:
            login_user(user, True)
            flash('You are now logged in. Welcome back!', 'success')
            return redirect(request.args.get('next') or url_for('main.index'))
        else:
            max_id = db.session.query(db.func.max(User.id)).scalar()
            user = User(
                id=max_id+1,
                email=email,
                social_id=me.data.get('id'),
                social_provider="github",
                username=me.data.get('login'),
                first_name=name,
                confirmed=True)
            db.session.add(user)
            db.session.commit()
            login_user(user, True)
            flash('You are now logged in. Welcome back!', 'success')
            return redirect(request.args.get('next') or url_for('main.index'))
    return github.authorize(
        callback=url_for('account.github_authorized', _external=True))


@account.route('/github/authorized')
def github_authorized():
    resp = github.authorized_response()
    if resp is None or resp.get('access_token') is None:
        return 'Access denied: reason=%s error=%s resp=%s' % (
            request.args['error'], request.args['error_description'], resp)
    session['github_token'] = (resp['access_token'], '')
    return redirect(url_for('account.github_login'))


@github.tokengetter
def get_github_oauth_token():
    return session.get('github_token')

# @account.route('/github-login-krishna')
# def github_login():
#     return github.authorize(
#         callback=url_for('account.github_authorized', _external=True))
#
# @account.route('/github/authorized')
# @github.authorized_handler
# def github_authorized(resp):
#     if resp is None:
#         flash("Failed to log in with github.", category="error")
#         return 'Access denied: reason=%s error=%s' % (
#             request.args['error_reason'],
#             request.args['error_description']
#         )
#     current_app.logger.info(resp)
#     session['github_token'] = (resp['access_token'], '')
#     user_github = github.get('user').data
#
#     # Check if user already exists, else update
#     user = User.query.filter_by(email=user_github["email"]).first()
#
#     if user:
#         login_user(user, True)
#         flash('You are now logged in. Welcome back!', 'success')
#         return redirect(request.args.get('next') or url_for('main.index'))
#
#     else:
#         # Create a new local user account for this user
#         max_id = db.session.query(db.func.max(User.id)).scalar()
#         user = User(
#             id=max_id+1,
#             email=user_github["email"],
#             social_id=user_github["id"],
#             social_provider="github",
#             username=user_github["login"],
#             first_name=user_github["name"],
#             confirmed=True)
#
#         # Save and commit our database models
#         db.session.add(user)
#         db.session.commit()
#
#         session['user_id'] = user.id
#         login_user(user, True)
#         flash('You are now logged in. Welcome!', 'success')
#         return redirect(request.args.get('next') or url_for('main.index'))
#
#     return False
#
# @github.tokengetter
# def get_github_oauth_token():
#     return session.get('github_token')

@account.route('/facebook-login-krishna')
def facebook_login():
    return facebook.authorize(
        callback=url_for('account.facebook_authorized', _external=True))

@account.route('/facebook/authorized')
@facebook.authorized_handler
def facebook_authorized(resp):
    if resp is None:
        flash("Failed to log in with facebook.", category="error")
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    session['facebook_token'] = (resp['access_token'], '')
    user_facebook = facebook.get('/me?fields=name,email,id').data

    # Check if user already exists, else update
    user = User.query.filter_by(email=user_facebook["email"]).first()

    if user:
        login_user(user, True)
        flash('You are now logged in. Welcome back!', 'success')
        return redirect(request.args.get('next') or url_for('main.index'))

    else:
        # Create a new local user account for this user
        max_id = db.session.query(db.func.max(User.id)).scalar()
        user = User(
            id=max_id+1,
            email=user_facebook["email"],
            social_id=user_facebook["id"],
            social_provider="facebook",
            first_name=user_facebook["name"],
            confirmed=True)

        # Save and commit our database models
        db.session.add(user)
        db.session.commit()

        session['user_id'] = user.id
        login_user(user, True)
        flash('You are now logged in. Welcome!', 'success')
        return redirect(request.args.get('next') or url_for('main.index'))

    return False

@facebook.tokengetter
def get_facebook_oauth_token():
    return session.get('facebook_token')


@account.route('/login', methods=['GET', 'POST'])
def login():
    """Log in an existing user."""
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.password_hash is not None and \
                user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            flash('You are now logged in. Welcome back!', 'success')
            return redirect(request.args.get('next') or url_for('main.index'))
        else:
            flash('Invalid email or password.', 'form-error')
    return render_template('account/login.html', form=form)


@account.route('/register', methods=['GET', 'POST'])
def register():
    """Register a new user, and send them a confirmation email."""
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            password=form.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        confirm_link = url_for('account.confirm', token=token, _external=True)
        send_email(
            recipient=user.email,
            subject='Confirm Your Account',
            template='account/email/confirm',
            user=user,
            confirm_link=confirm_link)
        flash('A confirmation link has been sent to {}.'.format(user.email),
              'warning')
        return redirect(url_for('main.index'))
    return render_template('account/register.html', form=form)


@account.route('/logout')
@login_required
def logout():
    session.pop('google_token', None)
    session.pop('github_token', None)
    session.pop('facebook_token', None)
    session.pop('user_id', None)
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))


@account.route('/manage', methods=['GET', 'POST'])
@account.route('/manage/info', methods=['GET', 'POST'])
@login_required
def manage():
    """Display a user's account information."""
    return render_template('account/manage.html', user=current_user, form=None)


@account.route('/reset-password', methods=['GET', 'POST'])
def reset_password_request():
    """Respond to existing user's request to reset their password."""
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = RequestResetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.generate_password_reset_token()
            reset_link = url_for(
                'account.reset_password', token=token, _external=True)
            send_email(
                recipient=user.email,
                subject='Reset Your Password',
                template='account/email/reset_password',
                user=user,
                reset_link=reset_link,
                next=request.args.get('next'))
        flash('A password reset link has been sent to {}.'.format(
            form.email.data), 'warning')
        return redirect(url_for('account.login'))
    return render_template('account/reset_password.html', form=form)


@account.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Reset an existing user's password."""
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            flash('Invalid email address.', 'form-error')
            return redirect(url_for('main.index'))
        if user.reset_password(token, form.new_password.data):
            flash('Your password has been updated.', 'form-success')
            return redirect(url_for('account.login'))
        else:
            flash('The password reset link is invalid or has expired.',
                  'form-error')
            return redirect(url_for('main.index'))
    return render_template('account/reset_password.html', form=form)


@account.route('/manage/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change an existing user's password."""
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.new_password.data
            db.session.add(current_user)
            db.session.commit()
            flash('Your password has been updated.', 'form-success')
            return redirect(url_for('main.index'))
        else:
            flash('Original password is invalid.', 'form-error')
    return render_template('account/manage.html', form=form, user=current_user)


@account.route('/manage/change-email', methods=['GET', 'POST'])
@login_required
def change_email_request():
    """Respond to existing user's request to change their email."""
    form = ChangeEmailForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            new_email = form.email.data
            token = current_user.generate_email_change_token(new_email)
            change_email_link = url_for(
                'account.change_email', token=token, _external=True)
            send_email(
                recipient=new_email,
                subject='Confirm Your New Email',
                template='account/email/change_email',
                # current_user is a LocalProxy, we want the underlying user
                # object
                user=current_user._get_current_object(),
                change_email_link=change_email_link)
            flash('A confirmation link has been sent to {}.'.format(new_email),
                  'warning')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid email or password.', 'form-error')
    return render_template('account/manage.html', form=form, user=current_user)


@account.route('/manage/change-email/<token>', methods=['GET', 'POST'])
@login_required
def change_email(token):
    """Change existing user's email with provided token."""
    if current_user.change_email(token):
        flash('Your email address has been updated.', 'success')
    else:
        flash('The confirmation link is invalid or has expired.', 'error')
    return redirect(url_for('main.index'))


@account.route('/confirm-account')
@login_required
def confirm_request():
    """Respond to new user's request to confirm their account."""
    token = current_user.generate_confirmation_token()
    confirm_link = url_for('account.confirm', token=token, _external=True)
    send_email(
        recipient=current_user.email,
        subject='Confirm Your Account',
        template='account/email/confirm',
        # current_user is a LocalProxy, we want the underlying user object
        user=current_user._get_current_object(),
        confirm_link=confirm_link)
    flash('A new confirmation link has been sent to {}.'.format(
        current_user.email), 'warning')
    return redirect(url_for('main.index'))


@account.route('/confirm-account/<token>')
@login_required
def confirm(token):
    """Confirm new user's account with provided token."""
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm_account(token):
        flash('Your account has been confirmed.', 'success')
    else:
        flash('The confirmation link is invalid or has expired.', 'error')
    return redirect(url_for('main.index'))


@account.route(
    '/join-from-invite/<int:user_id>/<token>', methods=['GET', 'POST'])
def join_from_invite(user_id, token):
    """
    Confirm new user's account with provided token and prompt them to set
    a password.
    """
    if current_user is not None and current_user.is_authenticated:
        flash('You are already logged in.', 'error')
        return redirect(url_for('main.index'))

    new_user = User.query.get(user_id)
    if new_user is None:
        return redirect(404)

    if new_user.password_hash is not None:
        flash('You have already joined.', 'error')
        return redirect(url_for('main.index'))

    if new_user.confirm_account(token):
        form = CreatePasswordForm()
        if form.validate_on_submit():
            new_user.password = form.password.data
            db.session.add(new_user)
            db.session.commit()
            flash('Your password has been set. After you log in, you can '
                  'go to the "Your Account" page to review your account '
                  'information and settings.', 'success')
            return redirect(url_for('account.login'))
        return render_template('account/join_invite.html', form=form)
    else:
        flash('The confirmation link is invalid or has expired. Another '
              'invite email with a new link has been sent to you.', 'error')
        token = new_user.generate_confirmation_token()
        invite_link = url_for(
            'account.join_from_invite',
            user_id=user_id,
            token=token,
            _external=True)
        send_email(
            recipient=new_user.email,
            subject='You Are Invited To Join',
            template='account/email/invite',
            user=new_user,
            invite_link=invite_link)
    return redirect(url_for('main.index'))


@account.before_app_request
def before_request():
    """Force user to confirm email before accessing login-required routes."""
    if current_user.is_authenticated \
            and not current_user.confirmed \
            and request.endpoint[:8] != 'account.' \
            and request.endpoint != 'static':
        return redirect(url_for('account.unconfirmed'))


@account.route('/unconfirmed')
def unconfirmed():
    """Catch users with unconfirmed emails."""
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('account/unconfirmed.html')


@account.route('/manage/apps/new', methods=['GET', 'POST'])
@login_required
def create_app():
    form = CreateAppForm()
    if form.validate_on_submit():
        app = App(
            application_id=gen_salt(10),
            application_name=form.application_name.data,
            application_description=form.application_description.data,
            application_website=form.application_website.data,
            user_id=current_user.id)
        db.session.add(app)
        db.session.flush()

        item = Client(
            client_id=gen_salt(40),
            client_secret=gen_salt(50),
            _default_scopes='verse chapter',
            user_id=current_user.id,
            app_id=app.application_id)
        db.session.add(item)
        db.session.commit()

        send_email(
            recipient=current_user.email,
            subject='Application Successfully Registered',
            template='account/email/confirm_app',
            user=current_user._get_current_object(),
            app_name=form.application_name.data)

        flash('You application has been created.', 'success')
        return redirect(
            url_for('account.update_app', application_id=app.application_id))
    return render_template(
        'account/create_app.html', user=current_user._get_current_object(), form=form)


@account.route('/manage/apps/<string:application_id>', methods=['GET', 'POST'])
@login_required
def update_app(application_id):
    app = App.query.filter_by(application_id=application_id).first()
    client = Client.query.filter_by(app_id=application_id).first()
    client_id = client.client_id
    client_secret = client.client_secret
    form_dict = {}
    form_dict['application_name'] = app.application_name
    form_dict['application_description'] = app.application_description
    form_dict['application_website'] = app.application_website
    form = UpdateAppForm(**form_dict)
    if form.validate_on_submit():
        app.application_name = form.application_name.data
        app.application_description = form.application_description.data
        app.application_website = form.application_website.data
        db.session.commit()

        flash('You application has been updated.', 'success')
        return redirect(url_for('account.all_apps'))
    return render_template(
        'account/update_app.html',
        user=current_user,
        form=form,
        app_name=form_dict['application_name'],
        client_id=client_id,
        client_secret=client_secret)


@account.route('/manage/apps', methods=['GET', 'POST'])
@login_required
def all_apps():
    if current_user.is_anonymous or current_user.confirmed:
        apps_list = App.query.filter_by(user_id=current_user.id).all()
        current_app.logger.info(apps_list)
        return render_template(
            'account/all_apps.html', user=current_user, apps_list=apps_list)
    return redirect(url_for('account.unconfirmed'))


@account.route(
    '/manage/apps/<string:application_id>/delete', methods=['GET', 'POST'])
@login_required
def delete_app(application_id):
    client = Client.query.filter_by(app_id=application_id).first()
    Token.query.filter_by(client_id=client.client_id).delete()
    Client.query.filter_by(app_id=application_id).delete()
    App.query.filter_by(application_id=application_id).delete()
    db.session.commit()
    flash('You application has been deleted.', 'success')
    return redirect(url_for('account.all_apps'))
