#!/usr/bin/env python
import requests
import yaml
import os
import jinja2


def render(tpl_path, context):
    path, filename = os.path.split(tpl_path)
    return jinja2.Environment(
        loader=jinja2.FileSystemLoader(path or './')
    ).get_template(filename).render(context)


class Service(object):

    def __init__(self, data, service_name):
        print service_name
        self._service_name = service_name
        self._data = data
        self._env = {}
        for env in data.get("environment", []):
            k,v = env.split("=", 1)
            self._env[k] = v
        if self.icon_url:
            download_file(self.icon_url, "./src/icons/{}.png".format(self.name).lower())

    @property
    def name(self):
        n = self._env.get("VIRTUAL_HOST", ".").split(".")[0]
        if n is "" or n is None:
            return self._service_name.replace("s-", "")
        return n
    
    @property
    def description(self):
        return self._env.get("DESCRIPTION", "")
    
    @property
    def icon_url(self):
        return self._env.get("ICON_URL")
    
    @property
    def active(self):
        return self.url is not None

    @property
    def url(self):
        return self._env.get("VIRTUAL_HOST")

    @property
    def nginx_location(self):
        path = "../s-{name}/nginx_config".format(name=self.name.lower())
        with open(path) as f:
            content = f.read()
        return content


def get_services():
    with open("../docker-compose.yml") as f:
        content = f.read()
        compose = yaml.load(content)
        for n in compose.get("services"):
            data = compose.get("services").get(n)
            yield Service(data, n)


def download_file(url, path):
    if os.path.exists(path):
        return
    print("downloading {} to {}".format(url, path))
    r = requests.get(url, allow_redirects=True)
    open(path, 'wb').write(r.content)


def build_index(services):
    context = {"services": services}
    content = render("./templates/index.html", context)
    with open("./src/index.html", "w") as f:
        f.write(content)

if __name__ == "__main__":
    services = list(get_services())
    build_index(services)
        
