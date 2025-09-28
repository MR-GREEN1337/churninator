"""Update agent run log and result structure

Revision ID: c110a9535ac2
Revises: 2c3914f9c5e9
Create Date: 2025-09-28 16:14:57.869567

"""

from typing import Sequence, Union


# revision identifiers, used by Alembic.
revision: str = "c110a9535ac2"
down_revision: Union[str, Sequence[str], None] = "2c3914f9c5e9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
