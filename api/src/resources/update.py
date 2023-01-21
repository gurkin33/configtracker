import requests
from flask_restful import Resource

from api.src import access_checker
from api import __version__


class UpdateInfo(Resource):

    """"
    Get update info
    """

    @classmethod
    @access_checker(['all'], True)
    def get(cls):
        output = {"error": True, "messages": [], "data": {
            "latest_version": "",
            "release_date": ""
        }}
        try:
            result = requests.get(
                url="https://hub.docker.com/v2/repositories/gurkin33/configtracker/tags/?page_size=2&page=1",
                timeout=15, verify=False)
        except Exception as e:
            output["messages"].append(str(e))
            return output
        if result.status_code != 200:
            return output
        else:
            try:
                output["data"]["latest_version"] = result.json()["results"][1]["name"]
                output["data"]["release_date"] = result.json()["results"][1]["last_updated"]
            except Exception as e:
                output["messages"].append(str(e))
                return output
            output["error"] = False
            return output
