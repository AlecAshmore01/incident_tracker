import io
import base64

import pyotp
import qrcode
from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    current_app,
    session,
)
from flask_login import login_user, logout_user, login_required, current_user
from flask_mail import Message

from app.auth.forms import RegistrationForm, LoginForm, OTPForm, ResetPasswordRequestForm, ResetPasswordForm
from app.extensions import db, bcrypt, limiter, mail
from app.models.user import User

auth_bp = Blueprint('auth', __name__, template_folder='templates/auth')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register() -> str:
    form = RegistrationForm()
    if form.validate_on_submit():
        # Hash the password with Bcrypt
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(
            username=form.username.data,
            email=form.email.data,
            role='regular'
        )
        user.password_hash = hashed_pw
        db.session.add(user)
        db.session.commit()

        current_app.logger.info(f'New user registered: {user.username}')
        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("10 per minute")  # Prevent brute-force
def login() -> str:
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        # 1) Check for account lockout
        if user and user.is_locked():
            flash(
                f"Account locked until {user.lock_until.strftime('%H:%M on %Y-%m-%d')}.",
                'danger'
            )
            return render_template('auth/login.html', form=form)

        # 2) Verify credentials
        if user and bcrypt.check_password_hash(user.password_hash, form.password.data):
            # If 2FA not yet configured, generate secret and go to setup
            if not user.otp_secret:
                user.generate_otp_secret()
                session['pre_2fa_user'] = user.id
                return redirect(url_for('auth.two_factor_setup'))

            # Otherwise go to verification
            session['pre_2fa_user'] = user.id
            return redirect(url_for('auth.two_factor_verify'))

        # 3) Failed login: increment and possibly lock
        if user:
            user.register_failed_login(max_attempts=5, lock_minutes=1)
        flash('Invalid username or password.', 'danger')

    return render_template('auth/login.html', form=form)


@auth_bp.route('/2fa-setup')
def two_factor_setup() -> str:
    user_id = session.get('pre_2fa_user')
    if not user_id:
        return redirect(url_for('auth.login'))

    user = User.query.get(user_id)
    # Generate provisioning URI and QR code
    uri = user.get_totp_uri()
    img = qrcode.make(uri)
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    img_b64 = base64.b64encode(buf.getvalue()).decode('utf-8')

    return render_template(
        'auth/2fa_setup.html',
        qr_data=f"data:image/png;base64,{img_b64}"
    )


@auth_bp.route('/2fa-verify', methods=['GET', 'POST'])
def two_factor_verify() -> str:
    user_id = session.get('pre_2fa_user')
    if not user_id:
        return redirect(url_for('auth.login'))

    user = User.query.get(user_id)
    form = OTPForm()
    if form.validate_on_submit():
        token = form.token.data
        totp = pyotp.TOTP(user.otp_secret)
        if totp.verify(token):
            # Successful 2FA: complete login
            login_user(user)
            user.reset_failed_logins()
            session.pop('pre_2fa_user', None)
            current_app.logger.info(f'2FA successful for user {user.username}')
            return redirect(url_for('main.index'))
        flash('Invalid authentication code.', 'danger')

    return render_template('auth/2fa_verify.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout() -> str:
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))


@auth_bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.get_reset_password_token()
            # send email
            msg = Message(
                subject="Password Reset Request",
                recipients=[user.email]
            )
            msg.html = render_template(
                'email/reset_password.html',
                user=user,
                token=token
            )
            mail.send(msg)
        # Do not reveal whether email is registered
        flash(
            'If an account with that email exists, '
            'you will receive a password‐reset email shortly.',
            'info'
        )
        return redirect(url_for('auth.login'))
    return render_template(
        'auth/reset_password_request.html',
        form=form
    )


@auth_bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    user = User.verify_reset_password_token(token)
    if not user:
        flash('The reset link is invalid or has expired.', 'warning')
        return redirect(url_for('auth.reset_password_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset. You can now log in.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)