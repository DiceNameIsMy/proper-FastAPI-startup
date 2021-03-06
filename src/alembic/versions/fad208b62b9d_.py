"""empty message

Revision ID: fad208b62b9d
Revises: b167f40f348f
Create Date: 2022-03-10 15:53:05.583925

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fad208b62b9d'
down_revision = 'b167f40f348f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('verification_codes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('code', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user_id', 'code')
    )
    op.create_index('verification_codes_user_id_idx', 'verification_codes', ['user_id', 'code'], unique=False)
    op.add_column('users', sa.Column('is_email_verified', sa.Boolean(), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'is_email_verified')
    op.drop_index('verification_codes_user_id_idx', table_name='verification_codes')
    op.drop_table('verification_codes')
    # ### end Alembic commands ###
