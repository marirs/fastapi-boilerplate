"""
Send Email
"""
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from server.core.settings import FROM_EMAIL, SG_API
import ssl

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    # Legacy Python that doesn't verify HTTPS certificates by default
    pass
else:
    # Handle target environment that doesn't support HTTPS verification
    ssl._create_default_https_context = _create_unverified_https_context


async def _send_email(msg):
    """Send an email using Sendgrid
    """
    try:
        sg = SendGridAPIClient(SG_API)
        response = sg.send(msg)
        return response
    except Exception as e:
        print(e)
        return None


async def verification_email(api_key, email_address):
    """Send verification email when an account gets created
    :param api_key: an api key that needs to be sent
    :param email_address: To email address
    """
    verification_email = f'<strong>CDE API Key</strong><p>Your CDE API Key is: \
    <b>{api_key}</b><br/>Verify your email address to start using your API key:&nbsp;\
    https://cde.to/api/user/verify?email={email_address}</p><p>Please do not loose your \
    api key, as the key is not stored in our system.</p><p>If you loose your api key, \
    you would need to reset your API key by following the link below:<br>\
    https://cde.to/api/user/reset?email={email_address}</p>'

    if not SG_API:
        return

    message = Mail(
        from_email=FROM_EMAIL,
        to_emails=email_address,
        subject='[CDE] Verification Email',
        html_content=verification_email
    )
    response = await _send_email(message)


async def reset_email(api_key, email_address):
    """Send API Reset email when a API reset is required
    :param api_key: an api key that needs to be sent
    :param email_address: To email address
    """
    reset_email = f'<strong>CDE API Key Reset</strong><p> You are someone has requested an reset of \
    your API Key for your email address<br/>Your new API Key is: <b>{api_key}</b></p><p>Please update \
    any or all of your scripts with your new API Key.'

    if not SG_API:
        return

    message = Mail(
        from_email=FROM_EMAIL,
        to_emails=email_address,
        subject="[CDE] API Reset Email",
        html_content=reset_email
    )
    response = await _send_email(message)
