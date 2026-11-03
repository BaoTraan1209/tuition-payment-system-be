
"""create tuition fees, payments and payment logs tables

Revision ID: 8dc1e3d2ad28
Revises: 2886bf3b692b
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '8dc1e3d2ad28'
down_revision: Union[str, Sequence[str], None] = '2886bf3b692b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    op.create_table(
        'tuition_fees',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.String(36), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('amount', sa.Integer(), nullable=False),
        sa.Column('due_date', sa.Date(), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='UNPAID'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        'payments',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('order_id', sa.String(100), nullable=False),
        sa.Column('user_id', sa.String(36), nullable=False),
        sa.Column('tuition_fee_id', sa.Integer(), nullable=False),
        sa.Column('amount', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='PENDING'),
        sa.Column('vnp_transaction_no', sa.String(100), nullable=True),
        sa.Column('response_code', sa.String(10), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.ForeignKeyConstraint(['tuition_fee_id'], ['tuition_fees.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('order_id', name='uq_payments_order_id')
    )

    op.create_table(
        'payment_logs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('payment_id', sa.Integer(), nullable=False),
        sa.Column('event', sa.String(50), nullable=False),
        sa.Column('response_code', sa.String(10), nullable=True),
        sa.Column('transaction_no', sa.String(100), nullable=True),
        sa.Column('message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['payment_id'], ['payments.id']),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('payment_logs')
    op.drop_table('payments')
    op.drop_table('tuition_fees')
