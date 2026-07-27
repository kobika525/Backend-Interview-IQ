"""initial schema

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-07-25

Hand-written initial migration covering every model in app/models/*.
(This repo ships with no live MySQL instance to run `alembic revision
--autogenerate` against, so this migration was authored directly from
the SQLAlchemy model definitions instead. Table/column defs mirror the
models exactly. If your models drift from this file, prefer running
`alembic revision --autogenerate -m "sync"` to generate a follow-up
migration rather than editing this one.)
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None

now = sa.func.now()


def ts_cols():
    return [
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=now),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=now),
    ]


def upgrade() -> None:
    # ---- users -----------------------------------------------------
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("full_name", sa.String(120), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("role", sa.Enum("USER", "ADMIN", name="user_role"), nullable=False, server_default="USER"),
        sa.Column("account_status", sa.Enum("ACTIVE", "SUSPENDED", "DISABLED", "PENDING_VERIFICATION", name="account_status"), nullable=False, server_default="ACTIVE"),
        sa.Column("email_verified", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.false()),
        *ts_cols(),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_role", "users", ["role"])
    op.create_index("ix_users_account_status", "users", ["account_status"])
    op.create_index("ix_users_is_deleted", "users", ["is_deleted"])

    # ---- skills ------------------------------------------------------
    op.create_table(
        "skills",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("category", sa.String(60), nullable=False),
        *ts_cols(),
    )
    op.create_index("ix_skills_name", "skills", ["name"], unique=True)
    op.create_index("ix_skills_category", "skills", ["category"])

    # ---- career_roles --------------------------------------------------
    op.create_table(
        "career_roles",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(120), nullable=False),
        sa.Column("slug", sa.String(140), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("responsibilities", sa.JSON(), nullable=False),
        sa.Column("experience_level", sa.Enum("BEGINNER", "INTERMEDIATE", "ADVANCED", name="experience_level"), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        *ts_cols(),
    )
    op.create_index("ix_career_roles_title", "career_roles", ["title"], unique=True)
    op.create_index("ix_career_roles_slug", "career_roles", ["slug"], unique=True)

    # ---- subscription_plans ------------------------------------------
    op.create_table(
        "subscription_plans",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(40), nullable=False),
        sa.Column("price_monthly", sa.Numeric(10, 2), nullable=False, server_default="0"),
        sa.Column("limits", sa.JSON(), nullable=False),
        sa.Column("features", sa.JSON(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        *ts_cols(),
    )
    op.create_index("ix_subscription_plans_name", "subscription_plans", ["name"], unique=True)

    # ---- achievements ---------------------------------------------------
    op.create_table(
        "achievements",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(80), nullable=False),
        sa.Column("title", sa.String(120), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("condition", sa.JSON(), nullable=False),
        *ts_cols(),
    )
    op.create_index("ix_achievements_code", "achievements", ["code"], unique=True)

    # ---- role_skills (composite PK) ----------------------------------
    op.create_table(
        "role_skills",
        sa.Column("role_id", sa.Integer(), sa.ForeignKey("career_roles.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("skill_id", sa.Integer(), sa.ForeignKey("skills.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("required", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("weight", sa.Float(), nullable=False, server_default="1.0"),
    )

    # ---- user_profiles ---------------------------------------------
    op.create_table(
        "user_profiles",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("career_goal", sa.String(255), nullable=True),
        sa.Column("experience_level", sa.Enum("BEGINNER", "INTERMEDIATE", "ADVANCED", name="experience_level", create_type=False), nullable=True),
        sa.Column("target_role_id", sa.Integer(), sa.ForeignKey("career_roles.id", ondelete="SET NULL"), nullable=True),
        sa.Column("preferred_interview_mode", sa.Enum("TEXT", "VOICE", "VIDEO", name="interview_mode"), nullable=True),
        sa.Column("weekly_learning_target", sa.Integer(), nullable=False, server_default="5"),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("profile_image_key", sa.String(255), nullable=True),
        sa.Column("onboarding_completed", sa.Boolean(), nullable=False, server_default=sa.false()),
        *ts_cols(),
    )
    op.create_index("ix_user_profiles_user_id", "user_profiles", ["user_id"], unique=True)

    # ---- refresh_tokens ------------------------------------------------
    op.create_table(
        "refresh_tokens",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("token_hash", sa.String(64), nullable=False),
        sa.Column("family_id", sa.String(36), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("revoked_at", sa.DateTime(), nullable=True),
        sa.Column("replaced_by_hash", sa.String(64), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=now),
    )
    op.create_index("ix_refresh_tokens_user_id", "refresh_tokens", ["user_id"])
    op.create_index("ix_refresh_tokens_token_hash", "refresh_tokens", ["token_hash"], unique=True)
    op.create_index("ix_refresh_tokens_family_id", "refresh_tokens", ["family_id"])
    op.create_index("ix_refresh_tokens_expires_at", "refresh_tokens", ["expires_at"])

    # ---- action_tokens ---------------------------------------------
    op.create_table(
        "action_tokens",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("purpose", sa.String(40), nullable=False),
        sa.Column("token_hash", sa.String(64), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("used_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=now),
    )
    op.create_index("ix_action_tokens_user_id", "action_tokens", ["user_id"])
    op.create_index("ix_action_tokens_purpose", "action_tokens", ["purpose"])
    op.create_index("ix_action_tokens_token_hash", "action_tokens", ["token_hash"], unique=True)
    op.create_index("ix_action_tokens_expires_at", "action_tokens", ["expires_at"])

    # ---- user_skills -------------------------------------------------
    op.create_table(
        "user_skills",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("skill_id", sa.Integer(), sa.ForeignKey("skills.id", ondelete="CASCADE"), nullable=False),
        sa.Column("proficiency", sa.Integer(), nullable=False, server_default="1"),
        *ts_cols(),
    )
    op.create_index("ix_user_skills_user_id", "user_skills", ["user_id"])

    # ---- resumes -------------------------------------------------------
    op.create_table(
        "resumes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("original_name", sa.String(255), nullable=False),
        sa.Column("storage_key", sa.String(255), nullable=False),
        sa.Column("mime_type", sa.String(120), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column("target_role_id", sa.Integer(), sa.ForeignKey("career_roles.id", ondelete="SET NULL"), nullable=True),
        sa.Column("status", sa.Enum("UPLOADED", "PROCESSING", "COMPLETED", "FAILED", name="resume_status"), nullable=False, server_default="UPLOADED"),
        sa.Column("extracted_text", sa.Text(), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.false()),
        *ts_cols(),
    )
    op.create_index("ix_resumes_user_id", "resumes", ["user_id"])
    op.create_index("ix_resumes_storage_key", "resumes", ["storage_key"], unique=True)
    op.create_index("ix_resumes_status", "resumes", ["status"])
    op.create_index("ix_resumes_is_deleted", "resumes", ["is_deleted"])

    # ---- interview_questions --------------------------------------
    op.create_table(
        "interview_questions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("question_text", sa.Text(), nullable=False),
        sa.Column("role_id", sa.Integer(), sa.ForeignKey("career_roles.id", ondelete="SET NULL"), nullable=True),
        sa.Column("category", sa.String(80), nullable=False),
        sa.Column("difficulty", sa.Enum("BEGINNER", "INTERMEDIATE", "ADVANCED", name="difficulty"), nullable=False),
        sa.Column("interview_type", sa.Enum("HR", "BEHAVIORAL", "TECHNICAL", "MIXED", name="interview_type"), nullable=False),
        sa.Column("expected_key_points", sa.JSON(), nullable=False),
        sa.Column("expected_keywords", sa.JSON(), nullable=False),
        sa.Column("sample_answer", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        *ts_cols(),
    )

    # ---- interview_sessions -----------------------------------------
    op.create_table(
        "interview_sessions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("role_id", sa.Integer(), sa.ForeignKey("career_roles.id", ondelete="SET NULL"), nullable=True),
        sa.Column("resume_id", sa.Integer(), sa.ForeignKey("resumes.id", ondelete="SET NULL"), nullable=True),
        sa.Column("interview_type", sa.Enum("HR", "BEHAVIORAL", "TECHNICAL", "MIXED", name="interview_type", create_type=False), nullable=False),
        sa.Column("mode", sa.Enum("TEXT", "VOICE", "VIDEO", name="interview_mode", create_type=False), nullable=False),
        sa.Column("experience_level", sa.Enum("BEGINNER", "INTERMEDIATE", "ADVANCED", name="experience_level", create_type=False), nullable=False),
        sa.Column("difficulty", sa.Enum("BEGINNER", "INTERMEDIATE", "ADVANCED", name="difficulty", create_type=False), nullable=False),
        sa.Column("duration_minutes", sa.Integer(), nullable=False, server_default="20"),
        sa.Column("requested_questions", sa.Integer(), nullable=False, server_default="5"),
        sa.Column("preferred_language", sa.String(20), nullable=False, server_default="en"),
        sa.Column("job_description", sa.Text(), nullable=True),
        sa.Column("status", sa.Enum("CREATED", "READY", "IN_PROGRESS", "PROCESSING", "COMPLETED", "CANCELLED", "FAILED", name="interview_status"), nullable=False, server_default="CREATED"),
        sa.Column("current_order", sa.Integer(), nullable=False, server_default="0"),
        *ts_cols(),
    )
    op.create_index("ix_interview_sessions_user_id", "interview_sessions", ["user_id"])
    op.create_index("ix_interview_sessions_status", "interview_sessions", ["status"])

    # ---- session_questions ---------------------------------------
    op.create_table(
        "session_questions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("session_id", sa.Integer(), sa.ForeignKey("interview_sessions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("question_id", sa.Integer(), sa.ForeignKey("interview_questions.id"), nullable=False),
        sa.Column("order_no", sa.Integer(), nullable=False),
        sa.Column("skipped", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.create_index("ix_session_questions_session_id", "session_questions", ["session_id"])

    # ---- interview_answers ------------------------------------------
    op.create_table(
        "interview_answers",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("session_question_id", sa.Integer(), sa.ForeignKey("session_questions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("answer_text", sa.Text(), nullable=True),
        sa.Column("media_key", sa.String(255), nullable=True),
        sa.Column("transcript", sa.Text(), nullable=True),
        sa.Column("duration_seconds", sa.Float(), nullable=True),
        *ts_cols(),
    )
    op.create_index("ix_interview_answers_session_question_id", "interview_answers", ["session_question_id"], unique=True)

    # ---- answer_evaluations --------------------------------------
    op.create_table(
        "answer_evaluations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("answer_id", sa.Integer(), sa.ForeignKey("interview_answers.id", ondelete="CASCADE"), nullable=False),
        sa.Column("final_score", sa.Float(), nullable=False),
        sa.Column("category_scores", sa.JSON(), nullable=False),
        sa.Column("raw_signals", sa.JSON(), nullable=False),
        sa.Column("strengths", sa.JSON(), nullable=False),
        sa.Column("weaknesses", sa.JSON(), nullable=False),
        sa.Column("feedback", sa.Text(), nullable=False),
        sa.Column("improved_answer", sa.Text(), nullable=True),
        sa.Column("scoring_version", sa.String(40), nullable=False, server_default="interview-v1"),
        *ts_cols(),
    )
    op.create_index("ix_answer_evaluations_answer_id", "answer_evaluations", ["answer_id"], unique=True)

    # ---- resume_analyses --------------------------------------------
    op.create_table(
        "resume_analyses",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("resume_id", sa.Integer(), sa.ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("ats_score", sa.Float(), nullable=False),
        sa.Column("category_scores", sa.JSON(), nullable=False),
        sa.Column("strengths", sa.JSON(), nullable=False),
        sa.Column("suggestions", sa.JSON(), nullable=False),
        sa.Column("sections", sa.JSON(), nullable=False),
        sa.Column("scoring_version", sa.String(40), nullable=False, server_default="ats-v1"),
        sa.Column("disclaimer", sa.String(255), nullable=False, server_default="Estimated AI-assisted ATS readiness score"),
        *ts_cols(),
    )
    op.create_index("ix_resume_analyses_resume_id", "resume_analyses", ["resume_id"], unique=True)

    # ---- resume_skills (composite PK) --------------------------------
    op.create_table(
        "resume_skills",
        sa.Column("resume_id", sa.Integer(), sa.ForeignKey("resumes.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("skill_id", sa.Integer(), sa.ForeignKey("skills.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("confidence", sa.Float(), nullable=False, server_default="1.0"),
    )

    # ---- interview_reports -------------------------------------------
    op.create_table(
        "interview_reports",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("session_id", sa.Integer(), sa.ForeignKey("interview_sessions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("overall_score", sa.Float(), nullable=False),
        sa.Column("performance_label", sa.String(40), nullable=False),
        sa.Column("category_scores", sa.JSON(), nullable=False),
        sa.Column("executive_summary", sa.Text(), nullable=False),
        sa.Column("strengths", sa.JSON(), nullable=False),
        sa.Column("growth_areas", sa.JSON(), nullable=False),
        sa.Column("question_feedback", sa.JSON(), nullable=False),
        sa.Column("recommendations", sa.JSON(), nullable=False),
        sa.Column("pdf_storage_key", sa.String(255), nullable=True),
        sa.Column("scoring_version", sa.String(40), nullable=False, server_default="report-v1"),
        *ts_cols(),
    )
    op.create_index("ix_interview_reports_user_id", "interview_reports", ["user_id"])
    op.create_index("ix_interview_reports_session_id", "interview_reports", ["session_id"], unique=True)

    # ---- career_matches ------------------------------------------------
    op.create_table(
        "career_matches",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("role_id", sa.Integer(), sa.ForeignKey("career_roles.id"), nullable=False),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column("matched_skills", sa.JSON(), nullable=False),
        sa.Column("missing_skills", sa.JSON(), nullable=False),
        sa.Column("explanation", sa.Text(), nullable=False),
        sa.Column("model_version", sa.String(40), nullable=False, server_default="rules-v1"),
        *ts_cols(),
    )
    op.create_index("ix_career_matches_user_id", "career_matches", ["user_id"])

    # ---- skill_gap_analyses ----------------------------------------
    op.create_table(
        "skill_gap_analyses",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("role_id", sa.Integer(), sa.ForeignKey("career_roles.id"), nullable=False),
        sa.Column("readiness_score", sa.Float(), nullable=False),
        sa.Column("matched_skills", sa.JSON(), nullable=False),
        sa.Column("missing_skills", sa.JSON(), nullable=False),
        sa.Column("priority_gaps", sa.JSON(), nullable=False),
        sa.Column("suggestions", sa.JSON(), nullable=False),
        sa.Column("scoring_version", sa.String(40), nullable=False, server_default="gap-v1"),
        *ts_cols(),
    )
    op.create_index("ix_skill_gap_analyses_user_id", "skill_gap_analyses", ["user_id"])

    # ---- learning_resources --------------------------------------
    op.create_table(
        "learning_resources",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(180), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("resource_type", sa.String(40), nullable=False),
        sa.Column("url", sa.String(500), nullable=False),
        sa.Column("skill_id", sa.Integer(), sa.ForeignKey("skills.id", ondelete="SET NULL"), nullable=True),
        sa.Column("premium_only", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        *ts_cols(),
    )

    # ---- user_resource_progress (composite PK) -----------------------
    op.create_table(
        "user_resource_progress",
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("resource_id", sa.Integer(), sa.ForeignKey("learning_resources.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("bookmarked", sa.Boolean(), nullable=False, server_default=sa.false()),
    )

    # ---- learning_roadmaps -------------------------------------------
    op.create_table(
        "learning_roadmaps",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("role_id", sa.Integer(), sa.ForeignKey("career_roles.id"), nullable=False),
        sa.Column("title", sa.String(160), nullable=False),
        sa.Column("status", sa.Enum("ACTIVE", "COMPLETED", "ARCHIVED", name="roadmap_status"), nullable=False, server_default="ACTIVE"),
        sa.Column("progress_percentage", sa.Float(), nullable=False, server_default="0"),
        *ts_cols(),
    )
    op.create_index("ix_learning_roadmaps_user_id", "learning_roadmaps", ["user_id"])

    # ---- roadmap_items -------------------------------------------
    op.create_table(
        "roadmap_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("roadmap_id", sa.Integer(), sa.ForeignKey("learning_roadmaps.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(160), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("item_type", sa.String(50), nullable=False),
        sa.Column("difficulty", sa.Enum("BEGINNER", "INTERMEDIATE", "ADVANCED", name="difficulty", create_type=False), nullable=False),
        sa.Column("order_no", sa.Integer(), nullable=False),
        sa.Column("estimated_hours", sa.Float(), nullable=False),
        sa.Column("resource_id", sa.Integer(), sa.ForeignKey("learning_resources.id", ondelete="SET NULL"), nullable=True),
        sa.Column("completed", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("progress_percentage", sa.Float(), nullable=False, server_default="0"),
        sa.Column("premium_only", sa.Boolean(), nullable=False, server_default=sa.false()),
        *ts_cols(),
    )
    op.create_index("ix_roadmap_items_roadmap_id", "roadmap_items", ["roadmap_id"])

    # ---- notifications -------------------------------------------------
    op.create_table(
        "notifications",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("type", sa.Enum("INTERVIEW", "RESUME", "LEARNING", "SUBSCRIPTION", "SYSTEM", name="notification_type"), nullable=False),
        sa.Column("title", sa.String(160), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("is_read", sa.Boolean(), nullable=False, server_default=sa.false()),
        *ts_cols(),
    )
    op.create_index("ix_notifications_user_id", "notifications", ["user_id"])
    op.create_index("ix_notifications_is_read", "notifications", ["is_read"])

    # ---- user_subscriptions ------------------------------------------
    op.create_table(
        "user_subscriptions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("plan_id", sa.Integer(), sa.ForeignKey("subscription_plans.id"), nullable=False),
        sa.Column("status", sa.Enum("ACTIVE", "CANCELLED", "EXPIRED", "PENDING", name="subscription_status"), nullable=False, server_default="ACTIVE"),
        sa.Column("starts_at", sa.DateTime(), nullable=False, server_default=now),
        sa.Column("ends_at", sa.DateTime(), nullable=True),
        *ts_cols(),
    )
    op.create_index("ix_user_subscriptions_user_id", "user_subscriptions", ["user_id"])

    # ---- usage_records ----------------------------------------------
    op.create_table(
        "usage_records",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("feature", sa.String(60), nullable=False),
        sa.Column("period_key", sa.String(10), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False, server_default="0"),
        *ts_cols(),
    )
    op.create_index("ix_usage_records_user_id", "usage_records", ["user_id"])
    op.create_index("ix_usage_records_feature", "usage_records", ["feature"])
    op.create_index("ix_usage_records_period_key", "usage_records", ["period_key"])

    # ---- billing_records --------------------------------------------
    op.create_table(
        "billing_records",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("description", sa.String(255), nullable=False),
        sa.Column("amount", sa.Numeric(10, 2), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False, server_default="LKR"),
        sa.Column("status", sa.String(30), nullable=False, server_default="DEMO"),
        sa.Column("external_reference", sa.String(100), nullable=True),
        *ts_cols(),
    )
    op.create_index("ix_billing_records_user_id", "billing_records", ["user_id"])

    # ---- support_tickets ----------------------------------------------
    op.create_table(
        "support_tickets",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("category", sa.String(50), nullable=False),
        sa.Column("subject", sa.String(180), nullable=False),
        sa.Column("status", sa.String(30), nullable=False, server_default="OPEN"),
        *ts_cols(),
    )
    op.create_index("ix_support_tickets_user_id", "support_tickets", ["user_id"])
    op.create_index("ix_support_tickets_status", "support_tickets", ["status"])

    # ---- support_messages -----------------------------------------
    op.create_table(
        "support_messages",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("ticket_id", sa.Integer(), sa.ForeignKey("support_tickets.id", ondelete="CASCADE"), nullable=False),
        sa.Column("sender_user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        *ts_cols(),
    )
    op.create_index("ix_support_messages_ticket_id", "support_messages", ["ticket_id"])

    # ---- user_achievements (composite PK) ----------------------------
    op.create_table(
        "user_achievements",
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("achievement_id", sa.Integer(), sa.ForeignKey("achievements.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("awarded_at", sa.DateTime(), nullable=False, server_default=now),
    )

    # ---- audit_logs ---------------------------------------------------
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("entity_type", sa.String(60), nullable=False),
        sa.Column("entity_id", sa.String(60), nullable=True),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=now),
    )
    op.create_index("ix_audit_logs_user_id", "audit_logs", ["user_id"])
    op.create_index("ix_audit_logs_action", "audit_logs", ["action"])
    op.create_index("ix_audit_logs_created_at", "audit_logs", ["created_at"])

    # ---- processing_jobs ----------------------------------------------
    op.create_table(
        "processing_jobs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("job_type", sa.String(50), nullable=False),
        sa.Column("entity_type", sa.String(50), nullable=False),
        sa.Column("entity_id", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(30), nullable=False, server_default="PROCESSING"),
        sa.Column("progress", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("current_stage", sa.String(160), nullable=False, server_default="Queued"),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        *ts_cols(),
    )
    op.create_index("ix_processing_jobs_user_id", "processing_jobs", ["user_id"])
    op.create_index("ix_processing_jobs_status", "processing_jobs", ["status"])


def downgrade() -> None:
    for table in [
        "processing_jobs", "audit_logs", "user_achievements", "support_messages",
        "support_tickets", "billing_records", "usage_records", "user_subscriptions",
        "notifications", "roadmap_items", "learning_roadmaps", "user_resource_progress",
        "learning_resources", "skill_gap_analyses", "career_matches", "interview_reports",
        "resume_skills", "resume_analyses", "answer_evaluations", "interview_answers",
        "session_questions", "interview_sessions", "interview_questions", "resumes",
        "user_skills", "action_tokens", "refresh_tokens", "user_profiles", "role_skills",
        "achievements", "subscription_plans", "career_roles", "skills", "users",
    ]:
        op.drop_table(table)
