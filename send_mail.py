# coding: utf-8
# vim: set fenc=utf-8 ft=python ts=4 sts=4 sw=4 ai et
"""
    send_mail
    ---------

    Email sending module for scripts.

    :copyright: Copyright 2017-2018 by Paulo Phagula.
    :license: MIT, see LICENSE for details.
"""
from __future__ import unicode_literals, print_function
import os
import re
import smtplib
from email.utils import COMMASPACE, formatdate, formataddr, make_msgid

import six
import html2text

if six.PY2:
    from email.MIMEMultipart import MIMEMultipart
    from email.MIMEBase import MIMEBase
    from email.MIMEText import MIMEText
    from email import Encoders as encoders
    from email import charset
if six.PY3:
    from email.mime.multipart import MIMEMultipart
    from email.mime.base import MIMEBase
    from email.mime.text import MIMEText
    from email import encoders
    from email import charset



# least buggy regex from http://www.regular-expressions.info/email.html
MAIL_ADDRESS_RE = re.compile(r'\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b', re.I)


def _is_valid_mail_address(address):
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
            or not _is_valid_mail_address(address[1])
    ):
        return False

    return True


def _parse_mail_address(address):
    """Makes email address into parseable format"""
    if not _is_valid_mail_address(address):
        raise Exception('cannot make parseable mail address: "%s" from invalid address' % address)

    if isinstance(address, six.string_types):
        return False, address

    if isinstance(address, tuple):
        return address


def _parse_multiple_mail_addresses(addresses):
    """Parses multiple mail addresses into final format"""
    addresses = addresses if isinstance(addresses, list) else list(map(six.text_type.strip, addresses.split(',')))
    for key, mail_address in enumerate(addresses):
        if not _is_valid_mail_address(mail_address):
            raise Exception('Invalid Address: "%s"' % six.text_type(mail_address))
        else:
            addresses[key] = _parse_mail_address(mail_address)

    return addresses


