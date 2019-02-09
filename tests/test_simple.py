from unittest import TestCase
from io import StringIO

from yamlmacros import process_macros
from yamlmacros.src.yaml_provider import get_yaml_instance

from sublime_lib import ResourcePath


FIXTURES_PATH = ResourcePath('Packages/yaml_macros_engine/tests/fixtures')


class TestSyntaxes(TestCase):

    def _test_fixture(self, name):
        fixtures = FIXTURES_PATH / name

        source_text = (fixtures / 'source.yaml').read_text()
        answer_text = (fixtures / 'answer.yaml').read_text()

        result = process_macros(
            source_text,
            macros_root=str(fixtures.file_path())
        )

        out = StringIO()
        serializer = get_yaml_instance()
        serializer.dump(result, stream=out)

        result_text = out.getvalue()

        self.assertEqual(result_text, answer_text)

    def test_simple(self):
        self._test_fixture('simple')

    def test_loading(self):
        self._test_fixture('loading')

    def test_options(self):
        self._test_fixture('options')
