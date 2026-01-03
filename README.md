# befriend

Playwright project for logging on to instagram, liking some things,
following some people, and then saving cookies for easier login next
time the script is ran.

Notice I made this run slow on purpose because I would prefer if my
instagram account did not get banned.

## usage

```bash
$ python3 befriend.py --help
usage: befriend.py [-h] [-l LIKES] [-f FOLLOWS] [-s SESSION_FILE]

automate following and liking on instagram

options:
  -h, --help            show this help message and exit
  -l LIKES, --likes LIKES
                        number of posts to like
  -f FOLLOWS, --follows FOLLOWS
                        number of suggested accounts to follow
  -s SESSION_FILE, --session-file SESSION_FILE
                        specify location of session file
```
