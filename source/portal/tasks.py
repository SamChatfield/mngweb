import subprocess
from celery import shared_task

@shared_task
def run_subprocess():
    return subprocess.call(['conda', '-h'])

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
