#!/usr/bin/python
import json
import os
import jinja2
import subprocess
import service


def render(tpl_path, context):
    path, filename = os.path.split(tpl_path)
    return jinja2.Environment(
        loader=jinja2.FileSystemLoader(path or './')
    ).get_template(filename).render(context)


def run_bash(cmd, log=False):
    pwd = os.path.abspath(".")
    uid = os.getuid()
    gid = os.getgid()
    cmd = cmd.format(pwd=pwd, gid=gid, uid=uid)
    if log:
        print cmd
    process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    return output, error


def services():
    with open("./services.json", "r") as f:
        for config in json.loads(f.read()):
            yield service.Service(config)
