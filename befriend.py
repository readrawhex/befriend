import sys
import json
import argparse
import random
from datetime import datetime
from time import sleep
from random import uniform as rand
from playwright.sync_api import sync_playwright


def parse_opts():
    """
    Parse arguments and return an `argparse` arguments object.
    """
    parser = argparse.ArgumentParser(
        description="automate following and liking on instagram"
    )
    parser.add_argument(
        "-l",
        "--likes",
        type=int,
        default=random.randint(70, 80),
        help="number of posts to like",
    )
    parser.add_argument(
        "-f",
        "--follows",
        type=int,
        default=5,
        help="number of suggested accounts to follow",
    )
    parser.add_argument(
        "-s",
        "--session-file",
        type=str,
        default=".befriend.sess",
        help="specify location of session file",
    )
    return parser.parse_args()


def logf(msg: str):
    """
    Log failure message to stderr and exit with status code `1`.
    """
    log("FAILURE: " + msg)
    sys.exit(1)


def log(msg: str):
    """
    Log message to stderr.
    """
    print(
        "{0}: {1}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), msg),
        file=sys.stderr,
    )


def wait_small():
    """
    Sleep (blocking) for a period between 0.4 to 1.1 seconds.
    """
    sleep(rand(0.4, 1.1))


def wait_long():
    """
    Sleep (blocking) for a period between 4.5 to 11 seconds.
    """
    sleep(rand(4.5, 11))


def sess_save(ctx, file_path: str):
    """
    Save session data to `file_path` for browser context `ctx`.
    """
    log(f"saving session data to {file_path}...")
    try:
        with open(file_path, "w") as f:
            json.dump(ctx.cookies(), f)
    except Exception as e:
        logf(str(e))


def sess_load(ctx, file_path: str):
    """
    Load session data from `file_path` for browser context `ctx`.
    """
    log(f"loading session data from {file_path}...")
    try:
        with open(file_path, "r") as f:
            cookies = json.load(f)
            if not cookies:
                log("no session data in file")
            else:
                ctx.add_cookies(cookies)
    except FileNotFoundError as e:
        log(f"session data not loaded: {e}")
    except Exception as e:
        logf(str(e))


def login(ctx):
    """
    Create page from browser context `ctx` and visit instagram.

    Check for a login page, and if so prompt user to enter login info manually, then
    continue.
    """

    page = ctx.new_page()
    page.goto("https://www.instagram.com/")
    page.wait_for_load_state("networkidle")
    usr = page.get_by_label("Phone number, username, or")
    pwd = page.get_by_label("Password")

    if usr.count() == 1 and pwd.count() == 1:
        log(
            "login page detected, please enter login info and then hit enter in terminal..."
        )
        input("")
        wait_long()
        page.wait_for_load_state("networkidle")

        if page.get_by_text("Sorry, your password was").count() > 0:
            page.close()
            logf("incorrect login provided")

        if page.get_by_role("button", name="Save info").count() == 1:
            page.get_by_role("button", name="Save info").click()
            log("saving login info into browser context...")

        wait_long()
        page.wait_for_load_state("networkidle")
    else:
        log("login using session data successful :)")

    return page


def scroll_feed(page, mlikes: int):
    """
    Scroll feed, liking `mlikes` number of posts that are not ads.
    """
    log("liking posts in feed...")
    wait_small()
    i = 0
    for _ in range(0, mlikes):
        post_locator = page.locator(
            'article:has([role="button"]:has-text("Like"),'
            + '[role="button"]:has-text("More options"), [role="button"]:has-text("Save")'
            + '):not(:has-text("Sponsored"))'
        )
        post_like_button = post_locator.get_by_role(
            "button", name="Like", exact=True
        ).first
        post_like_button.scroll_into_view_if_needed()
        page.wait_for_load_state("networkidle")
        post_like_button.click()
        wait_long()
        i += 1
    log(f"liked {i} posts from home feed")


def follow_recs(page, mfollows: int):
    """
    Go to suggested users page and like `mfollows` number of users.
    """
    page.get_by_role("link", name="See All", exact=True).click()
    wait_long()
    page.wait_for_load_state("networkidle")

    profile = page.locator('button > div > div:has-text("Follow")')
    for i in range(0, mfollows):
        profile.nth(i).click()
        wait_long()

    page.get_by_role("link", name="Home Home").click()
    wait_long()
    page.wait_for_load_state("networkidle")


def main():
    args = parse_opts()

    try:
        with sync_playwright() as p:
            log("loading browser")
            browser = p.chromium.launch(headless=False)
            context = browser.new_context()

            log("loading session data from save file")
            sess_load(context, args.session_file)

            log(
                "following {0} users, liking {1} posts...".format(
                    args.follows, args.likes
                )
            )
            page = login(context)
            if args.follows > 0:
                follow_recs(page, args.follows)
            if args.likes > 0:
                scroll_feed(page, args.likes)

            sess_save(context, args.session_file)
            wait_long()
            page.close()
        log("finished successfully :)")
    except KeyboardInterrupt:
        log("keyboard interrupt, saving session data...")
        sess_save(context, args.session_file)


if __name__ == "__main__":
    main()
