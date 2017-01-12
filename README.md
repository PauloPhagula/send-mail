# send_mail

Email sending module for scripts.

## Usage

Put `SMTP_HOST, SMTP_PORT, SMTP_USE_TLS, SMTP_USERNAME & SMTP_PASSWORD`
in environment variables so module can pick up or pass them as
keyword arguments dropping the *smpt_* prefix.

```python
HTML_EMAIL = """
<html>...
</html>
"""

PLAINTEXT_EMAIL = """
Yo...
"""

send_mail(
    [('To Example', 'to@example.com'), 'you@example.com'],
    '[AwesomeApp] very descriptive subject',
    HTML_EMAIL,
    is_html=True,
    cc='him@example.com, her@example.com',
    bcc=['them@example.com', ('You Know Who', 'youknowwho@example.com')],
    sender=('AwesomeApp', 'notifications@example.com'),
    reply_to='no-reply@example.com',
    attachments=['/full/path/to/attachment.ext']
)

send_mail(
    [('To Example', 'to@example.com'), 'you@example.com'],
    '[Mail Test] I should be delivered to the inbox',
    PLAINTEXT_EMAIL,
    is_html=False,
    cc='him@example.com, her@example.com',
    bcc=['them@example.com', ('You Know Who', 'youknowwho@example.com')],
    sender=('App', 'notifications@example.com'),
    reply_to='no-reply@example.com',
    attachments=['/full/path/to/attachment.ext', '/full/path/to/attachment.ext'],
    host="smtp.provider.org",
    port=25,
    username="username",
    password="****",
    use_tls=True
)
```

## Testing

```sh
cp .env.example .env
# edit .env file with your mail settings
tox
```
