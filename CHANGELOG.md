# Changelog

For a complete view of all the releases, visit the releases page on GitHub:
[https://github.com/dareenzo/send_mail/releases](https://github.com/dareenzo/send_mail/releases)

## v1.0.1 - 2017-01-22
- Only provide `send_mail` method as part of the public API. The rest of the
  methods stay private
 
## v1.0.0 - 2017-01-22

- Breaking changes
  - Changed `send_mail` function signature to take subject as first and
    only mandatory parameter.
  - plain-text message must be passed in `message` and html in `html_message`
  - `logger` is no longer created within the `send_mail` but instead if passed
    as a keyword paramter. In it's absence messages are not logged
- Improve module documentation
- Require at least one destination address

## v0.3.0 - 2017-01-13

- Allow debugging

## v0.2.0 - 2017-01-13

- Allow connecting to server with SSL

## v0.1.1 - 2017-01-13

- Replace call to dict.iteritems which is Python3 by six.iteritems
- We put and get env. vars as strings, so parse SMTP_USE_SSL to bool before using 
- Improve cheap_dot_env method in test code


## v0.1.0 - 2017-01-12

- Initial release
