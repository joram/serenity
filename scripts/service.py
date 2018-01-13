import util
import os


class Service(object):

    def __init__(self, config):
        self.config = config

    @property
    def _proxy_url(self):
        if 'docker' in self.config:
            port = self.config['docker']['port']
            return "http://localhost:{port}".format(port=port)
        return self.config['proxy_url']

    @property
    def _name(self):
        return self.config['name']

    def write_nginx_config(self):
        filepath = "/etc/nginx/sites-enabled/{name}".format(name=self._name)
        with open(filepath, "w") as f:
            context = {
                "name": self._name,
                "proxy_url": self._proxy_url
            }
            content = util.render("./templates/nginx_config", context)
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
            cmd = "docker run -d --name {name} {flags} -p {port}:{port} {image_name}".format(
                image_name=self.config['docker']['image'],
                name="serenity_{name}".format(name=self._name),
                port=self.config['docker']['port'],
                flags=" ".join(self.config['docker']['flags'])
            )
            print "docker run -d --name {name} ...".format(name=self._name)
            util.run_bash(cmd)
