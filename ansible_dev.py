import click
from action import Action
import traceback
from colorama import Fore, Back, Style

class Config(object):
    def __init__(self):
        self.verbose = False
        self.action_plugin = None

pass_config = click.make_pass_decorator(Config)

@click.group()
@click.option('--verbose', '-v', count=True, help='Enables verbose mode')
@click.option('--debug', '-d', is_flag=True, help='Enables debug mode')
@click.pass_context
def cli(ctx, verbose, debug):
    """ansible-dev is a command line tool for getting started with
    ansible.
    It does all prerequisite for running ansible and starts
    initial template for plalybook and roles
    """
    ctx.obj = Config()
    ctx.obj.verbose = verbose
    ctx.obj.debug = debug
    ctx.obj.action_plugin = Action(verbose)

@cli.command()
@click.option('--venv-name', default='.venv',
              type=click.STRING, help='Name to create virtualenv')
@click.option('--ansible-version', default='devel',
              type=click.STRING, help='ansible version to checkout')
@click.option('--ansible-repo', default='https://github.com/ansible/ansible.git',
              type=click.STRING, help='ansible version to checkout')
@click.argument('path', type=click.Path())
@pass_config
def init(config, path, venv_name, ansible_version, ansible_repo):
    """
    Initialize the environment for ansible in a given directory path
    
    Usage: ansible-dev init <path>
    """
    if not path:
        click.echo("Usage: ansible-dev init <path>")
        return

    click.echo('Start: Init at %s ' % path, color=Fore.GREEN)
    
    if config.verbose > 1:
        click.echo("Init args: path=%s, venv_name=%s" % (path, venv_name))
        click.echo("Init args type: path=%s, venv_name=%s" %
                  (type(path), type(venv_name)))

    try:
        click.echo("Step 1/6: create workspace directory")
        config.action_plugin.create_directory(path)
        click.echo("Step 2/6: create Virtual Environment")
        venv_path = config.action_plugin.create_venv(app_name=venv_name)
        click.echo("Step 3/6: clone ansible git repo")
        ansible_path = config.action_plugin.clone_git_repo(
            ansible_repo, ansible_version)
        click.echo("Step 4/6: Install ansible Dependencies in virtial env")
        config.action_plugin.install_repo_dependancies_in_venv(ansible_path)
        click.echo("Step 5/6: Install ansible in virtual-env")
        config.action_plugin.activate_ansible_in_venv(ansible_path)
        click.echo("Step 6/6: Checking ansible installation in virtial env")
        out = config.action_plugin.print_ansible_version(ansible_path)
        click.echo(out)
        click.echo("Init Success: Ansible virtual env is ready at : %s" % venv_path)
    except Exception as e:
        print ("Failed : Exception %s" % e)
        if config.debug:
            traceback.print_exc()
        return
