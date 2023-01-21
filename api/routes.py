from flask_restful import Api
from api.src.resources import User, UserTable, UserGroup, AuthLogin, UserGroupTable, UserGroupReferences, UserInfo,\
    UserGroupPermissions, Script, Smtp, SmtpTest, UserSubscriptionsTable, AuthRefreshToken, AuthLogout,\
    NotificationsConfig, NotificationsRepoGroup, NotificationsRepository, ConfigData,\
    ScriptTable, ScriptReferences, Node, NodeTable, NodeReferences, Credentials, CredentialsTable, CommitNotes,\
    CredentialsReferences, Config, ConfigTable, ConfigTest, ConfigReport, ConfigBin, ConfigBinTable, ConfigDownload,\
    RepositoryTable, RepoGroupTable, Repository, RepoGroup, RepoGroupTree, EngineProgress,\
    ConfigGitDiff, ConfigGitLog, EngineAction, EngineStatus, CronEngine, Session, SessionTable,\
    ExportSettings, ImportSettings, UpdateInfo, AuthChangePassword,\
    BriefStats, StatsRepoSize, StatsRepoConfigs, StatsConfigError, StatsConfigLatest,\
    ProjectVersion


class RouteMaker:

    _routes = [
        (AuthLogin, '/login', '/auth/login'),
        (AuthLogout, '/logout', '/auth/logout'),
        (AuthRefreshToken, '/auth/refresh-token'),
        (AuthChangePassword, '/auth/change-password'),

        (User, '/user', '/user/<string:user_id>'),
        (UserInfo, '/user/info'),
        (UserTable, '/user/table'),
        (UserSubscriptionsTable, '/user/<string:user_id>/subscriptions'),

        (Session, '/user/session/<string:session_id>'),
        (SessionTable, '/user/session/table'),

        (UserGroup, '/user-group', '/user-group/<string:group_id>'),
        (UserGroupTable, '/user-group/table'),
        (UserGroupReferences, '/user-group/references/<string:group_id>'),
        (UserGroupPermissions, '/user-group/permissions'),

        (Script, '/script', '/script/<string:script_id>'),
        (ScriptTable, '/script/table'),
        (ScriptReferences, '/script/references/<string:script_id>'),

        (Node, '/node', '/node/<string:node_id>'),
        (NodeTable, '/node/table'),
        (NodeReferences, '/node/references/<string:node_id>'),

        (Credentials, '/credentials', '/credentials/<string:credentials_id>'),
        (CredentialsTable, '/credentials/table'),
        (CredentialsReferences, '/credentials/references/<string:credentials_id>'),

        (Config, '/repository/<string:repo_id>/config', '/repository/<string:repo_id>/config/<string:config_id>'),
        (ConfigTable, '/repository/<string:repo_id>/config/table',
         '/repository/<string:repo_id>/group/<string:group_id>/config/table'),
        (ConfigTest, '/config/test'),
        (ConfigDownload, '/config/<string:config_id>/download',
         '/config/<string:config_id>/download/<string:commit>',
         '/bin/config/<string:config_id>/download/<string:commit>'),
        (ConfigData, '/config/<string:config_id>/data',
         '/config/<string:config_id>/data/commit/<string:commit>',
         '/bin/config/<string:config_id>/data/commit/<string:commit>'),
        (ConfigReport, '/config/<string:config_id>/report'),

        (ConfigGitLog, '/config-viewer/git/log/<string:config_id>', '/bin/config-viewer/git/log/<string:config_id>'),
        (ConfigGitDiff, '/config-viewer/git/diff/<string:config_id>', '/bin/config-viewer/git/diff/<string:config_id>'),
        (CommitNotes, '/config-viewer/<string:config_id>/commit/<string:commit>/notes',
         '/bin/config-viewer/<string:config_id>/commit/<string:commit>/notes'
         ),

        (ConfigBin, '/repository/<string:repo_id>/bin/config/<string:config_bin_id>'),
        (ConfigBinTable, '/repository/<string:repo_id>/bin/config/table'),

        (Repository, '/repository', '/repository/<string:repo_id>'),
        (RepositoryTable, '/repository/table'),
        (RepoGroup, '/repository/<string:repo_id>/group', '/repository/<string:repo_id>/group/<string:repo_group_id>'),
        (RepoGroupTable, '/repository/<string:repo_id>/group/table',
         '/repository/<string:repo_id>/group/table/<string:exclude_id>'),
        (RepoGroupTree, '/repository/<string:repo_id>/group/tree',
         '/repository/<string:repo_id>/group/tree/<string:group_id>'),

        # Notifications
        (NotificationsConfig, '/config/<string:config_id>/notifications'),
        (NotificationsRepoGroup, '/repository/group/<string:repo_group_id>/notifications'),
        (NotificationsRepository, '/repository/<string:repo_id>/notifications'),

        (EngineStatus, '/engine',),
        (EngineAction, '/engine/<string:action>'),
        (EngineProgress, '/engine/progress'),

        (CronEngine, '/cron/engine'),

        (ExportSettings, '/settings/export'),
        (ImportSettings, '/settings/import'),

        (Smtp, '/settings/smtp'),
        (SmtpTest, '/settings/smtp/test'),

        (BriefStats, '/stats'),
        (StatsRepoSize, '/stats/repository/size', '/stats/repository/size/<int:limit>'),
        (StatsRepoConfigs, '/stats/repository/configs', '/stats/repository/configs/<int:limit>'),
        (StatsConfigError, '/stats/configs/error', '/stats/configs/error/<int:limit>'),
        (StatsConfigLatest, '/stats/configs/latest', '/stats/configs/latest/<int:limit>'),

        (ProjectVersion, '/version'),
        (UpdateInfo, '/update'),
    ]

    @classmethod
    def run(cls, api: Api):
        for r in cls._routes:
            api.add_resource(*r)
