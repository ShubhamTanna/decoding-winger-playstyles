"""Integration checks: isolated builds, source immutability and semantic corruptions."""
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch
import pandas as pd
from portfolio_contract import ROOT, FILES, SOURCES, digest, load_sources, validate_sources
from export_portfolio import build, write_csv
from validate_portfolio import validate


class PortfolioTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix="portfolio-tests-", dir=ROOT/".local")
        cls.root = Path(cls.temp.name)
        cls.data = ROOT/"data/processed"
        cls.before = {str(p): digest(p) for p in (ROOT/"data").rglob('*') if p.is_file()}
        cls.first, cls.second = cls.root/"first", cls.root/"second"
        build(cls.first, cls.data, allow_dirty=True)
        build(cls.second, cls.data, allow_dirty=True)

    @classmethod
    def tearDownClass(cls):
        after = {str(p): digest(p) for p in (ROOT/"data").rglob('*') if p.is_file()}
        if cls.before != after:
            raise AssertionError("Research inputs changed during tests")
        cls.temp.cleanup()

    def test_deterministic_bytes(self):
        self.assertEqual({p.name for p in self.first.iterdir()}, FILES)
        for name in FILES:
            self.assertEqual((self.first/name).read_bytes(), (self.second/name).read_bytes(), name)

    def test_roundtrip_all_values(self):
        report = validate(self.first, self.data, allow_dirty=True)
        self.assertTrue(report['exact_source_value_roundtrip'])
        self.assertEqual(report['counts']['comparison_cases'], 10)

    def test_refuses_overwrite(self):
        with self.assertRaisesRegex(ValueError, 'already exists'):
            build(self.first, self.data, allow_dirty=True)

    def test_missing_input(self):
        with self.assertRaisesRegex(FileNotFoundError, 'Required analytical input missing'):
            load_sources(self.root/"missing")

    def test_missing_output(self):
        target = self.root/"missing-output"
        shutil.copytree(self.first, target)
        (target/'facts.md').unlink()
        with self.assertRaisesRegex(ValueError, 'eight contract files'):
            validate(target, self.data, allow_dirty=True)

    def test_source_row_order(self):
        d = load_sources(self.data)
        d['scaled'] = d['scaled'].iloc[::-1].reset_index(drop=True)
        with self.assertRaisesRegex(ValueError, 'Ordered identity mismatch'):
            validate_sources(d)

    def test_source_feature_order(self):
        d = load_sources(self.data)
        cols = d['scaled'].columns.tolist()
        cols[-1], cols[-2] = cols[-2], cols[-1]
        d['scaled'] = d['scaled'][cols]
        with self.assertRaisesRegex(ValueError, 'Matrix order mismatch'):
            validate_sources(d)

    def test_semantic_corruptions_even_with_updated_checksums(self):
        def change(frame, col, value):
            frame.loc[0, col] = value
        scenarios = [
            ('distance', 'neighbours.csv', lambda x: change(x, 'distance', x.loc[0, 'distance']+0.01)),
            ('same_player', 'neighbours.csv', lambda x: change(x, 'candidate_spell_id', x.loc[0, 'target_spell_id'])),
            ('rank', 'neighbours.csv', lambda x: change(x, 'rank', 2)),
            ('unknown_id', 'fingerprint.csv', lambda x: change(x, 'spell_id', 'spell_invalid')),
            ('percentile', 'fingerprint.csv', lambda x: change(x, 'population_percentile', x.loc[0, 'population_percentile']+1)),
            ('pca', 'spells.csv', lambda x: change(x, 'PC1', x.loc[0, 'PC1']+0.01)),
            ('duplicate', 'spells.csv', lambda x: change(x, 'spell_id', x.loc[1, 'spell_id'])),
            ('centroid', 'archetypes.csv', lambda x: change(x, 'shots_p90', x.loc[0, 'shots_p90']+0.01)),
            ('schema', 'features.csv', lambda x: x.rename(columns={'formula':'incorrect'}, inplace=True)),
            ('acceptance', 'acceptance.csv', lambda x: change(x, 'expected', '999')),
        ]
        for label, name, mutate in scenarios:
            with self.subTest(label=label):
                target = self.root/label
                shutil.copytree(self.first, target)
                frame = pd.read_csv(target/name, float_precision='round_trip', keep_default_na=False)
                mutate(frame)
                write_csv(target/name, frame)
                manifest_path = target/'manifest.json'
                manifest = json.loads(manifest_path.read_text())
                manifest['files'][name]['sha256'] = digest(target/name)
                manifest['files'][name]['bytes'] = (target/name).stat().st_size
                manifest_path.write_text(json.dumps(manifest))
                with self.assertRaises(ValueError):
                    validate(target, self.data, allow_dirty=True)

    def test_failed_validation_does_not_publish(self):
        target = self.root/'should-not-exist'
        with patch('export_portfolio.validate', side_effect=ValueError('deliberate failure')):
            with self.assertRaisesRegex(ValueError, 'deliberate failure'):
                build(target, self.data, allow_dirty=True)
        self.assertFalse(target.exists())
        self.assertEqual(list(self.root.glob('.web-build-*')), [])


if __name__ == '__main__':
    unittest.main(verbosity=2)
