import os
import shutil
import subprocess
import pathlib

backend = pathlib.Path(__file__).resolve().parent
os.chdir(backend)

deploy = os.path.join(backend.parent, 'deploy')

if os.path.exists(deploy):
    shutil.rmtree(deploy)

shutil.copytree(backend, deploy)

# additional settings for django on heroku
os.chdir(deploy)
with open(os.path.join('hacknu', 'settings.py'), 'a') as f:
    f.write('import django_heroku')
    f.write(os.linesep)
    f.write('django_heroku.settings(locals())')
    f.write(os.linesep)

with open(os.path.join('requirements.txt'), 'a') as f:
    f.write('django-heroku==0.3.1')
    f.write(os.linesep)

# description files for heroku
os.chdir(deploy)

with open('Procfile', 'w') as f:
    f.write('web: gunicorn hacknu.wsgi')
    f.write(os.linesep)

with open('runtime.txt', 'w') as f:
    f.write('python-3.9.2')
    f.write(os.linesep)

# pushing to heroku
if os.path.exists('.git'):
    shutil.rmtree('.git')

subprocess.run(['git', 'init'])
subprocess.run(['git', 'checkout', '-b', 'main'])
subprocess.run(['git', 'add', '-A'])
subprocess.run(['git', 'commit',  '-m', 'Deploy'])

subprocess.run(['heroku', 'git:remote', '-a', 'unknownasd'])
subprocess.run(['git', 'push', '-f', 'heroku', 'main'])
