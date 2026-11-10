from flask import Blueprint, request, jsonify, current_app
from models.db import db, Schools, Contacts, Visits, FollowUps
from sqlalchemy import func, cast, select
from geoalchemy2 import Geometry
from geoalchemy2.elements import WKTElement
from datetime import date

bp = Blueprint("visits", __name__, url_prefix="/api")

@bp.route("/visits", methods=["POST"])
def create_visit():
  allowed_statuses = {
    "identified",
    "interested",
    "communicating_with_higher_ups_and_awaiting_decision",
    "customer",
    "not_interested"

  }
  data = request.get_json()
  if not data:
    return jsonify({"error":"No info received"}), 400
  errors = {}
  school_id = data.get("school_id")
  new_school = data.get("new_school")

  if not school_id and not (isinstance(new_school, dict) and new_school.get("name")):
    errors["school"] = ["You must pprovide an existing school ID or new school name"]

  next_action_date = None

  if data.get("next_action_date"):
    try:
      next_action_date  = date.fromisoformat(data["next_action_date"])
    except (ValueError,TypeError):
      errors["next_action_date"] = ["Invalid date format"]
  elif data.get("next_action") and not data.get("next_action_date"):
    errors["next_action_date"] = ["A date is required when creating a followup"]


  latitude = data.get("lat")
  longitude = data.get("lng")

  if (
    isinstance(latitude, bool) or not isinstance(latitude, (int,float))
    or isinstance(longitude, bool) or not isinstance(longitude, (int,float))
    or not -90 <= latitude <= 90 or not -180 <= longitude <= 180
  ):
    errors["coordinates"] = ["Invalid GPS coordinates"]

  school_status = data.get("school_status")

  if school_status is not None and school_status not in allowed_statuses:
    errors["school_status"] = ["Invalid school status"]

  if errors:
    return jsonify ({"errors":errors}), 400

  try:
    if school_id:
      school = db.session.get(Schools, school_id)

      if not school:
        return jsonify({"error":"School not found"}), 404
    else:
      school = Schools(
        school_name=new_school["name"], location_name=new_school.get("location_name"),
        ownership=new_school.get("ownership"), approx_student_size=new_school.get("approx_student_size"),
        status="identified"
      )

      db.session.add(school)

      db.session.flush()

    school.status = data.get("school_status", school.status)
    school.current_system = data.get("current_system", school.current_system)
    if data.get("approx_student_size") is not None:
      school.approx_student_size = data["approx_student_size"]

    contact = None

    if  data.get("contact_name"):
      contact = Contacts(
        school_id=school.school_id,
        name = data["contact_name"],
        position = data.get("contact_position"),
        phone_number = data.get("phone_number")
      )

      db.session.add(contact)

    visit_location = WKTElement(f"POINT({longitude} {latitude})", srid=4326)
    gps_accuracy_m = data.get("gps_accuracy_m")
    visit = Visits(
      school_id = school.school_id,
      next_action = data.get("next_action"),
      visit_outcome = data.get("visit_outcome"),
      demo_done = data.get("demo_done", False),
      problem_identified = data.get("problem_identified"),
      main_objection = data.get("main_objection"),
      requested_documents = data.get("requested_documents"),
      notes = data.get("notes"),
      visit_location = visit_location,
      gps_accuracy_m = gps_accuracy_m,
      )
    db.session.add(visit)
    db.session.flush()

    verification_status = "flagged"
    distance = None

    if school.location_coordinates is not None:
      max_distance = current_app.config["VISIT_MAX_DISTANCE_M"]
      max_accuracy = current_app.config["VISIT_MAX_GPS_ACCURACY_M"]
      distance = db.session.scalar(
        select(
          func.ST_Distance(school.location_coordinates, visit.visit_location)
        )
      )
      if (
        distance is not None
        and distance <= max_distance
        and (gps_accuracy_m is not None and gps_accuracy_m <= max_accuracy)
      ):
        verification_status = "verified"

    visit.distance_m = distance
    visit.verification_status = verification_status

    if data.get("next_action"):
      follow_up = FollowUps (
        school_id = school.school_id,
        visit_id = visit.visit_id,
        description = data["next_action"],
        due_date = next_action_date
      )
      db.session.add(follow_up)

    db.session.commit()

    return jsonify ({
      "message":"Visit recorded successfully",
      "school_id": school.school_id,
      "visit_id": visit.visit_id,
      "verification_status": visit.verification_status
    }), 201
    
  except Exception:
    db.session.rollback()

    return jsonify ({
      "error":"Could not save visit"
    }), 500
    
