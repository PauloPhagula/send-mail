# coding: utf-8
# vim: fenc=utf-8 ft=python ts=4 sts=4 sw=4 ai et
"""
    send_mail
    ---------

    Email sending module for scripts.

    :copyright: (c) 2017 by Paulo Phagula.
    :license: MIT, see LICENSE for more details.
"""
from __future__ import unicode_literals, print_function
import os
import logging
import re
import smtplib
from email.utils import COMMASPACE, formatdate, formataddr

import six
import html2text

if six.PY2:
    from email.MIMEMultipart import MIMEMultipart
    from email.MIMEBase import MIMEBase
    from email.MIMEText import MIMEText
    from email import Encoders as encoders
if six.PY3:
    from email.mime.multipart import MIMEMultipart
    from email.mime.base import MIMEBase
    from email.mime.text import MIMEText
    from email import encoders


# least buggy regex from http://www.regular-expressions.info/email.html
MAIL_ADDRESS_RE = re.compile(r'\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b', re.I)


def is_valid_mail_address(address):
    """Verifies if email address is valid"""
    if not address:
        return False

    if not isinstance(address, (six.string_types, tuple)):
        return False

    if isinstance(address, six.string_types) and not MAIL_ADDRESS_RE.match(address):
        return False

    if isinstance(address, tuple) and (
            len(address) != 2
            or not isinstance(address[0], (six.string_types, bool))
            or not isinstance(address[1], six.string_types)
            or not is_valid_mail_address(address[1])
    ):
        return False

    return True


def to_parseable_mail_address(address):
    """Makes email address into parseable format"""
    if not is_valid_mail_address(address):
        raise Exception('cannot make parseable mail address: "%s" from invalid address' % address)

    if isinstance(address, six.string_types):
        return False, address

    if isinstance(address, tuple):
        return address


def send_mail(to, subject, message, is_html=False, cc=None, bcc=None,
              reply_to=None, attachments=None, sender=None, text=None,
              custom_headers=None, **kwargs):
    """Send an outgoing email with the given parameters.

    Single emails addresses can be provided a string `'email@example.com'`
    or tuples of `('Example', 'email@example.com'')`

    Multiple email addresses can be provided CSV `'email@example.com, email2@example.com'`
    or lists mixing singular address style `['email@example.com', (Example, email@example.com)]`

    By default emails are considered to be in plain-text format, but one can change
    them to HTML by passing `is_html=True`.

    When sending an HTML email a plain-text fallback can be provided with the
    `text` parameter, and if a fallback is not provided the conversion will be
    done for you based on the HTML message.

    Attachments can be passed as a CSV string with full paths to the desired files.
    """
    mail = MIMEMultipart()
    body = MIMEMultipart('alternative')

    logger = logging.getLogger()
    html2text_converter = html2text.HTML2Text()

    if sender:
        sender = to_parseable_mail_address(sender)

    if reply_to:
        reply_to = to_parseable_mail_address(reply_to)

    to = to if isinstance(to, list) else list(map(six.text_type.strip, to.split(',')))
    for key, mail_address in enumerate(to):
        if not is_valid_mail_address(mail_address):
            raise Exception('Invalid Address "%s" in To' % six.text_type(mail_address))
        else:
            to[key] = to_parseable_mail_address(mail_address)

    if cc:
        cc = cc if isinstance(cc, list) else list(map(six.text_type.strip, cc.split(',')))
        for key, mail_address in enumerate(cc):
            if not is_valid_mail_address(mail_address):
                raise Exception('Invalid Address: "%s" in Cc' % six.text_type(mail_address))
            else:
                cc[key] = to_parseable_mail_address(mail_address)

    if bcc:
        bcc = bcc if isinstance(bcc, list) else list(map(six.text_type.strip, bcc.split(',')))
        for key, mail_address in enumerate(bcc):
            if not is_valid_mail_address(mail_address):
                raise Exception('Invalid Address: "%s" in Bcc' % six.text_type(mail_address))
            else:
                bcc[key] = to_parseable_mail_address(mail_address)

    if sender:
        mail['From'] = formataddr(sender)

    if to:
        mail['To'] = COMMASPACE.join(list(map(formataddr, to)))

    if cc:
        mail['Cc'] = COMMASPACE.join(list(map(formataddr, cc)))

    if reply_to:
        mail['Reply-To'] = formataddr(reply_to)

    mail['Date'] = formatdate(localtime=True)
    mail['Subject'] = subject
    mail.preamble = subject

    if not is_html:
        body.attach(MIMEText(message, 'plain', 'utf-8'))
    else:
        if text:
            body.attach(MIMEText(text, 'plain', 'utf-8'))
        else:
            body.attach(MIMEText(html2text_converter.handle(message), 'plain', 'utf-8'))

        body.attach(MIMEText(message, 'html', 'utf-8'))

    mail.attach(body)

    if attachments:
        attachments = attachments if isinstance(attachments, list) else list(map(six.text_type.strip, attachments.split(',')))
        for file_path in attachments:
            try:
                if not os.path.isfile(file_path):
                    raise Exception('File for attachment "%s" not found in file system' % six.text_type(file_path))
                with open(file_path, 'rb') as f:
                    attachment = MIMEBase('application', "octet-stream")
                    attachment.set_payload(f.read())
                    encoders.encode_base64(attachment)
                    file_name = os.path.basename(file_path)
                    attachment.add_header('Content-Disposition', 'attachment; filename="%s"' % file_name)
                    mail.attach(attachment)
            except Exception as ex:
                logger.error("Unable to open one of the attachments. Error: %s" % six.text_type(ex))
                raise

    if custom_headers:
        for k, v in custom_headers.iteritems():
            mail.add_header(k, v)

    all_destinations = []
    if to:
        all_destinations.extend(to)
    if cc:
        all_destinations.extend(cc)
    if bcc:
        all_destinations.extend(bcc)


    host = kwargs.get('host', None) or os.getenv('SMTP_HOST')
    port = kwargs.get('port', None) or os.getenv('SMTP_PORT')
    port = int(port)
    username = kwargs.get('username', None) or os.getenv('SMTP_USERNAME')
    password = kwargs.get('password', None) or os.getenv('SMTP_PASSWORD')
    if six.PY2:
        password = six.binary_type(password)
    use_tls = kwargs.get('use_tls', None) or os.getenv('SMTP_USE_TLS')

    try:
        # this doesn't support `with` statement so we do `close` the old way.
        mail_server = smtplib.SMTP(host, port)
        mail_server.ehlo()
        if use_tls:
            mail_server.starttls()
        mail_server.ehlo()
        mail_server.login(username, password)
        mail_server.sendmail(subject, list(map(lambda x: x[1], all_destinations)), mail.as_string())
        # Should be mailServer.quit(), but that crashes...
        mail_server.close()
    except Exception as ex:
        logger.error("Unable to send the email. Error: %s" % str(ex))
        raise
