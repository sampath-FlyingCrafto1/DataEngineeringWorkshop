import os
import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from click.testing import CliRunner
from ingest_data import run

class TestIngestData(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()
        self.data_dir = 'test_data'
        os.makedirs(self.data_dir, exist_ok=True)

        # Create a dummy CSV
        self.csv_path = os.path.join(self.data_dir, 'test.csv')
        df = pd.DataFrame({'a': [1, 2], 'b': [3, 4]})
        df.to_csv(self.csv_path, index=False)

    def tearDown(self):
        if os.path.exists(self.csv_path):
            os.remove(self.csv_path)
        if os.path.exists(self.data_dir):
            os.rmdir(self.data_dir)

    @patch('ingest_data.create_engine')
    @patch('pandas.read_csv')
    def test_run_success(self, mock_read_csv, mock_create_engine):
        # Setup mocks
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine

        # Mocking the iterator behavior of pd.read_csv(..., iterator=True)
        # It needs to return an iterable of DataFrames
        df_chunk = pd.DataFrame({'a': [1], 'b': [3]})
        mock_read_csv.return_value = [df_chunk]

        result = self.runner.invoke(run, [
            '--data-dir', self.data_dir,
            '--pg-user', 'user',
            '--pg-pass', 'pass',
            '--pg-host', 'host',
            '--pg-port', '5432',
            '--pg-db', 'db'
        ])

        # Assertions
        self.assertEqual(result.exit_code, 0)
        self.assertIn('Successfully ingested test.csv into test', result.output)

        # Verify engine creation
        mock_create_engine.assert_called_once_with('postgresql://user:pass@host:5432/db')

        # Verify read_csv call
        mock_read_csv.assert_called_once()

        # Check if to_sql was called. Since we can't easily mock the df returned from the list
        # without more complex mocking, we can just check if the output says it was successful.
        # Alternatively, we could mock the DataFrame class itself.

if __name__ == '__main__':
    unittest.main()
