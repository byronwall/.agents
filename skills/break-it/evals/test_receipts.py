import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/cheese.py"


class ReceiptTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.run_dir = Path(tmp.name)
        diagram = SCRIPT.parents[1] / "references/boundary-example.draft"
        (self.run_dir / "boundary.draft").write_bytes(diagram.read_bytes())
        self.candidate = {
            "id": "C8", "title": "Settings Apply keeps the draft", "harm": "wrong",
            "holes": [{"condition": "draft edited", "freq": "routine"}],
            "status": "held", "revision": "abc1234", "expected": "West",
            "observed": "West", "reproduce": "Run the draft probe on Settings Apply",
            "evidence": ["head.log"],
            "control": {"outcome": "failure-observed", "observed": "draft reverted to East",
                        "evidence": ["control.log"]},
        }
        (self.run_dir / "head.log").write_text("West")
        (self.run_dir / "control.log").write_text("East")

    def check(self, code, *messages, mode="finish"):
        ledger = self.run_dir / "ledger.json"
        ledger.write_text(json.dumps({"candidates": [self.candidate]}))
        proc = subprocess.run([sys.executable, SCRIPT, mode, ledger], capture_output=True, text=True)
        self.assertEqual(proc.returncode, code, proc.stdout + proc.stderr)
        for message in messages:
            self.assertIn(message, proc.stdout)
        if code:
            self.assertNotIn("evidence complete", proc.stdout)

    def test_deleted_evidence_for_either_verdict(self):
        (self.run_dir / "head.log").unlink()
        for status in ("held", "broke"):
            self.candidate.update(status=status, base="differs")
            self.check(1, "C8 evidence", "head.log")

    def test_control_receipt(self):
        self.check(0, "evidence complete")
        (self.run_dir / "control.log").unlink()
        self.check(1, "C8 control evidence", "control.log")
        self.candidate["control"] = "probe would fail"
        self.check(1, "C8", "control receipt")

    def test_import_error(self):
        (self.run_dir / "control.log").write_text("ImportError before the probe ran")
        self.candidate["control"].update(outcome="setup-error", observed="ImportError")
        self.check(1, "C8", "target failure")

    def test_break_with_successful_exit(self):
        output = subprocess.check_output([sys.executable, "-c", "print('East')"], text=True)
        (self.run_dir / "head.log").write_text(output)
        self.candidate.update(status="broke", base="differs", observed=output.strip())
        del self.candidate["control"]
        self.check(0, "evidence complete")

    def test_reasoned_gap(self):
        for status in ("untested", "inconclusive"):
            self.candidate.update(status=status, note="Apply writes shared configuration")
            self.check(0, "evidence complete", "Coverage gaps: 1", "C8", status, self.candidate["note"])
            del self.candidate["note"]
            self.check(1, "C8", "reason")

    def test_historical_status_default(self):
        del self.candidate["status"]
        self.check(0, mode="check")
        self.check(1, "C8", "missing explicit status")

    def test_required_fields(self):
        for field in ("revision", "reproduce", "expected", "observed"):
            with self.subTest(field=field):
                value = self.candidate.pop(field)
                self.check(1, "C8", field)
                self.candidate[field] = value

    def test_artifact_must_be_retained_in_run(self):
        (self.run_dir / "outside").symlink_to(SCRIPT)
        (self.run_dir / "empty").touch()
        for name in ("outside", "empty", ".", str(SCRIPT)):
            with self.subTest(name=name):
                self.candidate["evidence"] = [name]
                self.check(1, "C8 evidence", name)


if __name__ == "__main__":
    unittest.main()
