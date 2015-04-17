import os
import subprocess

from django.conf import settings
from django.core.management.base import BaseCommand

from django_scripts.models import Script


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        if not self.__is_django_scripts_settings_valid():
            return

        for script_name in os.listdir(settings.SCRIPTS_DIR):
            self.__run_script(script_name)

    def __run_script(self, script_name):
        if self.__is_extension_valid(script_name):
            interpreter = self.__interpreters[script_name.split('.')[-1]]
            exit_status = subprocess.call(
                [interpreter, os.path.join(settings.SCRIPTS_DIR, script_name)])
            self.__show_running_message(exit_status, script_name)
            if exit_status == 0:
                self.__save_script_as_applied(script_name)

    def __show_running_message(self, exit_status, script_name):
        if exit_status == 0:
            script = Script.objects.filter(name=script_name)
            if not script:
                self.stdout.write('{}... RAN'.format(script_name))
        else:
            self.stdout.write('{}... FAILED'.format(script_name))

    def __save_script_as_applied(self, script_name):
        if not Script.objects.filter(name=script_name):
            Script.objects.create(name=script_name)

    def __is_django_scripts_settings_valid(self):
        try:
            settings.SCRIPTS_DIR
        except:
            self.stderr.write(
                'To use django_scripts, you have to declare '
                'SCRIPTS_DIR in your settings.py')
            return False
        return True

    def __is_extension_valid(self, script_name):
        if len(script_name.split('.')) == 1:
            self.stderr.write(
                '{} does not have an explicit extension'.format(script_name))
            return False

        extension = script_name.split('.')[-1]

        if extension in self.__interpreters:
            return True

        self.stderr.write('Unknown interpreter for {}'.format(script_name))
        return False

    @property
    def __interpreters(self):
        settings_interpreters = getattr(settings, 'SCRIPTS_INTERPRETERS', None)
        default_interpreters = {'sh': 'bash', 'py': 'python'}
        return settings_interpreters or default_interpreters
