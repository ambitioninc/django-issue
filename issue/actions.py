from django.core.mail import EmailMultiAlternatives


def email(issue, subject, recipients, message_txt=None, message_html=None, reply_address=None):
    """
    """
    message_txt = message_txt or ''
    reply_address = reply_address or ''

    email = EmailMultiAlternatives(subject, message_txt, reply_address, recipients)

    if message_html:
        email.attach_alternative(message_html, 'text/html')

    email.send()
