from flask import request
from flask_restful import Resource
from respect_validation import Validator as v, FormValidator

from api.src import access_checker
from api.src.models import ConfigModel, ConfigBinModel, CommitNotesModel


class ConfigGitLog(Resource):

    """"
    Config git log resource
    """

    @classmethod
    @access_checker(['manager'], True)
    def post(cls, config_id: str = ''):
        to_bin = request.path.startswith('/api/bin/')
        if not config_id:
            return {"error": ["Config ID must be present!"]}, 400
        if to_bin:
            config = ConfigBinModel.find_by_id(_id=config_id)
        else:
            config = ConfigModel.find_by_id(_id=config_id)
        if not config:
            return {"error": ["Config with this ID not found"]}, 404
        if not to_bin and not config.is_exists():
            return {"error": ["Config file does not exist yet. Please try to run tracker engine and check "
                              "if it appears else try to test config"]}, 404

        log_filters = request.get_json()

        rules = {
            'last_n': v.intType().min(0),
            'before': v.Optional(v.stringType().dateTime()),
            'after': v.Optional(v.stringType().dateTime()),
        }
        fv = FormValidator()
        fv.validate(log_filters, rules)
        if fv.failed():
            return {'validation': fv.get_messages()}, 400

        last_n = log_filters.get('last_n', 10)
        after = log_filters.get('after', None)
        before = log_filters.get('before', None)

        log = config.get_git_log(last_n, after, before)
        if len(log) == 0:
            return {"error": ["No commits found"]}, 404

        return log


class ConfigGitDiff(Resource):

    """"
    Config git diff resource
    """

    @classmethod
    @access_checker(['manager'], True)
    def post(cls, config_id: str = ''):
        to_bin = request.path.startswith('/api/bin/')
        if not config_id:
            return {"error": ["Config ID must be present!"]}, 400
        if to_bin:
            config = ConfigBinModel.find_by_id(_id=config_id)
        else:
            config = ConfigModel.find_by_id(_id=config_id)
        if not config:
            return {"error": ["Config with this ID not found"]}, 404
        if not to_bin and not config.is_exists():
            return {"error": ["Config file does not exist yet. Please try to run tracker engine and check"
                              " if it appear else try to test config"]}, 404

        diff_options_json = request.get_json()

        context = diff_options_json['context_lines'] if diff_options_json.get('context_lines', None) else 4

        commit_a = diff_options_json['commit_a']
        if diff_options_json.get('commit_b', None) is None:
            commit_b = diff_options_json['commit_a']
            commit_a = f"{diff_options_json['commit_a']}~"
        else:
            commit_b = diff_options_json['commit_b']
        diff = config.get_git_diff(commit_a, commit_b, context=context)
        notes = CommitNotesModel.find_(config_id, diff_options_json['commit_a'], bin_=to_bin)
        return {
            "diff": diff,
            # "data": config.get_data(diff_options_json['commit_a']),
            "notes": notes.get() if notes else None
        }
