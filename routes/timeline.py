"""时间轴首页路由。"""
from datetime import date

from flask import Blueprint, render_template

from models.event import list_events
from models.timeline import get_timeline
from routes.guard import login_required

bp = Blueprint("timeline", __name__)


@bp.route("/")
@login_required
def index():
    timeline = get_timeline()
    events = list_events(timeline["id"])
    return render_template("timeline.html", timeline=timeline, events=events, today=date.today().isoformat())
