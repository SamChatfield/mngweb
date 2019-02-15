import subprocess
from celery import shared_task

@shared_task
def run_subprocess():
    # We can return a Python object which will be serialised and sent
    obj = {}
    # Note we must decode the return value of subprocess.check_output as UTF-8 string
    obj['outstr'] = subprocess.check_output(['conda', '-h']).decode('utf-8')
    return obj

@shared_task
def touch_file():
    return subprocess.call(['touch', '/home/ubuntu/CELERYTEST.txt'])

@shared_task
def mngvariants(uuid, samples, reference):
    return subprocess.call([
        'mngvariants',
        '--uuid {}'.format(uuid),
        '--samples {}'.format(' '.join(samples)),
        '--reference {}'.format(reference)
    ])
