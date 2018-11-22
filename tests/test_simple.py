import sublime

from unittest import TestCase
from io import StringIO
import os
from os import path

from yamlmacros import process_macros
from yamlmacros.src.yaml_provider import get_yaml_instance

FIXTURES_PATH = 'yaml_macros_engine/tests/fixtures'


def load_fixture(*fixture_path):
    return sublime.load_resource(
        path.join('Packages', FIXTURES_PATH, *fixture_path)
    )


class TestSyntaxes(TestCase):

    def _test_fixture(self, name):
        os.chdir(path.join(sublime.packages_path(), FIXTURES_PATH, name))
        source_text = load_fixture(name, 'source.yaml')
        answer_text = load_fixture(name, 'answer.yaml')

        result = process_macros(source_text)

        out = StringIO()
        serializer = get_yaml_instance()
        serializer.dump(result, stream=out)

        result_text = out.getvalue()

        self.assertEqual(result_text, answer_text)

    def test_simple(self):
        self._test_fixture('simple')
