"""empty message

Revision ID: 5f5b0bf99cf7
Revises: a554aef46b4e
Create Date: 2022-12-19 14:55:54.538477

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5f5b0bf99cf7'
down_revision = 'a554aef46b4e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(op.f('uq_commit_notes_id'), 'commit_notes', ['id'])
    op.create_unique_constraint(op.f('uq_config_reports_id'), 'config_reports', ['id'])
    op.create_unique_constraint(op.f('uq_configs_id'), 'configs', ['id'])
    op.create_unique_constraint(op.f('uq_configs_bin_id'), 'configs_bin', ['id'])
    op.create_unique_constraint(op.f('uq_credentials_id'), 'credentials', ['id'])
    op.create_unique_constraint(op.f('uq_expectations_id'), 'expectations', ['id'])
    op.create_unique_constraint(op.f('uq_nodes_id'), 'nodes', ['id'])
    op.create_unique_constraint(op.f('uq_notifications_config_id'), 'notifications_config', ['id'])
    op.create_unique_constraint(op.f('uq_notifications_repo_id'), 'notifications_repo', ['id'])
    op.create_unique_constraint(op.f('uq_notifications_repo_group_id'), 'notifications_repo_group', ['id'])
    op.create_unique_constraint(op.f('uq_repo_stats_id'), 'repo_stats', ['id'])
    op.create_unique_constraint(op.f('uq_repositories_id'), 'repositories', ['id'])
    op.create_unique_constraint(op.f('uq_scripts_id'), 'scripts', ['id'])
    op.create_unique_constraint(op.f('uq_scripts_expect_id'), 'scripts_expect', ['id'])
    op.create_unique_constraint(op.f('uq_scripts_file_transfer_id'), 'scripts_file_transfer', ['id'])
    op.create_unique_constraint(op.f('uq_scripts_wget_id'), 'scripts_wget', ['id'])
    op.create_unique_constraint(op.f('uq_sessions_id'), 'sessions', ['id'])
    op.create_unique_constraint(op.f('uq_user_group_permissions_id'), 'user_group_permissions', ['id'])
    op.create_unique_constraint(op.f('uq_user_groups_id'), 'user_groups', ['id'])
    op.create_unique_constraint(op.f('uq_users_id'), 'users', ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(op.f('uq_users_id'), 'users', type_='unique')
    op.drop_constraint(op.f('uq_user_groups_id'), 'user_groups', type_='unique')
    op.drop_constraint(op.f('uq_user_group_permissions_id'), 'user_group_permissions', type_='unique')
    op.drop_constraint(op.f('uq_sessions_id'), 'sessions', type_='unique')
    op.drop_constraint(op.f('uq_scripts_wget_id'), 'scripts_wget', type_='unique')
    op.drop_constraint(op.f('uq_scripts_file_transfer_id'), 'scripts_file_transfer', type_='unique')
    op.drop_constraint(op.f('uq_scripts_expect_id'), 'scripts_expect', type_='unique')
    op.drop_constraint(op.f('uq_scripts_id'), 'scripts', type_='unique')
    op.drop_constraint(op.f('uq_repositories_id'), 'repositories', type_='unique')
    op.drop_constraint(op.f('uq_repo_stats_id'), 'repo_stats', type_='unique')
    op.drop_constraint(op.f('uq_notifications_repo_group_id'), 'notifications_repo_group', type_='unique')
    op.drop_constraint(op.f('uq_notifications_repo_id'), 'notifications_repo', type_='unique')
    op.drop_constraint(op.f('uq_notifications_config_id'), 'notifications_config', type_='unique')
    op.drop_constraint(op.f('uq_nodes_id'), 'nodes', type_='unique')
    op.drop_constraint(op.f('uq_expectations_id'), 'expectations', type_='unique')
    op.drop_constraint(op.f('uq_credentials_id'), 'credentials', type_='unique')
    op.drop_constraint(op.f('uq_configs_bin_id'), 'configs_bin', type_='unique')
    op.drop_constraint(op.f('uq_configs_id'), 'configs', type_='unique')
    op.drop_constraint(op.f('uq_config_reports_id'), 'config_reports', type_='unique')
    op.drop_constraint(op.f('uq_commit_notes_id'), 'commit_notes', type_='unique')
    # ### end Alembic commands ###
