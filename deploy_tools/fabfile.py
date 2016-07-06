from fabric.contrib.files import exists, sed
from fabric.api import env, local, run, put

REPO_URL = 'https://bitbucket.org/jomaresti/mngweb'


def deploy():
    site_folder = '/home/%s/sites/%s' % (env.user, env.host)
    source_folder = site_folder + '/source'
    local_source_folder = '../source'
    _get_latest_source(site_folder)
    _create_directory_structure(site_folder)
    _update_settings(source_folder, env.host)
    _copy_local_settings(local_source_folder, source_folder)
    _update_virtualenv(site_folder)
    _update_static_files(source_folder)
    _update_database(source_folder)


def _create_directory_structure(site_folder):
    for subfolder in ('database', 'static', 'media', 'venv'):
        run('mkdir -p %s/%s' % (site_folder, subfolder))


def _get_latest_source(site_folder):
    run('mkdir -p %s' % (site_folder,))
    if exists(site_folder + '/.git'):
        run('cd %s && git fetch' % (site_folder,))
    else:
        run('git clone %s %s' % (REPO_URL, site_folder))
    current_commit = local("git log -n 1 --format=%H", capture=True)
    run('cd %s && git reset --hard %s' % (site_folder, current_commit))


def _update_settings(source_folder, site_name):
    settings_path = source_folder + '/mngweb/settings/'
    sed(settings_path + '__init__.py', ".dev", ".production")


def _update_virtualenv(site_folder):
    virtualenv_folder = site_folder + '/venv'
    if not exists(virtualenv_folder + '/bin/pip'):
        run('virtualenv --python=python3 %s' % (virtualenv_folder,))
    run('%s/bin/pip install -r %s/requirements/production.txt' % (
        virtualenv_folder, site_folder
    ))


def _copy_local_settings(local_source_folder, source_folder):
    put(local_source_folder + '/mngweb/settings/local.py',
        source_folder + '/mngweb/settings/local.py')


def _update_static_files(source_folder):
    run('cd %s && ../venv/bin/python3 manage.py collectstatic --noinput' % (
        source_folder,
    ))


def _update_database(source_folder):
    run('cd %s && ../venv/bin/python3 manage.py migrate --noinput' % (
        source_folder,
    ))
