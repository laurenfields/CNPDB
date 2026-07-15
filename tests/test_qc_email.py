# -*- coding: utf-8 -*-
"""Tests for the database-accuracy email body builder."""
import pandas as pd

from DataCuration import qc_email


def test_body_clean_when_no_issues():
    body = qc_email.build_body(pd.DataFrame(columns=["category", "severity"]), 1516)
    assert "no flagged issues" in body


def test_body_summarizes_counts():
    issues = pd.DataFrame([
        {"category": "mass_discrepancy", "severity": "high"},
        {"category": "mass_discrepancy", "severity": "high"},
        {"category": "missing_OS", "severity": "low"},
    ])
    body = qc_email.build_body(issues, 1516)
    assert "3 flagged QC issue(s)" in body
    assert "mass_discrepancy: 2" in body
    assert "high: 2" in body
    assert "do NOT block" in body
