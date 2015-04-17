import os
import random
import sys

if sys.version_info[0] >= 3:
    from string import (
        ascii_lowercase as lowercase, ascii_uppercase as uppercase)
else:
    from string import lowercase, uppercase

from django.conf import settings
from django.core import management
from django.test import TestCase, override_settings
from django.utils.six import StringIO

from django_scripts.models import Script


def generate_script_file(extension='.sh', script_content=None):
    script_name = '{}{}'.format(''.join(
        random.choice(
            uppercase + lowercase) for _ in range(10)),
        extension)

    with open(os.path.join(settings.SCRIPTS_DIR, script_name), 'w') as f:
        if script_content:
            f.write(script_content)

    return script_name


def create_scripts_dir(base_dir=None):
    directory_path = os.path.join(base_dir or settings.BASE_DIR, 'scripts')
    try:
        os.mkdir(directory_path)
    except:
        pass


def delete_scripts(scripts_dir=settings.SCRIPTS_DIR):
    for script in os.listdir(scripts_dir):
        script_path = os.path.join(scripts_dir, script)
        try:
            if os.path.isfile(script_path):
                os.unlink(script_path)
        except Exception:
            pass


class ScriptsTest(TestCase):
    def setUp(self):
        self.stdout = StringIO()
        self.stderr = StringIO()

    def tearDown(self):
        delete_scripts()

    def test_run_script(self):
        script_name = generate_script_file()
        management.call_command('runscripts', stdout=self.stdout)
        self.assertEqual(
            1,
            Script.objects.filter(name=script_name).count())

    def test_check_sucess_message(self):
        script_name = generate_script_file()
        management.call_command('runscripts', stdout=self.stdout)
        self.assertIn('{}... RAN'.format(script_name), self.stdout.getvalue())

    def test_script_cant_run_twice(self):
        script_name = generate_script_file()
        management.call_command('runscripts', stdout=self.stdout)
        self.assertEqual(
            1,
            Script.objects.filter(name=script_name).count())
        management.call_command('runscripts', stdout=self.stdout)
        self.assertEqual(
            1,
            Script.objects.filter(name=script_name).count())

    def test_dont_show_message_when_the_script_doesnt_run(self):
        script_name = generate_script_file()
        management.call_command('runscripts', stdout=self.stdout)
        self.assertIn('{}... RAN'.format(script_name), self.stdout.getvalue())

        self.stdout = StringIO()
        management.call_command('runscripts', stdout=self.stdout)
        self.assertEqual('', self.stdout.getvalue())

    def test_dont_mark_as_applied_when_script_fails(self):
        script_content = 'exit 1'
        generate_script_file(script_content=script_content)
        management.call_command('runscripts', stdout=self.stdout)
        self.assertEqual(0, Script.objects.count())

    def test_check_fail_message(self):
        script_content = 'exit 1'
        script_name = generate_script_file(script_content=script_content)
        management.call_command('runscripts', stdout=self.stdout)
        self.assertEqual(0, Script.objects.count())
        self.assertIn('{}... FAILED'.format(script_name), self.stdout.getvalue())

    def test_unknown_extensions_should_be_warned(self):
        script_name = generate_script_file(extension='.rb')
        management.call_command(
            'runscripts',
            stdout=self.stdout,
            stderr=self.stderr)
        self.assertIn(
            'Unknown interpreter for {}'.format(script_name),
            self.stderr.getvalue())

    def test_show_warning_when_script_doesnt_have_extension(self):
        script_name = generate_script_file(extension='')
        management.call_command(
            'runscripts',
            stdout=self.stdout,
            stderr=self.stderr)
        self.assertIn(
            '{} does not have an explicit extension'.format(script_name),
            self.stderr.getvalue())
        self.assertEqual(0, Script.objects.count())

    @override_settings(SCRIPTS_INTERPRETERS={'pl': 'perl'})
    def test_use_interpreters_from_settings(self):
        generate_script_file(extension='.pl')
        management.call_command('runscripts', stdout=self.stdout)
        self.assertEqual(1, Script.objects.count())

    def test_use_correct_interpreter(self):
        content_python_script = 'import string'
        generate_script_file(
            extension='.py', script_content=content_python_script)
        content_shell_script = 'echo "django_scripts" > /dev/null'
        generate_script_file(
            script_content=content_shell_script)
        management.call_command('runscripts', stdout=self.stdout)
        self.assertEqual(2, Script.objects.count())
