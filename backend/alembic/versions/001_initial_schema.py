"""Initial database schema

Revision ID: 001_initial
Revises: 
Create Date: 2026-02-09

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Users
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(255), unique=True, nullable=False),
        sa.Column('username', sa.String(50), unique=True, nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=True),
        sa.Column('display_name', sa.String(100), nullable=True),
        sa.Column('bio', sa.String(280), nullable=True),
        sa.Column('avatar_url', sa.String(500), nullable=True),
        sa.Column('timezone', sa.String(50), default='UTC', nullable=False),
        sa.Column('level', sa.Integer, default=1, nullable=False),
        sa.Column('total_xp', sa.Integer, default=0, nullable=False),
        sa.Column('coins', sa.Integer, default=0, nullable=False),
        sa.Column('current_streak', sa.Integer, default=0, nullable=False),
        sa.Column('best_streak', sa.Integer, default=0, nullable=False),
        sa.Column('last_activity_date', sa.Date, nullable=True),
        sa.Column('streak_freeze_available', sa.Integer, default=1, nullable=False),
        sa.Column('friend_code', sa.String(20), unique=True, nullable=False),
        sa.Column('is_public', sa.Boolean, default=False, nullable=False),
        sa.Column('google_id', sa.String(255), unique=True, nullable=True),
        sa.Column('apple_id', sa.String(255), unique=True, nullable=True),
        sa.Column('notifications_enabled', sa.Boolean, default=True, nullable=False),
        sa.Column('theme', sa.String(20), default='dark', nullable=False),
        sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    op.create_index('ix_users_email', 'users', ['email'])
    op.create_index('ix_users_username', 'users', ['username'])
    op.create_index('ix_users_friend_code', 'users', ['friend_code'])

    # Characters
    op.create_table(
        'characters',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False),
        sa.Column('name', sa.String(50), nullable=False),
        sa.Column('character_class', sa.String(20), default='warrior', nullable=False),
        sa.Column('strength', sa.Integer, default=5, nullable=False),
        sa.Column('endurance', sa.Integer, default=5, nullable=False),
        sa.Column('agility', sa.Integer, default=5, nullable=False),
        sa.Column('intelligence', sa.Integer, default=5, nullable=False),
        sa.Column('available_points', sa.Integer, default=0, nullable=False),
        sa.Column('body_type', sa.String(20), default='light', nullable=False),
        sa.Column('skin_color', sa.String(20), default='peach', nullable=False),
        sa.Column('hair_style', sa.String(30), default='short', nullable=False),
        sa.Column('hair_color', sa.String(20), default='brown', nullable=False),
        sa.Column('equipped_weapon', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('equipped_armor', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('equipped_accessory', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('wins', sa.Integer, default=0, nullable=False),
        sa.Column('losses', sa.Integer, default=0, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )

    # Habits
    op.create_table(
        'habits',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('icon', sa.String(50), default='✅', nullable=False),
        sa.Column('color', sa.String(20), default='#6366F1', nullable=False),
        sa.Column('category', sa.String(50), default='general', nullable=False),
        sa.Column('frequency_type', sa.String(20), default='daily', nullable=False),
        sa.Column('frequency_days', postgresql.ARRAY(sa.Integer), default=[], nullable=False),
        sa.Column('frequency_count', sa.Integer, nullable=True),
        sa.Column('target_value', sa.Integer, nullable=True),
        sa.Column('unit', sa.String(30), nullable=True),
        sa.Column('reminder_time', sa.Time, nullable=True),
        sa.Column('reminder_enabled', sa.Boolean, default=False, nullable=False),
        sa.Column('current_streak', sa.Integer, default=0, nullable=False),
        sa.Column('best_streak', sa.Integer, default=0, nullable=False),
        sa.Column('total_completions', sa.Integer, default=0, nullable=False),
        sa.Column('total_xp_earned', sa.Integer, default=0, nullable=False),
        sa.Column('position', sa.Integer, default=0, nullable=False),
        sa.Column('is_archived', sa.Boolean, default=False, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    op.create_index('ix_habits_user_id', 'habits', ['user_id'])

    # Tasks
    op.create_table(
        'tasks',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('category', sa.String(50), default='general', nullable=False),
        sa.Column('priority', sa.String(20), default='medium', nullable=False),
        sa.Column('due_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('status', sa.String(20), default='pending', nullable=False),
        sa.Column('difficulty', sa.String(20), nullable=True),
        sa.Column('xp_reward', sa.Integer, nullable=True),
        sa.Column('coins_reward', sa.Integer, nullable=True),
        sa.Column('ai_evaluated', sa.Boolean, default=False, nullable=False),
        sa.Column('ai_reasoning', sa.Text, nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    op.create_index('ix_tasks_user_id', 'tasks', ['user_id'])
    op.create_index('ix_tasks_status', 'tasks', ['status'])

    # Completions
    op.create_table(
        'completions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('habit_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('habits.id', ondelete='CASCADE'), nullable=False),
        sa.Column('completed_date', sa.Date, nullable=False),
        sa.Column('value', sa.Integer, default=1, nullable=False),
        sa.Column('xp_earned', sa.Integer, default=0, nullable=False),
        sa.Column('coins_earned', sa.Integer, default=0, nullable=False),
        sa.Column('streak_at_completion', sa.Integer, default=0, nullable=False),
        sa.Column('note', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_completions_user_date', 'completions', ['user_id', 'completed_date'])
    op.create_unique_constraint('uq_completions_habit_date', 'completions', ['habit_id', 'completed_date'])

    # Items
    op.create_table(
        'items',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('category', sa.String(30), nullable=False),
        sa.Column('slot', sa.String(20), nullable=True),
        sa.Column('rarity', sa.String(20), default='common', nullable=False),
        sa.Column('price', sa.Integer, default=0, nullable=False),
        sa.Column('level_required', sa.Integer, default=1, nullable=False),
        sa.Column('strength_bonus', sa.Integer, default=0, nullable=False),
        sa.Column('endurance_bonus', sa.Integer, default=0, nullable=False),
        sa.Column('agility_bonus', sa.Integer, default=0, nullable=False),
        sa.Column('intelligence_bonus', sa.Integer, default=0, nullable=False),
        sa.Column('sprite_sheet', sa.String(200), nullable=True),
        sa.Column('is_available', sa.Boolean, default=True, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # User Inventory
    op.create_table(
        'user_inventory',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('item_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('items.id', ondelete='CASCADE'), nullable=False),
        sa.Column('quantity', sa.Integer, default=1, nullable=False),
        sa.Column('acquired_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_unique_constraint('uq_user_inventory', 'user_inventory', ['user_id', 'item_id'])

    # Badges
    op.create_table(
        'badges',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('category', sa.String(50), nullable=False),
        sa.Column('tier', sa.String(20), default='bronze', nullable=False),
        sa.Column('icon', sa.String(100), nullable=True),
        sa.Column('condition_type', sa.String(50), nullable=False),
        sa.Column('condition_value', sa.Integer, nullable=False),
        sa.Column('xp_reward', sa.Integer, default=0, nullable=False),
        sa.Column('coins_reward', sa.Integer, default=0, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # User Badges
    op.create_table(
        'user_badges',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('badge_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('badges.id', ondelete='CASCADE'), nullable=False),
        sa.Column('unlocked_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('is_displayed', sa.Boolean, default=False, nullable=False),
    )
    op.create_unique_constraint('uq_user_badges', 'user_badges', ['user_id', 'badge_id'])

    # Friendships
    op.create_table(
        'friendships',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('requester_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('addressee_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('status', sa.String(20), default='pending', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    op.create_unique_constraint('uq_friendships', 'friendships', ['requester_id', 'addressee_id'])

    # Combats
    op.create_table(
        'combats',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('challenger_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('defender_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('winner_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('status', sa.String(20), default='pending', nullable=False),
        sa.Column('combat_log', postgresql.JSONB, nullable=True),
        sa.Column('challenger_hp_start', sa.Integer, nullable=True),
        sa.Column('defender_hp_start', sa.Integer, nullable=True),
        sa.Column('bet_coins', sa.Integer, default=0, nullable=False),
        sa.Column('xp_reward', sa.Integer, default=0, nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Daily Stats
    op.create_table(
        'daily_stats',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('date', sa.Date, nullable=False),
        sa.Column('habits_completed', sa.Integer, default=0, nullable=False),
        sa.Column('habits_total', sa.Integer, default=0, nullable=False),
        sa.Column('tasks_completed', sa.Integer, default=0, nullable=False),
        sa.Column('xp_earned', sa.Integer, default=0, nullable=False),
        sa.Column('coins_earned', sa.Integer, default=0, nullable=False),
        sa.Column('streak_day', sa.Integer, default=0, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_unique_constraint('uq_daily_stats', 'daily_stats', ['user_id', 'date'])
    op.create_index('ix_daily_stats_user_date', 'daily_stats', ['user_id', 'date'])

    # Notifications
    op.create_table(
        'notifications',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('type', sa.String(50), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('message', sa.Text, nullable=True),
        sa.Column('data', postgresql.JSONB, nullable=True),
        sa.Column('is_read', sa.Boolean, default=False, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_notifications_user_id', 'notifications', ['user_id'])


def downgrade() -> None:
    op.drop_table('notifications')
    op.drop_table('daily_stats')
    op.drop_table('combats')
    op.drop_table('friendships')
    op.drop_table('user_badges')
    op.drop_table('badges')
    op.drop_table('user_inventory')
    op.drop_table('items')
    op.drop_table('completions')
    op.drop_table('tasks')
    op.drop_table('habits')
    op.drop_table('characters')
    op.drop_table('users')
