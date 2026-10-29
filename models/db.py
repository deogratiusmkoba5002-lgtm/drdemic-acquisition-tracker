from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from geoalchemy2 import Geography
from datetime import date, datetime

db = SQLAlchemy()

class Schools(db.Model):
  __tablename__ = "schools"

  school_id: Mapped[int] = mapped_column(
    Integer,
    primary_key=True,
    autoincrement=True
  )

  school_name: Mapped[str] = mapped_column(
    String(255),
    nullable=False
  )

  location_name: Mapped[str | None] = mapped_column(
    String(255),
    nullable=True
  )

  location_coordinates: Mapped[object | None] = mapped_column(
    Geography(geometry_type="POINT", srid=4326),
    nullable=True
  )

  approx_student_size: Mapped[int | None] = mapped_column(
    Integer,
    nullable=True
  )

class Visits(db.Model):
  __tablename__ = "visits"

  visit_id: Mapped[int] = mapped_column(
    primary_key=True,
    autoincrement=True
  )

  visit_date: Mapped[date] = mapped_column(
    db.Date,
    nullable = False
  )

  next_visit_date: Mapped[date | None] = mapped_column(
    db.Date,
    nullable = True
  )

  visit_outcome: Mapped[str | None] = mapped_column(
    String(255),
    nullable = True
  )

  next_action: Mapped[str | None] = mapped_column(
    String(255),
    nullable = True
  )

  demo_done: Mapped[bool] = mapped_column(
    db.Boolean,
    nullable = False,
    default = False
  )

  problem_identified: Mapped[str | None] = mapped_column(
    String(255),
    nullable = True
  )

  main_objection: Mapped[str | None] = mapped_column(
    String(255),
    nullable = True
  )

  requested_documents: Mapped[str | None] = mapped_column(
    String(255),
    nullable = True
  )

  notes: Mapped[str | None] = mapped_column(
    String(500),
    nullable = True
  )

  gps_accuracy_m: Mapped[int | None] = mapped_column(
    Integer,
    nullable = True
  )

  school_id: Mapped[int] = mapped_column(
    ForeignKey("schools.school_id"),
    nullable = False
  )

class Contacts(db.Model):
  __tablename__ = "contacts"

  contact_id: Mapped[int] = mapped_column(
    Integer,
    primary_key = True,
    autoincrement = True
  )

  school_id: Mapped[int] = mapped_column(
    ForeignKey("schools.school_id"),
    nullable = False
  )

  phone_number: Mapped[str | None] = mapped_column(
    String(20),
    nullable = True
  )

  name: Mapped[str] = mapped_column(
    String(50),
    nullable = False
  )

  position: Mapped[str] = mapped_column(
    String(50),
    nullable = False
  )