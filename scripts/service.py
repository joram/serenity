import util
import os


class Service(object):

    def __init__(self, config):
        self.config = config


    @property
    def _ports(self):
        ports = []
        port = self.config['docker'].get('port')
        if port is not None:
            ports = [port]
        ports += self.config['docker'].get('ports', [])
        return ports

    def proxy_url(self, port):
        if 'docker' in self.config:
            protocol = self.config["docker"].get("protocol", "http")
            return "{protocol}://localhost:{port}".format(port=port, protocol=protocol)
        return self.config['proxy_url']

    @property
    def _name(self):
        return self.config['name']

    @property
    def _nginx_context(self):
        port = self.config['docker'].get('port')
        return {
            "name": self._name,
            "url": self.proxy_url(port),
        }

    def write_nginx_config(self):
        if "proxy_url" in self.config:
            return
        filepath = "/etc/nginx/sites-enabled/{name}".format(name=self._name)
        with open(filepath, "w") as f:
            content = util.render("./templates/nginx_config", self._nginx_context)
            f.write(content)

    def get_image(self):
        if 'docker' in self.config:
            cmd = "docker pull {image_name}".format(image_name=self.config['docker']['image'])
            util.run_bash(cmd)

    def stop(self):
        if 'docker' in self.config:
            output, error = util.run_bash("docker ps")
            image_name ="serenity_{name}".format(name=self._name)
            if image_name in output:
                util.run_bash("docker stop {name}".format(name=image_name))
            util.run_bash("docker rm {name}".format(name=image_name))

    def ensure_data_dirs(self):
        base_dir = "./data/{}".format(self._name)
        data_dirs = [base_dir]
        for folder in self.config["docker"].get("dirs", []):
            data_dirs.append(os.path.join(base_dir, folder))

        for data_dir in data_dirs:
            if not os.path.exists(data_dir):
                os.makedirs(data_dir)

    def run(self):
        if 'docker' in self.config:
            self.stop()
            self.ensure_data_dirs()
            flags = self.config['docker']['flags']
            flags += ["-p {port}:{port}".format(port=p) for p in self._ports]
            cmd = "docker run -d --name {name} {flags} {image_name}".format(
                image_name=self.config['docker']['image'],
                name="serenity_{name}".format(name=self._name),
                flags=" ".join(flags)
            )
            util.run_bash(cmd)

class HomeService(Service):

    def __init__(self):
        self.config = {}

    @property
    def _name(self):
        return "home"

    @property
    def _nginx_context(self):
        return {"url": "http://127.0.0.1:8085", "name": ""}

