"""Models package - Import all models for SQLAlchemy mapper registration."""

from .base import Base, UUIDMixin
from .user import User
from .character import Character
from .habit import Habit
from .task import Task
from .subtask import Subtask
from .completion import Completion
from .item import Item
from .inventory import UserInventory
from .badge import Badge, UserBadge
from .friendship import Friendship
from .combat import Combat
from .stats import DailyStats
from .notification import Notification
from .transaction import CoinTransaction, XPTransaction

__all__ = [
    'Base',
    'UUIDMixin',
    'User',
    'Character',
    'Habit',
    'Task',
    'Subtask',
    'Completion',
    'Item',
    'UserInventory',
    'Badge',
    'UserBadge',
    'Friendship',
    'Combat',
    'DailyStats',
    'Notification',
    'CoinTransaction',
    'XPTransaction',
]
