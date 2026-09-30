"""Initial migration."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers
revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Sessions table
    op.create_table(
        "sessions",
        sa.Column("id", sqlite.UUID(as_uuid=False), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("language", sa.String(10), nullable=False, server_default="en"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_sessions_started_at", "sessions", ["started_at"])
    op.create_index("ix_sessions_status", "sessions", ["status"])

    # Transcript segments table
    op.create_table(
        "transcript_segments",
        sa.Column("id", sqlite.UUID(as_uuid=False), nullable=False),
        sa.Column("session_id", sqlite.UUID(as_uuid=False), nullable=False),
        sa.Column("start_ms", sa.Integer(), nullable=False),
        sa.Column("end_ms", sa.Integer(), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("language", sa.String(10), nullable=False),
        sa.Column("provider", sa.String(50), nullable=False),
        sa.Column("simulated", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.ForeignKeyConstraint(["session_id"], ["sessions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_transcript_segments_session_id", "transcript_segments", ["session_id"])
    op.create_index("ix_transcript_segments_start_ms", "transcript_segments", ["start_ms"])

    # Summaries table
    op.create_table(
        "summaries",
        sa.Column("id", sqlite.UUID(as_uuid=False), nullable=False),
        sa.Column("session_id", sqlite.UUID(as_uuid=False), nullable=False),
        sa.Column("key_points", sqlite.JSON(), nullable=False, server_default="[]"),
        sa.Column("action_items", sqlite.JSON(), nullable=False, server_default="[]"),
        sa.Column("provider", sa.String(50), nullable=False),
        sa.Column("simulated", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["session_id"], ["sessions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_summaries_session_id", "summaries", ["session_id"])
    op.create_index("ix_summaries_created_at", "summaries", ["created_at"])

    # Stage logs table
    op.create_table(
        "stage_logs",
        sa.Column("id", sqlite.UUID(as_uuid=False), nullable=False),
        sa.Column("session_id", sqlite.UUID(as_uuid=False), nullable=True),
        sa.Column("stage", sa.String(50), nullable=False),
        sa.Column("provider", sa.String(50), nullable=False),
        sa.Column("latency_ms", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["session_id"], ["sessions.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_stage_logs_session_id", "stage_logs", ["session_id"])
    op.create_index("ix_stage_logs_stage", "stage_logs", ["stage"])
    op.create_index("ix_stage_logs_created_at", "stage_logs", ["created_at"])

    # Benchmark runs table
    op.create_table(
        "benchmark_runs",
        sa.Column("id", sqlite.UUID(as_uuid=False), nullable=False),
        sa.Column("audio_name", sa.String(255), nullable=False),
        sa.Column("audio_duration_s", sa.Float(), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("device_info", sqlite.JSON(), nullable=False, server_default="{}"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_benchmark_runs_started_at", "benchmark_runs", ["started_at"])

    # Benchmark results table
    op.create_table(
        "benchmark_results",
        sa.Column("id", sqlite.UUID(as_uuid=False), nullable=False),
        sa.Column("run_id", sqlite.UUID(as_uuid=False), nullable=False),
        sa.Column("provider", sa.String(50), nullable=False),
        sa.Column("stage", sa.String(50), nullable=False),
        sa.Column("latency_ms", sa.Integer(), nullable=False),
        sa.Column("real_time_factor", sa.Float(), nullable=False),
        sa.Column("cpu_percent", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("npu_percent", sa.Float(), nullable=True),
        sa.Column("battery_delta_percent", sa.Float(), nullable=True),
        sa.Column("simulated", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.ForeignKeyConstraint(["run_id"], ["benchmark_runs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_benchmark_results_run_id", "benchmark_results", ["run_id"])
    op.create_index("ix_benchmark_results_provider", "benchmark_results", ["provider"])
    op.create_index("ix_benchmark_results_stage", "benchmark_results", ["stage"])


def downgrade() -> None:
    op.drop_table("benchmark_results")
    op.drop_table("benchmark_runs")
    op.drop_table("stage_logs")
    op.drop_table("summaries")
    op.drop_table("transcript_segments")
    op.drop_table("sessions")