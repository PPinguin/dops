"""solution answer

Revision ID: 55d80f79736f
Revises: 
Create Date: 2021-05-25 19:33:37.515324

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '55d80f79736f'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=64), nullable=True),
    sa.Column('username', sa.String(length=64), nullable=True),
    sa.Column('password', sa.String(length=128), nullable=True),
    sa.Column('points', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=True)
    op.create_index(op.f('ix_user_username'), 'user', ['username'], unique=False)
    op.create_table('followers',
    sa.Column('follower', sa.Integer(), nullable=True),
    sa.Column('followed', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['followed'], ['user.id'], ),
    sa.ForeignKeyConstraint(['follower'], ['user.id'], )
    )
    op.create_table('riddle',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('body', sa.Text(), nullable=False),
    sa.Column('answer', sa.String(length=80), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('theme', sa.String(length=7), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_riddle_timestamp'), 'riddle', ['timestamp'], unique=False)
    op.create_table('solution',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('riddle_id', sa.Integer(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('answer', sa.String(length=80), nullable=True),
    sa.ForeignKeyConstraint(['riddle_id'], ['riddle.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('solution')
    op.drop_index(op.f('ix_riddle_timestamp'), table_name='riddle')
    op.drop_table('riddle')
    op.drop_table('followers')
    op.drop_index(op.f('ix_user_username'), table_name='user')
    op.drop_index(op.f('ix_user_email'), table_name='user')
    op.drop_table('user')
    # ### end Alembic commands ###
