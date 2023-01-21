"""empty message

Revision ID: a554aef46b4e
Revises: 
Create Date: 2022-12-11 14:49:51.472524

"""
import uuid

import bcrypt
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'a554aef46b4e'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('credentials',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
    sa.Column('name', sa.String(length=256), nullable=False),
    sa.Column('username', sa.String(length=256), nullable=False),
    sa.Column('password', sa.String(length=2048), nullable=False),
    sa.Column('ssh_key', sa.String(length=4096), nullable=False),
    sa.Column('type', sa.String(length=32), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_credentials')),
    sa.UniqueConstraint('id', name=op.f('uq_credentials_id')),
    sa.UniqueConstraint('name', name=op.f('uq_credentials_name'))
    )
    op.create_table('nodes',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
    sa.Column('name', sa.String(length=256), nullable=False),
    sa.Column('address', sa.String(length=512), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_nodes')),
    sa.UniqueConstraint('address', name=op.f('uq_nodes_address')),
    sa.UniqueConstraint('id', name=op.f('uq_nodes_id')),
    sa.UniqueConstraint('name', name=op.f('uq_nodes_name'))
    )
    op.create_table('repositories',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
    sa.Column('name', sa.String(length=256), nullable=False),
    sa.Column('description', sa.String(length=1024), nullable=False),
    sa.Column('icon', sa.String(length=1024), nullable=True),
    sa.Column('commits', sa.Integer(), nullable=True),
    sa.Column('size', sa.Integer(), nullable=True),
    sa.Column('last_commit', sa.TIMESTAMP(), nullable=True),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_repositories')),
    sa.UniqueConstraint('id', name=op.f('uq_repositories_id')),
    sa.UniqueConstraint('name', name=op.f('uq_repositories_name'))
    )
    op.create_table('scripts_expect',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('protocol', sa.String(length=128), nullable=False),
    sa.Column('port', sa.Integer(), nullable=False),
    sa.Column('username_prompt', sa.String(length=256), nullable=False),
    sa.Column('password_prompt', sa.String(length=256), nullable=False),
    sa.Column('default_prompt', sa.String(length=256), nullable=False),
    sa.Column('timeout', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_scripts_expect')),
    sa.UniqueConstraint('id', name=op.f('uq_scripts_expect_id'))
    )
    op.create_table('scripts_file_transfer',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('path', sa.String(length=512), nullable=False),
    sa.Column('protocol', sa.String(length=16), nullable=False),
    sa.Column('port', sa.Integer(), nullable=False),
    sa.Column('timeout', sa.Integer(), nullable=False),
    sa.Column('ftp_secure', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_scripts_file_transfer')),
    sa.UniqueConstraint('id', name=op.f('uq_scripts_file_transfer_id'))
    )
    op.create_table('scripts_wget',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('link', sa.String(length=512), nullable=False),
    sa.Column('timeout', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_scripts_wget')),
    sa.UniqueConstraint('id', name=op.f('uq_scripts_wget_id'))
    )
    op.create_table('user_groups',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
    sa.Column('name', sa.String(length=256), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_user_groups')),
    sa.UniqueConstraint('id', name=op.f('uq_user_groups_id')),
    sa.UniqueConstraint('name', name=op.f('uq_user_groups_name'))
    )
    op.create_table('users',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
    sa.Column('username', sa.String(length=80), nullable=False),
    sa.Column('email', sa.String(length=128), server_default='', nullable=False),
    sa.Column('password', sa.String(length=512), nullable=False),
    sa.Column('firstname', sa.String(length=64), server_default='', nullable=False),
    sa.Column('lastname', sa.String(length=64), server_default='', nullable=False),
    sa.Column('pic', sa.String(length=512), nullable=True),
    sa.Column('language', sa.String(length=128), server_default='en_EN', nullable=False),
    sa.Column('timezone', sa.String(length=32), server_default='GMT-0', nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_users')),
    sa.UniqueConstraint('id', name=op.f('uq_users_id')),
    sa.UniqueConstraint('username', name=op.f('uq_users_username'))
    )
    op.create_table('configs_bin',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
    sa.Column('name', sa.String(length=256), nullable=False),
    sa.Column('size', sa.Integer(), nullable=True),
    sa.Column('last_modification', sa.TIMESTAMP(), nullable=True),
    sa.Column('address', sa.String(length=256), nullable=False),
    sa.Column('username', sa.String(length=256), nullable=False),
    sa.Column('protocol', sa.String(length=256), nullable=False),
    sa.Column('repo_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('style', sa.String(length=1024), nullable=True),
    sa.Column('icon', sa.String(length=1024), nullable=True),
    sa.ForeignKeyConstraint(['repo_id'], ['repositories.id'], name=op.f('fk_configs_bin_repo_id_repositories')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_configs_bin')),
    sa.UniqueConstraint('id', name=op.f('uq_configs_bin_id'))
    )
    op.create_table('expectations',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('script_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('prompt', sa.String(length=256), nullable=False),
    sa.Column('cmd', sa.String(length=1024), nullable=False),
    sa.Column('timeout', sa.Integer(), nullable=False),
    sa.Column('save', sa.Boolean(), nullable=False),
    sa.Column('order', sa.Integer(), nullable=False),
    sa.Column('secret', sa.Boolean(), nullable=False),
    sa.Column('skip_top', sa.Integer(), nullable=False),
    sa.Column('skip_bottom', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['script_id'], ['scripts_expect.id'], name=op.f('fk_expectations_script_id_scripts_expect')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_expectations')),
    sa.UniqueConstraint('id', name=op.f('uq_expectations_id'))
    )
    op.create_table('notifications_repo',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('repo_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('group_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.ForeignKeyConstraint(['group_id'], ['user_groups.id'], name=op.f('fk_notifications_repo_group_id_user_groups')),
    sa.ForeignKeyConstraint(['repo_id'], ['repositories.id'], name=op.f('fk_notifications_repo_repo_id_repositories')),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_notifications_repo_user_id_users')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_notifications_repo')),
    sa.UniqueConstraint('id', name=op.f('uq_notifications_repo_id'))
    )
    op.create_table('repo_groups',
    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('name', sa.String(length=256), nullable=False),
    sa.Column('description', sa.String(length=1024), nullable=False),
    sa.Column('repo_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('parent_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('fullpath', sa.Text(), nullable=False),
    sa.Column('fullpath_id', sa.Text(), nullable=False),
    sa.Column('level', sa.Integer(), nullable=False),
    sa.Column('expandable', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['parent_id'], ['repo_groups.id'], name=op.f('fk_repo_groups_parent_id_repo_groups')),
    sa.ForeignKeyConstraint(['repo_id'], ['repositories.id'], name=op.f('fk_repo_groups_repo_id_repositories')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_repo_groups'))
    )
    op.create_table('repo_stats',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('repo_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('date', sa.TIMESTAMP(), nullable=False),
    sa.Column('files_changed', sa.Integer(), nullable=False),
    sa.Column('insertions', sa.Integer(), nullable=False),
    sa.Column('deletions', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['repo_id'], ['repositories.id'], name=op.f('fk_repo_stats_repo_id_repositories')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_repo_stats')),
    sa.UniqueConstraint('id', name=op.f('uq_repo_stats_id'))
    )
    op.create_table('scripts',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
    sa.Column('name', sa.String(length=256), nullable=False),
    sa.Column('type', sa.String(length=128), nullable=False),
    sa.Column('expect_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('file_transfer_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('wget_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.ForeignKeyConstraint(['expect_id'], ['scripts_expect.id'], name=op.f('fk_scripts_expect_id_scripts_expect')),
    sa.ForeignKeyConstraint(['file_transfer_id'], ['scripts_file_transfer.id'], name=op.f('fk_scripts_file_transfer_id_scripts_file_transfer')),
    sa.ForeignKeyConstraint(['wget_id'], ['scripts_wget.id'], name=op.f('fk_scripts_wget_id_scripts_wget')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_scripts')),
    sa.UniqueConstraint('id', name=op.f('uq_scripts_id')),
    sa.UniqueConstraint('name', name=op.f('uq_scripts_name'))
    )
    op.create_table('sessions',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('access_jti', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('refresh_jti', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('new_jti', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('client', sa.String(), nullable=True),
    sa.Column('ip_address', sa.String(length=45), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_sessions_user_id_users')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_sessions')),
    sa.UniqueConstraint('id', name=op.f('uq_sessions_id'))
    )
    op.create_table('user_group_members',
    sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('user_group_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.ForeignKeyConstraint(['user_group_id'], ['user_groups.id'], name=op.f('fk_user_group_members_user_group_id_user_groups')),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_user_group_members_user_id_users'))
    )
    op.create_table('user_group_permissions',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('user_group_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('permission', sa.String(length=80), nullable=False),
    sa.ForeignKeyConstraint(['user_group_id'], ['user_groups.id'], name=op.f('fk_user_group_permissions_user_group_id_user_groups')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_user_group_permissions')),
    sa.UniqueConstraint('id', name=op.f('uq_user_group_permissions_id'))
    )
    op.create_table('configs',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
    sa.Column('name', sa.String(length=256), nullable=False),
    sa.Column('exists', sa.Boolean(), nullable=False),
    sa.Column('status', sa.Boolean(), nullable=True),
    sa.Column('in_process', sa.Boolean(), nullable=True),
    sa.Column('size', sa.Integer(), nullable=True),
    sa.Column('last_modification', sa.TIMESTAMP(), nullable=True),
    sa.Column('node_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('credentials_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('script_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('repo_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('repo_group_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('style', sa.String(length=1024), nullable=True),
    sa.Column('icon', sa.String(length=1024), nullable=True),
    sa.Column('notifications', sa.String(length=2048), nullable=False),
    sa.ForeignKeyConstraint(['credentials_id'], ['credentials.id'], name=op.f('fk_configs_credentials_id_credentials')),
    sa.ForeignKeyConstraint(['node_id'], ['nodes.id'], name=op.f('fk_configs_node_id_nodes')),
    sa.ForeignKeyConstraint(['repo_group_id'], ['repo_groups.id'], name=op.f('fk_configs_repo_group_id_repo_groups')),
    sa.ForeignKeyConstraint(['repo_id'], ['repositories.id'], name=op.f('fk_configs_repo_id_repositories')),
    sa.ForeignKeyConstraint(['script_id'], ['scripts.id'], name=op.f('fk_configs_script_id_scripts')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_configs')),
    sa.UniqueConstraint('id', name=op.f('uq_configs_id'))
    )
    op.create_table('notifications_repo_group',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('repo_group_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('group_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.ForeignKeyConstraint(['group_id'], ['user_groups.id'], name=op.f('fk_notifications_repo_group_group_id_user_groups')),
    sa.ForeignKeyConstraint(['repo_group_id'], ['repo_groups.id'], name=op.f('fk_notifications_repo_group_repo_group_id_repo_groups')),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_notifications_repo_group_user_id_users')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_notifications_repo_group')),
    sa.UniqueConstraint('id', name=op.f('uq_notifications_repo_group_id'))
    )
    op.create_table('commit_notes',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
    sa.Column('config_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('config_bin_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('commit', sa.String(length=40), nullable=False),
    sa.Column('name', sa.String(length=256), nullable=False),
    sa.Column('description', sa.String(length=4096), nullable=False),
    sa.ForeignKeyConstraint(['config_bin_id'], ['configs_bin.id'], name=op.f('fk_commit_notes_config_bin_id_configs_bin')),
    sa.ForeignKeyConstraint(['config_id'], ['configs.id'], name=op.f('fk_commit_notes_config_id_configs')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_commit_notes')),
    sa.UniqueConstraint('id', name=op.f('uq_commit_notes_id'))
    )
    op.create_table('config_reports',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('config_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('message', sa.String(length=4096), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['config_id'], ['configs.id'], name=op.f('fk_config_reports_config_id_configs')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_config_reports')),
    sa.UniqueConstraint('id', name=op.f('uq_config_reports_id'))
    )
    op.create_table('notifications_config',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('config_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('group_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.ForeignKeyConstraint(['config_id'], ['configs.id'], name=op.f('fk_notifications_config_config_id_configs')),
    sa.ForeignKeyConstraint(['group_id'], ['user_groups.id'], name=op.f('fk_notifications_config_group_id_user_groups')),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_notifications_config_user_id_users')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_notifications_config')),
    sa.UniqueConstraint('id', name=op.f('uq_notifications_config_id'))
    )
    # ### end Alembic commands ###

    bind = op.get_bind()
    session = sa.orm.Session(bind=bind)
    session.execute(f"INSERT INTO users (username, id, password) "
                    f"VALUES ('admin', '{uuid.uuid4()}'"
                    f", '{bcrypt.hashpw('admin'.encode(), bcrypt.gensalt()).decode('utf-8')}')")

    session.execute(f"INSERT INTO user_groups (name, id) VALUES ('Administrators', '{uuid.uuid4()}')")
    group = session.execute("SELECT * FROM user_groups where name = 'Administrators'").fetchone()
    session.execute(f"INSERT INTO user_group_permissions (id, user_group_id, permission) "
                    f"VALUES ('{uuid.uuid4()}', '{group[0]}', 'admin')")

    user = session.execute("SELECT * FROM users where username = 'admin'").fetchone()
    session.execute(f"INSERT INTO user_group_members (user_id, user_group_id) "
                    f"VALUES ('{user[0]}', '{group[0]}')")

    session.execute(f"INSERT INTO user_groups (name, id) VALUES ('Demo', '{uuid.uuid4()}')")
    group_demo = session.execute("SELECT * FROM user_groups where name = 'Demo'").fetchone()
    session.execute(f"INSERT INTO user_group_permissions (id, user_group_id, permission) "
                    f"VALUES ('{uuid.uuid4()}', '{group_demo[0]}', 'demo')")

    session.execute(f"INSERT INTO user_groups (name, id) VALUES ('Managers', '{uuid.uuid4()}')")
    group_demo = session.execute("SELECT * FROM user_groups where name = 'Managers'").fetchone()
    session.execute(f"INSERT INTO user_group_permissions (id, user_group_id, permission) "
                    f"VALUES ('{uuid.uuid4()}', '{group_demo[0]}', 'manager')")

    session.execute(f"INSERT INTO repositories (id, name, description) "
                    f"VALUES ('{uuid.uuid4()}','default', 'Default repository')")


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('notifications_config')
    op.drop_table('config_reports')
    op.drop_table('commit_notes')
    op.drop_table('notifications_repo_group')
    op.drop_table('configs')
    op.drop_table('user_group_permissions')
    op.drop_table('user_group_members')
    op.drop_table('sessions')
    op.drop_table('scripts')
    op.drop_table('repo_stats')
    op.drop_table('repo_groups')
    op.drop_table('notifications_repo')
    op.drop_table('expectations')
    op.drop_table('configs_bin')
    op.drop_table('users')
    op.drop_table('user_groups')
    op.drop_table('scripts_wget')
    op.drop_table('scripts_file_transfer')
    op.drop_table('scripts_expect')
    op.drop_table('repositories')
    op.drop_table('nodes')
    op.drop_table('credentials')
    # ### end Alembic commands ###