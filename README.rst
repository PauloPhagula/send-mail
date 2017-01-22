**********
send_mail
**********

e-mail sending module.

Code Example
==============

.. code:: python

    PLAINTEXT_EMAIL = """
    Yo...
    """

    send_mail(
        '[AwesomeApp] very descriptive subject',
        message=PLAINTEXT_EMAIL,
        to=[('To Example', 'to@example.com'), 'you@example.com'],
        cc='him@example.com, her@example.com',
        bcc=['them@example.com', ('You Know Who', 'youknowwho@example.com')],
        sender=('AwesomeApp', 'notifications@example.com'),
        reply_to='no-reply@example.com',
        attachments=['/full/path/to/attachment.ext']
    )

.. attention::

    In order to send the e-mail the function requires your server details.
    You can put these details in
    ``SMTP_HOST, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD, SMTP_USE_SSL & SMTP_USE_TLS``
    environment variables, or pass them as keyword arguments without the
    *smpt_* prefix.

Installation
==============

You can install this module directly from github with

``pip install -e git+https://github.com/dareenzo/send_mail@v0.3.0#egg=send_mail``

Testing
========

Unit tests are provided with the code and you can run them by copying
the ``.env.example`` file into a ``.env`` file on the root of the
project.

The ``.env`` file contains the required environment variables for the
module. So update it with your own settings.
These setting will be read by the ``cheap_dot_env`` function into
environment variables before each test so that the ``send_mail``
function can work properly

.. code-block:: sh
    :linenos:

    cp .env.example .env
    # edit .env file with your mail settings
    pip install -r requirements/test.txt
    tox

Documentation Generation
=========================

.. code-block:: sh
    :linenos:

    # edit documentation in _docs
    cd _docs
    make singlehtml
    cd ..
    cp -fR _docs/_build/singlehtml/* docs/

Copyright & License
=====================

Code and documentation are available according to the MIT License.

See the `LICENSE`_ file for details.

.. _LICENSE: http://www.github.com/dareenzo/send_mail/blob/master/LICENSE
