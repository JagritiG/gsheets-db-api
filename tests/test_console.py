# -*- coding: utf-8 -*-

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

import unittest

import requests_mock
from six import StringIO

from .context import console, exceptions


class ConsoleTestSuite(unittest.TestCase):

    @patch('gsheetsdb.console.docopt')
    @patch('sys.stdout', new_callable=StringIO)
    @patch('gsheetsdb.console.prompt')
    def test_main(self, prompt, stdout, docopt):
        docopt.return_value = {
            '--headers': '0',
            '--raise': False,
            '--service-account-file': None,
            '--subject': None,
        }
        prompt.side_effect = EOFError()
        console.main()
        self.assertEqual(stdout.getvalue(), 'See ya!\n')

    @patch('gsheetsdb.console.docopt')
    @requests_mock.Mocker()
    @patch('sys.stdout', new_callable=StringIO)
    @patch('gsheetsdb.console.prompt')
    def test_main_query(self, m, prompt, stdout, docopt):
        docopt.return_value = {
            '--headers': '0',
            '--raise': False,
            '--service-account-file': None,
            '--subject': None,
        }
        header_payload = {
            'table': {
                'cols': [
                    {'id': 'A', 'label': 'country', 'type': 'string'},
                    {
                        'id': 'B',
                        'label': 'cnt',
                        'type': 'number',
                        'pattern': 'General',
                    },
                ],
            },
        }
        query_payload = {
            'status': 'ok',
            'table': {
                'cols': [
                    {'id': 'A', 'label': 'country', 'type': 'string'},
                    {
                        'id': 'B',
                        'label': 'cnt',
                        'type': 'number',
                        'pattern': 'General',
                    },
                ],
                'rows': [
                    {'c': [{'v': 'BR'}, {'v': 1.0, 'f': '1'}]},
                    {'c': [{'v': 'IN'}, {'v': 2.0, 'f': '2'}]},
                ],
            },
        }
        m.get(
            'http://docs.google.com/gviz/tq?gid=0&tq=SELECT%20%2A%20LIMIT%200',
            json=header_payload,
        )
        m.get(
            'http://docs.google.com/gviz/tq?gid=0&tq=SELECT%20%2A',
            json=query_payload,
        )

        def gen():
            yield 'SELECT * FROM "http://docs.google.com/"'
            raise EOFError()

        prompt.side_effect = gen()
        console.main()
        result = stdout.getvalue()
        expected = (
            'country      cnt\n'
            '---------  -----\n'
            'BR             1\n'
            'IN             2\n'
            'See ya!\n'
        )
        self.assertEqual(result, expected)

    @patch('gsheetsdb.console.docopt')
    @patch('sys.stdout', new_callable=StringIO)
    @patch('gsheetsdb.console.prompt')
    def test_console_exception(self, prompt, stdout, docopt):
        docopt.return_value = {
            '--headers': '0',
            '--raise': False,
            '--service-account-file': None,
            '--subject': None,
        }

        def gen():
            yield 'SELECTSELECTSELECT'
            raise EOFError()

        prompt.side_effect = gen()
        console.main()
        result = stdout.getvalue()
        expected = (
            'Invalid query: SELECTSELECTSELECT\n'
            'See ya!\n'
        )
        self.assertEqual(result, expected)

    @patch('gsheetsdb.console.docopt')
    @patch('sys.stdout', new_callable=StringIO)
    @patch('gsheetsdb.console.prompt')
    def test_console_raise_exception(self, prompt, stdout, docopt):
        docopt.return_value = {
            '--headers': '0',
            '--raise': True,
            '--service-account-file': None,
            '--subject': None,
        }

        def gen():
            yield 'SELECTSELECTSELECT'
            raise EOFError()

        prompt.side_effect = gen()
        with self.assertRaises(exceptions.ProgrammingError):
            console.main()
