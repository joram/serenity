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

    def __init__(self, name, icon_url, port):
        self.name = name
        self.icon_url = icon_url
        self.port = port
        if self.active:
            download_file(icon_url, "./src/icons/{}.png".format(name).lower())
   
    @property
    def active(self):
        return self.port != ""

    @property
    def url(self):
        return "/{name}".format(name=self.name.lower())

    @property
    def nginx_location(self):
        path = "../s-{name}/nginx_config".format(name=self.name.lower())
        with open(path) as f:
            content = f.read()
        return content


def get_services():
    with open("../docker-compose.yml") as f:
        content = f.read()
        services = yaml.load(content)

    for details in services.values():
        name = ""
        icon_url = ""
        port = ""
        env = details.get("environment", [])
        for e in env:
            if "=" in e:
                k,v = e.split("=")
                if k == "SERENITY_NAME":
                    name = v
                if k == "SERENITY_ICON_URL":
                    icon_url = v
                if k == "SERENITY_PORT":
                    port = v
        yield Service(name, icon_url, port)


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
        
