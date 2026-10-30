from datetime import date, datetime

from flask_sqlalchemy import SQLAlchemy
from geoalchemy2 import Geography
from sqlalchemy import (
  Boolean, CheckConstraint, Date, DateTime, Float,
  ForeignKey, Integer, String, Text, func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

db = SQLAlchemy()


class TimestampMixin:
  """Adds created_at / updated_at to any model that inherits it."""
  created_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True),
    server_default=func.now(),
    nullable=False
  )

  updated_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True),
    server_default=func.now(),
    onupdate=func.now(),
    nullable=False
  )


class SourceSchools(TimestampMixin, db.Model):
  """Raw imported OSM records. Never edited by the app, only reviewed."""
  __tablename__ = "source_schools"

  source_school_id: Mapped[int] = mapped_column(
    Integer,
    primary_key=True,
    autoincrement=True
  )

  osm_id: Mapped[str] = mapped_column(
    String(50),
    index=True,          # NOT unique: the dataset has repeated ids
    nullable=False
  )

  name: Mapped[str | None] = mapped_column(String(255), nullable=True)
  name_en: Mapped[str | None] = mapped_column(String(255), nullable=True)
  amenity: Mapped[str | None] = mapped_column(String(50), nullable=True)
  building: Mapped[str | None] = mapped_column(String(50), nullable=True)
  operator_type: Mapped[str | None] = mapped_column(String(50), nullable=True)

  adm1_name: Mapped[str | None] = mapped_column(String(100), nullable=True)  # region
  adm2_name: Mapped[str | None] = mapped_column(String(100), nullable=True)  # district
  adm3_name: Mapped[str | None] = mapped_column(String(100), nullable=True)  # ward

  original_geometry_type: Mapped[str | None] = mapped_column(
    String(20),          # "POINT" / "POLYGON" / "MULTIPOLYGON"
    nullable=True
  )

  location: Mapped[object | None] = mapped_column(
    Geography(geometry_type="POINT", srid=4326),   # centroid if original was a polygon
    nullable=True
  )

  schools: Mapped[list["Schools"]] = relationship(back_populates="source")


class Schools(TimestampMixin, db.Model):
  __tablename__ = "schools"

  school_id: Mapped[int] = mapped_column(
    Integer,
    primary_key=True,
    autoincrement=True
  )

  school_name: Mapped[str] = mapped_column(String(255), nullable=False)
  location_name: Mapped[str | None] = mapped_column(String(255), nullable=True)

  location_coordinates: Mapped[object | None] = mapped_column(
    Geography(geometry_type="POINT", srid=4326),
    nullable=True
  )

  approx_student_size: Mapped[int | None] = mapped_column(Integer, nullable=True)
  ownership: Mapped[str | None] = mapped_column(String(50), nullable=True)

  source_id: Mapped[int | None] = mapped_column(
    ForeignKey("source_schools.source_school_id", ondelete="SET NULL"),
    nullable=True
  )

  status: Mapped[str] = mapped_column(
    String(50),
    nullable=False,
    default="identified"
  )

  source: Mapped["SourceSchools | None"] = relationship(back_populates="schools")
  visits: Mapped[list["Visits"]] = relationship(
    back_populates="school",
    order_by="Visits.visited_at.desc()"
  )
  contacts: Mapped[list["Contacts"]] = relationship(back_populates="school")
  follow_ups: Mapped[list["FollowUps"]] = relationship(back_populates="school")
  current_system: Mapped[str | None] = mapped_column(
    String(255),
    nullable=True
  )


class Visits(TimestampMixin, db.Model):
  __tablename__ = "visits"
  __table_args__ = (
    CheckConstraint(
      "verification_status IN ('verified', 'flagged', 'rejected')",
      name="ck_visits_verification_status"
    ),
  )

  visit_id: Mapped[int] = mapped_column(
    Integer,
    primary_key=True,
    autoincrement=True
  )

  school_id: Mapped[int] = mapped_column(
    ForeignKey("schools.school_id", ondelete="RESTRICT"),
    nullable=False,
    index=True
  )

  visited_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True),
    nullable=False,
    server_default=func.now()
  )

  next_visit_date: Mapped[date | None] = mapped_column(Date, nullable=True)

  visit_outcome: Mapped[str | None] = mapped_column(String(255), nullable=True)
  next_action: Mapped[str | None] = mapped_column(String(255), nullable=True)

  demo_done: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

  problem_identified: Mapped[str | None] = mapped_column(Text, nullable=True)
  main_objection: Mapped[str | None] = mapped_column(Text, nullable=True)
  requested_documents: Mapped[str | None] = mapped_column(Text, nullable=True)
  notes: Mapped[str | None] = mapped_column(Text, nullable=True)

  visit_location: Mapped[object | None] = mapped_column(
    Geography(geometry_type="POINT", srid=4326),
    nullable=True
  )
  gps_accuracy_m: Mapped[float | None] = mapped_column(Float, nullable=True)
  distance_m: Mapped[float | None] = mapped_column(Float, nullable=True)
  verification_status: Mapped[str | None] = mapped_column(String(20), nullable=True)

  school: Mapped["Schools"] = relationship(back_populates="visits")
  follow_ups: Mapped[list["FollowUps"]] = relationship(back_populates="visit")


class Contacts(TimestampMixin, db.Model):
  __tablename__ = "contacts"

  contact_id: Mapped[int] = mapped_column(
    Integer,
    primary_key=True,
    autoincrement=True
  )

  school_id: Mapped[int] = mapped_column(
    ForeignKey("schools.school_id", ondelete="RESTRICT"),
    nullable=False,
    index=True
  )

  name: Mapped[str] = mapped_column(String(100), nullable=False)
  position: Mapped[str | None] = mapped_column(String(100), nullable=True)
  phone_number: Mapped[str | None] = mapped_column(String(20), nullable=True)

  school: Mapped["Schools"] = relationship(back_populates="contacts")


class FollowUps(TimestampMixin, db.Model):
  __tablename__ = "follow_ups"
  __table_args__ = (
    CheckConstraint(
      "status IN ('pending', 'completed', 'cancelled')",
      name="ck_follow_ups_status"
    ),
  )

  follow_up_id: Mapped[int] = mapped_column(
    Integer,
    primary_key=True,
    autoincrement=True
  )

  school_id: Mapped[int] = mapped_column(
    ForeignKey("schools.school_id", ondelete="RESTRICT"),
    nullable=False,
    index=True
  )

  visit_id: Mapped[int | None] = mapped_column(
    ForeignKey("visits.visit_id", ondelete="SET NULL"),
    nullable=True
  )

  description: Mapped[str] = mapped_column(Text, nullable=False)
  due_date: Mapped[date] = mapped_column(Date, nullable=False)

  status: Mapped[str] = mapped_column(
    String(20),
    nullable=False,
    default="pending"
  )

  completed_at: Mapped[datetime | None] = mapped_column(
    DateTime(timezone=True),
    nullable=True        # stays NULL until you mark the task done
  )

  notes: Mapped[str | None] = mapped_column(Text, nullable=True)

  school: Mapped["Schools"] = relationship(back_populates="follow_ups")
  visit: Mapped["Visits | None"] = relationship(back_populates="follow_ups")