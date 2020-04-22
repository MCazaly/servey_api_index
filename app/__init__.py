from flask import Flask, url_for
from flask_restplus import Api, Resource
from os import path
import json
import requests


name = "Servey API Index"
app = Flask(name)


class SecureApi(Api):
    @property
    def specs_url(self):
        # HTTPS monkey patch
        scheme = "http" if ":5000" in self.base_url else "https"
        return url_for(self.endpoint("specs"), _external=True, _scheme=scheme)


api = SecureApi(app, doc="/")
api.title = name

directory = path.dirname(path.abspath(__file__))
manifest_path = path.join(path.dirname(path.abspath(__file__)), "manifest.json")

if not path.isfile(manifest_path):
    with open(manifest_path, "w") as file:
        file.write("{}")
with open(manifest_path, "r") as file:
    manifest = json.load(file)


@api.route("/api/<string:key>")
class ApiIndex(Resource):
    @staticmethod
    def get(key):
        return get_api(key)


@api.route("/all")
class ApiIndexAll(Resource):
    @staticmethod
    def get():
        apis = {}
        for key in manifest:
            apis[key] = get_api(key)
        return apis


@api.route("/list")
class ApiList(Resource):
    @staticmethod
    def get():
        return list(manifest.keys())


def check_online(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
    except (requests.HTTPError, UnicodeDecodeError, requests.exceptions.ConnectionError):
        return False
    return True


def get_api(key):
    info = manifest[key]
    instance = {}
    instance.update(info)
    instance["online"] = check_online(instance["url"])
    return instance


def main():
    app.run()


if __name__ == "__main__":
    main()
