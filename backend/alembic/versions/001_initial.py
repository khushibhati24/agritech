"""initial database schema

Revision ID: 001_initial
Revises:
Create Date: 2026-08-26
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "001_initial"
down_revision: Union[str, Sequence[str], None] = None
branch_labels = None
depends_on = None


user_role = sa.Enum(
    "farmer",
    "buyer",
    "transporter",
    "admin",
    name="user_role",
)


def upgrade() -> None:
    bind = op.get_bind()

    op.create_table(
        "users",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
        ),
        sa.Column(
            "name",
            sa.String(150),
            nullable=False,
        ),
        sa.Column(
            "email",
            sa.String(255),
            nullable=False,
        ),
        sa.Column(
            "phone",
            sa.String(30),
            nullable=False,
        ),
        sa.Column(
            "password_hash",
            sa.String(255),
            nullable=False,
        ),
        sa.Column(
            "role",
            user_role,
            nullable=False,
        ),
        sa.Column(
            "is_verified",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.UniqueConstraint(
            "email",
            name="uq_users_email",
        ),
    )

    op.create_index(
        "ix_users_email",
        "users",
        ["email"],
    )

    op.create_table(
        "farmer_profiles",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "address",
            sa.String(500),
            nullable=False,
        ),
        sa.Column(
            "location",
            sa.String(255),
            nullable=False,
        ),
        sa.Column(
            "farming_type",
            sa.String(150),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint(
            "user_id",
            name="uq_farmer_profiles_user_id",
        ),
    )

    op.create_table(
        "buyer_profiles",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "business_name",
            sa.String(255),
            nullable=False,
        ),
        sa.Column(
            "business_type",
            sa.String(150),
            nullable=False,
        ),
        sa.Column(
            "address",
            sa.String(500),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint(
            "user_id",
            name="uq_buyer_profiles_user_id",
        ),
    )

    op.create_table(
        "transporter_profiles",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "vehicle_number",
            sa.String(100),
            nullable=False,
        ),
        sa.Column(
            "vehicles_type",
            sa.String(150),
            nullable=False,
        ),
        sa.Column(
            "capacity",
            sa.String(100),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint(
            "user_id",
            name="uq_transporter_profiles_user_id",
        ),
    )

    op.create_table(
        "admin_logs",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
        ),
        sa.Column(
            "admin_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "action",
            sa.String(255),
            nullable=False,
        ),
        sa.Column(
            "details",
            sa.JSON(),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["admin_id"],
            ["users.id"],
        ),
    )

    op.create_index(
        "ix_admin_logs_admin_id",
        "admin_logs",
        ["admin_id"],
    )

    op.create_table(
        "revoked_tokens",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
        ),
        sa.Column(
            "jti",
            sa.String(255),
            nullable=False,
        ),
        sa.Column(
            "expires_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "revoked_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.UniqueConstraint(
            "jti",
            name="uq_revoked_tokens_jti",
        ),
    )

    op.create_index(
        "ix_revoked_tokens_jti",
        "revoked_tokens",
        ["jti"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_revoked_tokens_jti",
        table_name="revoked_tokens",
    )
    op.drop_table("revoked_tokens")

    op.drop_index(
        "ix_admin_logs_admin_id",
        table_name="admin_logs",
    )
    op.drop_table("admin_logs")

    op.drop_table("transporter_profiles")
    op.drop_table("buyer_profiles")
    op.drop_table("farmer_profiles")

    op.drop_index(
        "ix_users_email",
        table_name="users",
    )
    op.drop_table("users")
