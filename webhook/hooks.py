from sqlalchemy.event import listen
from CTFd.models import Users, Solves, Challenges, Teams, Tags
from flask import current_app as app
from ...utils.modes import get_model
from hmac import new as new_hmac
from json import dumps as json_dumps
from CTFd.utils.config import is_teams_mode
from requests import post
from CTFd.models import (
    db
)

#Reference: https://github.com/KaindorfCTF/ctfd-notifier/raw/master/hooks.py

def trigger_solved_hook(details):
    signature = details["signature"]
    body = details["data"]
    url = details["url"]
    try:
        post("{}/?signature={}".format(url,signature), data=body)
    except Exception as err:
        print("error posting webhook: ",str(err))
    print("solved hook: ", body, signature)

def make_challenges_visible_by_tag(tagname, conn):
    challenges = _get_challenges_by_tagname(tagname)
    for challenge in challenges:
        
        ### BEWARE!!
        ### We've hooked the solve event
        ### So we know this session probably
        ### didn't hide a challenge. But
        ### this is dangerous territory.
        conn.execute(
            Challenges.__table__.
            update().values(state="visible").
            where(Challenges.id ==challenge.id)
        )
        #db.session.commit()


def process_threshold_action(action, result, conn):
    if action["action"] == "unlock":
        tag = action["tag"]
        make_challenges_visible_by_tag(tag, conn)
    elif action["action"] == "webhook":
        result["url"] = action["url"]
        app.webhook_plugin_executor.submit_job(trigger_solved_hook, result)

def check_threshold_alerts(result, conn):
    solve_details = result["solve"]
    before_score = solve_details["before_score"]
    after_score = solve_details["score"]
    for threshold in app.webhook_plugin_levels:
        if before_score < threshold["threshold"] and after_score >= threshold["threshold"]:
            for action in threshold["actions"]:
                process_threshold_action(action, result, conn)


def on_solve(mapper, conn, solve):
    details = get_solve_details(solve)
    hmac_secret = app.webhook_plugin_secret
    data = json_dumps(details)
    hmac = new_hmac(hmac_secret.encode(), data.encode(), digestmod="sha256").hexdigest()
    result = { 
        "solve": details, 
        "data" : data,
        "signature" : hmac,
        "url" : app.webhook_plugin_url
        }
    if app.webhook_report_all_solves or details["challenge"] in app.webhook_reported_solves:
        app.webhook_plugin_executor.submit_job(trigger_solved_hook, result)
    check_threshold_alerts(result, conn)



def load_hooks():
    listen(Solves, "after_insert", on_solve)

def _get_team_by_id(team_id):
    return Teams.query.filter_by(id=team_id).first()

def _get_user_by_id(user_id):
    return Users.query.filter_by(id=user_id).first()

def _get_challenge_by_id(challenge_id):
    return Challenges.query.filter_by(id=challenge_id).first()

def _get_challenges_by_tagname(tagname):
    challenges = []
    tags = Tags.query.filter_by(value=tagname)
    for tag in tags:
        challenge = _get_challenge_by_id(tag.challenge_id)
        challenges.append(challenge)
    return challenges

def get_solve_details(solve):
    user = _get_user_by_id(solve.user_id)
    name = user.name
    challenge = _get_challenge_by_id(solve.challenge_id)

    if is_teams_mode():
        team = _get_team_by_id(user.team_id)
    else:
        team = user
    score = team.get_score()
    before_score = score - challenge.value
    details = {
        "user": name,
        "challenge" : challenge.name,
        "score" : score,
        "before_score" : before_score
        }
    return details
