#!/usr/bin/env python
import yaml


def get_services():
    with open("docker-compose.yml") as f:
        content = f.read()
        services = yaml.load(content)

    data = []
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
        data.append((name, icon_url, port))
    return data


def build_index():
    context = {}
    with open("services.json", "r") as f:
        services = json.loads(f.read())
        for i in range(0, len(services)):
            if "proxy_url" in services[i]:
                url = services[i].get("proxy_url")
                services[i]['url'] = url
                continue
            url = "http://{name}.serenity.oram.ca".format(name=services[i].get("name", "unknown"))
            services[i]['url'] = url
        context["services"] = services

    content = util.render("templates/index.html", context)
    with open("./home/src/index.html", "w") as f:
        f.write(content)

    util.run_bash("docker stop serenity_index")
    util.run_bash("docker rm -f serenity_index")
    util.run_bash("docker build -t serenity_index ./home/")
    util.run_bash("docker run --name=serenity_index -p 8085:80 -d serenity_index")


if __name__ == "__main__":
    for name, icon, port in get_services():
        print name, icon, port
