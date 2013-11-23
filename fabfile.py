import sys
from fabric.context_managers import prefix
from fabric.decorators import task
from fabric.operations import local
from test.features.driver.server_driver import ServerDriver

VIRTUALENV = '.venv'


@task(default=True)
def default():
    test()


@task
def setup():
    local('virtualenv --distribute --python=python2.7 {env}'.format(env=VIRTUALENV))
    install_requirements()


@task
def install_requirements():
    with prefix(_activate_virtual_env()):
        local('pip install -r requirements.txt --use-mirrors')
        local('pip install -r requirements-test.txt --use-mirrors')


@task
def unit():
    with prefix(_activate_virtual_env()):
        local("nosetests -a '!needs_server'")


@task
def test():
    with prefix(_activate_virtual_env()), YoseServer(port=8080):
        local("nosetests --tc=server_url:'http://localhost:8080'")


@task
def run_server():
    with prefix(_activate_virtual_env()):
        local("python -c 'import yose; yose.app.run(port=8080)'")


def _activate_virtual_env():
    if not hasattr(sys, 'real_prefix'):
        return '. {env}/bin/activate'.format(env=VIRTUALENV)
    else:
        return 'true'


class YoseServer():
    def __init__(self, port=8080):
        self.port = port
        self.server = ServerDriver(name='Yose', port=self.port)

    def __enter__(self):
        self.server.start(cmd=['gunicorn', 'yose:app', '-w', '1', '-b', '0.0.0.0:{0}'.format(self.port)])
        return self.server

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.server.shutdown()