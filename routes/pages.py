from flask import Blueprint, render_template

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


# routes/pages.py

# STEP 1: import Blueprint and render_template from flask

# STEP 2: bp = Blueprint("pages", __name__)   (no url_prefix, these are real pages)

# STEP 3: one function per page, each returning render_template("<file>.html")
#   "/"             -> function dashboard()    -> dashboard.html
#   "/map"          -> function map_page()     -> map.html
#   "/in-progress"  -> function in_progress()  -> in_progress.html
#   "/customers"    -> function customers()    -> customers.html
#   "/lost"         -> function lost()         -> lost.html
#   (the function names matter: url_for("pages.dashboard") uses them)

# STEP 4: register this blueprint in create_app(), like schools_bp