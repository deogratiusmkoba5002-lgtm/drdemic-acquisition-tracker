from flask import Blueprint, render_template
from statuses import STATUSES

bp = Blueprint("pages", __name__)

@bp.route("/")
def render_dashboard():
  return render_template("dashboard.html")

@bp.route("/map")
def render_map_page():
  return render_template("map.html")

@bp.route("/in-progress")
def render_in_progress_page():
  return render_template("in_progress.html")

@bp.route("/customers")
def render_customers_page():
  return render_template("customers.html")

@bp.route("/lost")
def render_lost_page():
  return render_template("lost.html")

@bp.route("/visits/new")
def render_visit_form_page():
#  return render_template("visit_form.html", statuses=STATUSES)
   return render_template("visit_form.html", statuses=STATUSES)

# routes/pages.py
# STEP 1: add a route "/visits/new" -> function render_visit_form_page()
# STEP 2: import STATUSES from statuses.py and pass it:
#         render_template("visit_form.html", statuses=STATUSES)