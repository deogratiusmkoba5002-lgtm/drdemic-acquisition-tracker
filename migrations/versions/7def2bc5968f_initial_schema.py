"""initial schema

Revision ID: 7def2bc5968f
Revises: 
Create Date: 2026-10-30 02:49:23.929150

"""
from alembic import op
import sqlalchemy as sa
import geoalchemy2


# revision identifiers, used by Alembic.
revision = '7def2bc5968f'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('source_schools',
    sa.Column('source_school_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('osm_id', sa.String(length=50), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.Column('name_en', sa.String(length=255), nullable=True),
    sa.Column('amenity', sa.String(length=50), nullable=True),
    sa.Column('building', sa.String(length=50), nullable=True),
    sa.Column('operator_type', sa.String(length=50), nullable=True),
    sa.Column('adm1_name', sa.String(length=100), nullable=True),
    sa.Column('adm2_name', sa.String(length=100), nullable=True),
    sa.Column('adm3_name', sa.String(length=100), nullable=True),
    sa.Column('original_geometry_type', sa.String(length=20), nullable=True),
    sa.Column('location', geoalchemy2.types.Geography(geometry_type='POINT', srid=4326, dimension=2, from_text='ST_GeogFromText', name='geography'), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('source_school_id')
    )
    with op.batch_alter_table('source_schools', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_source_schools_osm_id'), ['osm_id'], unique=False)

    op.create_table('schools',
    sa.Column('school_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('school_name', sa.String(length=255), nullable=False),
    sa.Column('location_name', sa.String(length=255), nullable=True),
    sa.Column('location_coordinates', geoalchemy2.types.Geography(geometry_type='POINT', srid=4326, dimension=2, from_text='ST_GeogFromText', name='geography'), nullable=True),
    sa.Column('approx_student_size', sa.Integer(), nullable=True),
    sa.Column('ownership', sa.String(length=50), nullable=True),
    sa.Column('source_id', sa.Integer(), nullable=True),
    sa.Column('status', sa.String(length=50), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['source_id'], ['source_schools.source_school_id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('school_id')
    )

    op.create_table('contacts',
    sa.Column('contact_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('school_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('position', sa.String(length=100), nullable=True),
    sa.Column('phone_number', sa.String(length=20), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['school_id'], ['schools.school_id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('contact_id')
    )
    with op.batch_alter_table('contacts', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_contacts_school_id'), ['school_id'], unique=False)

    op.create_table('visits',
    sa.Column('visit_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('school_id', sa.Integer(), nullable=False),
    sa.Column('visited_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('next_visit_date', sa.Date(), nullable=True),
    sa.Column('visit_outcome', sa.String(length=255), nullable=True),
    sa.Column('next_action', sa.String(length=255), nullable=True),
    sa.Column('demo_done', sa.Boolean(), nullable=False),
    sa.Column('problem_identified', sa.Text(), nullable=True),
    sa.Column('main_objection', sa.Text(), nullable=True),
    sa.Column('requested_documents', sa.Text(), nullable=True),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('visit_location', geoalchemy2.types.Geography(geometry_type='POINT', srid=4326, dimension=2, from_text='ST_GeogFromText', name='geography'), nullable=True),
    sa.Column('gps_accuracy_m', sa.Float(), nullable=True),
    sa.Column('distance_m', sa.Float(), nullable=True),
    sa.Column('verification_status', sa.String(length=20), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint("verification_status IN ('verified', 'flagged', 'rejected')", name='ck_visits_verification_status'),
    sa.ForeignKeyConstraint(['school_id'], ['schools.school_id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('visit_id')
    )
    with op.batch_alter_table('visits', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_visits_school_id'), ['school_id'], unique=False)

    op.create_table('follow_ups',
    sa.Column('follow_up_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('school_id', sa.Integer(), nullable=False),
    sa.Column('visit_id', sa.Integer(), nullable=True),
    sa.Column('description', sa.Text(), nullable=False),
    sa.Column('due_date', sa.Date(), nullable=False),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint("status IN ('pending', 'completed', 'cancelled')", name='ck_follow_ups_status'),
    sa.ForeignKeyConstraint(['school_id'], ['schools.school_id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['visit_id'], ['visits.visit_id'], ondelete='SET NULL'),)