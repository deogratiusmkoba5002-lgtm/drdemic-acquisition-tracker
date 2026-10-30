from flask import Blueprint, jsonify
from models.db import db, Visits, Schools
from sqlalchemy import exists, select, cast, func
from geoalchemy2 import Geometry 

bp = Blueprint("schools", __name__, url_prefix="/api")

@bp.route("/schools")
def list_schools():
  visited_check = exists().where(Visits.school_id == Schools.school_id)
  my_query = select(Schools.school_id, Schools.school_name, Schools.ownership, Schools.status,
         func.ST_Y(cast(Schools.location_coordinates, Geometry)).label("latitude"),
         func.ST_X(cast(Schools.location_coordinates, Geometry)).label("longitude"),
         visited_check.label("visited")).where(Schools.location_coordinates.is_not(None))
  rows = db.session.execute(my_query).all()

  schools = []
  for row in rows:
    schools_dictionary = {
      "id":row.school_id, "name":row.school_name, "lat":row.latitude, 
      "lng":row.longitude, "ownership":row.ownership, "status":row.status,
      "visited":row.visited
    }
    schools.append(schools_dictionary)

  return jsonify(schools)


  