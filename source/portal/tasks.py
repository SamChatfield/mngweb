import subprocess
from celery import shared_task


@shared_task
def mngvariants(uuid, samples, reference):
    cmd = [
        'mngvariants',
        '--uuid',
        '{}'.format(uuid),
        '--samples'
    ] + samples + [
        '--reference',
        '{}'.format(reference)
    ]
    return subprocess.check_output(cmd).decode('utf-8')