def send_mail(
        subject,
        message='', html_message='',
        to=None, cc=None, bcc=None,
        sender=None, reply_to=None,
        attachments=None,
        custom_headers=None,
        logger=None,
        **kwargs
):
    """Sends an email.

    Single emails addresses can be provided as strings like `'pphagula@gmail.com'`
    or name-address tuples like `('Paulo Phagula', 'pphagula@gmail.com'')`

    Multiple email addresses can be provided as CSV strings like `'email@example.com, email2@example.com'`
    or lists mixing singular address style `['email@example.com', (Example, email@example.com)]`

    Attachments can be passed as a CSV string with full paths to the
    desired files.

    Args:
        subject (:obj:`str`): Subject line for this e-mail message.
        message (:obj:`str`): Plain-text message body.
        html_message (:obj:`str`): HTML message body.
        to: Recipients address collection
        cc: Carbon Copy (CC) recipients address collection
        bcc: Blind Carbon Copy (BCC) recipients address collection
        sender: Sender email address as it appears in the 'From' email line.
        reply_to: List of addresses to reply to for the mail message.
        attachments: Attachments collection used to store data
            attached to this e-mail message.
        custom_headers (:obj:`dict`, optional): Custom Headers to be added to the mail.
        logger (:obj:`logging.Logger`,optional): Logger instance for logging
            error and debug messages.
        **kwargs: Arbitrary keywords arguments

            If any of them is not provided they will be taken from
            their environment variables equivalents (SMTP_<KEYWORD>) or
            use default values.

            - host (:obj:`str`, optional): mail server host. If not given uses :envvar:`SMTP_HOST`.
            - port (:obj:`str` or :obj:`int`, optional): mail server port. If not given uses :envvar:`SMTP_PORT`.
            - username (:obj:`str`, optional): mail server password. If not given uses :envvar:`SMTP_USERNAME`.
            - password (:obj:`str`, optional): mail server password. If not given uses :envvar:`SMTP_PASSWORD`.
            - use_tls (:obj:`bool`, optional): connect using TLS flag. If not given uses :envvar:`SMTP_USE_TLS`. Defaults to False
            - use_ssl (:obj:`bool`, optional): connect using SSL flag. If not given uses :envvar:`SMTP_USE_SSL`.  Defaults to False
            - debug (:obj:`bool`, optional): debug mode enabling flag. If not given uses :envvar:`SMTP_DEBUG`.Defaults to False

    Raises:
        ValueError: if no recipient is given or no message is given.

    .. envvar:: SMTP_HOST
        Mail server host.

    .. envvar:: SMTP_PORT
        Mail server port.

    .. envvar:: SMTP_USERNAME
        Mail server username for login.

    .. envvar:: SMTP_PASSWORD
        Mail server password for login.

    .. envvar:: SMTP_USE_TLS
        Flag indicating if connection should be made using TLS.

    .. envvar:: SMTP_USE_SSL
        Flag indicating if connection to server should be made using SSL.

    .. envvar:: SMTP_DEBUG
        Flag indicating if debug mode is enabled.abs
    """

    # 1. Parse and Validate Email details

    if sender:
        sender = _parse_mail_address(sender)

    if reply_to:
        reply_to = _parse_multiple_mail_addresses(reply_to)

    all_destinations = []

    if to:
        to = _parse_multiple_mail_addresses(to)
        all_destinations.extend(to)

    if cc:
        cc = _parse_multiple_mail_addresses(cc)
        all_destinations.extend(cc)

    if bcc:
        bcc = _parse_multiple_mail_addresses(cc)
        all_destinations.extend(bcc)

    if len(all_destinations) == 0:
        raise ValueError('At least one recipient must be specified')

    if message and not isinstance(message, six.text_type):
        raise ValueError('message must be a string')

    if html_message and not isinstance(html_message, six.text_type):
        raise ValueError('html_message must be a string')

    # 2. Setup email object with basic details

    mail = MIMEMultipart()
    body = MIMEMultipart('alternative')

    html2text_converter = html2text.HTML2Text()

    if sender:
        mail['From'] = formataddr(sender)

    if to:
        mail['To'] = COMMASPACE.join(list(map(formataddr, to)))

    if cc:
        mail['Cc'] = COMMASPACE.join(list(map(formataddr, cc)))

    if reply_to:
        mail['Reply-To'] = COMMASPACE.join(list(map(formataddr, reply_to)))

    mail['Date'] = formatdate(localtime=True)
    mail['Message-ID'] = make_msgid()
    mail['Subject'] = subject
    mail.preamble = subject

    if html_message and not message:
        message = html2text_converter.handle(message)

    # Add missing charset email charset and email encodings
    # https://stackoverflow.com/questions/9403265/how-do-i-use-python-3-2-email-module-to-send-unicode-messages-encoded-in-utf-8-w
    charset.add_charset('utf-8', charset.QP, charset.QP)

    # NOTE: We must always attach plain text mail before html, otherwise we'll break Gmail
    if message:
        body.attach(MIMEText(message, 'plain', 'utf-8'))

    if html_message:
        body.attach(MIMEText(html_message, 'html', 'utf-8'))

    mail.attach(body)

    # 3. Add attachments to email

    if attachments:
        attachments = attachments if isinstance(attachments, list) else list(map(six.text_type.strip, attachments.split(',')))
        for file_path in attachments:
            try:
                if not os.path.isfile(file_path):
                    raise ValueError('File for attachment "%s" not found in file system' % six.text_type(file_path))

                with open(file_path, 'rb') as f:
                    attachment = MIMEBase('application', "octet-stream")
                    attachment.set_payload(f.read())
                    encoders.encode_base64(attachment)
                    file_name = os.path.basename(file_path)
                    attachment.add_header('Content-Disposition', 'attachment; filename="%s"' % file_name)
                    mail.attach(attachment)
            except Exception as ex:
                if logger is not None:
                    logger.error("Unable to open one of the attachments. Error: %s" % six.text_type(ex))
                raise

    # 4. Add custom headers to email

    if custom_headers:
        for k, v in six.iteritems(custom_headers):
            mail.add_header(k, v)

    # 5. Connect to mail server and send email

    host = kwargs.get('host', None) or os.getenv('SMTP_HOST')
    port = kwargs.get('port', None) or os.getenv('SMTP_PORT')
    port = int(port)
    username = kwargs.get('username', None) or os.getenv('SMTP_USERNAME')
    password = kwargs.get('password', None) or os.getenv('SMTP_PASSWORD')
    use_tls = kwargs.get('use_tls', False) or os.getenv('SMTP_USE_TLS', False)
    use_ssl = kwargs.get('use_ssl', False) or os.getenv('SMTP_USE_SSL', False)
    debug = kwargs.get('debug', False) or os.getenv('SMTP_DEBUG', False)

    if six.PY2:
        password = six.binary_type(password)

    if use_tls in ("False", "false"):
        use_tls = False

    if use_ssl in ("False", "false"):
        use_ssl = False

    if debug in ("False", "false"):
        debug = False

    try:
        # this doesn't support `with` statement so we do `close` the old way.
        mail_server = smtplib.SMTP_SSL(host, port) if use_ssl else smtplib.SMTP(host, port)

        if debug:
            mail_server.set_debuglevel(1)

        mail_server.ehlo()  # identify ourselves, prompting server for supported features

        if use_tls:
            mail_server.starttls()
            mail_server.ehlo()  # re-identify ourselves over TLS connection

        mail_server.login(username, password)
        mail_server.sendmail(subject, list(map(lambda x: x[1], all_destinations)), mail.as_string())
        # Should be mailServer.quit(), but that crashes...
        mail_server.close()
    except Exception as ex:
        if logger is not None:
            logger.error("Unable to send the email. Error: %s" % str(ex))
        raise
