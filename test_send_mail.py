# coding: utf-8
# vim: fenc=utf-8 ft=python ts=4 sts=4 sw=4 ai et
from __future__ import unicode_literals, print_function
import unittest
import os
import codecs

from send_mail import send_mail


PLAINTEXT_EMAIL = """
Yo...
"""
EMAIL_TEMPLATE = """
<html>
    <head></head>
    <body>
        <h1>Hello, Welcome to the mailing group</h1>
        <p>See you in the inbox</p>
        <br/>
        <br/>
        </p>Regards</p>
    </body>
</html>
"""


def cheap_dot_env(dot_env_path):
    """Help fn to load constants from file into env vars"""
    if os.path.exists(dot_env_path):
        with codecs.open(dot_env_path, encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if len(line) == 0 or line.startswith(';') or line.startswith('#'):
                    continue
                var = line.replace('"', '')
                var = line.strip().split('=')
                if len(var) == 2:
                    key = var[0]
                    value = var[1].replace('"', '').strip()
                    os.environ[key] = value
    else:
        raise Exception('no dot env file')


class MailTestCase(unittest.TestCase):

    def setUp(self):
        if not os.getenv('TEST_ENV') == 'travis':
            cheap_dot_env(os.path.join(os.path.abspath(os.path.dirname(__file__)), '.env'))

    def test_full_email_is_sent(self):
        send_mail(
            '[Mail Test] I should be delivered to the inbox',
            message=PLAINTEXT_EMAIL,
            html_message=EMAIL_TEMPLATE,
            to=[('To Example', 'to@example.com'), 'you@example.com'],
            cc='him@example.com, her@example.com',
            bcc=['them@example.com', ('You Know Who', 'youknowwho@example.com')],
            sender=('App', 'notifications@example.com'),
            reply_to='no-reply@example.com',
            attachments=[os.path.abspath(os.path.dirname(__file__)) + '/LICENSE',
                         os.path.abspath(os.path.dirname(__file__)) + '/README.rst']
        )

    def test_full_email_is_sent_with_details_as_keywords(self):

        host = os.getenv('SMTP_HOST')
        port = os.getenv('SMTP_PORT')
        username = os.getenv('SMTP_USERNAME')
        password = os.getenv('SMTP_PASSWORD')
        use_tls = os.getenv('SMTP_USE_TLS')

        send_mail(
            '[Mail Test] I should be delivered to the inbox',
            message=PLAINTEXT_EMAIL,
            html_message=EMAIL_TEMPLATE,
            to=[('To Example', 'to@example.com'), 'you@example.com'],
            cc='him@example.com, her@example.com',
            bcc=[
                'them@example.com',
                ('You Know Who', 'youknowwho@example.com')
            ],
            sender=('App', 'notifications@example.com'),
            reply_to='no-reply@example.com',
            attachments=[
                os.path.abspath(os.path.dirname(__file__)) + '/LICENSE',
                os.path.abspath(os.path.dirname(__file__)) + '/README.rst'
            ],
            host=host,
            port=port,
            username=username,
            password=password,
            use_tls=use_tls
        )



if __name__ == '__main__':
    unittest.main()
