# -*- coding: utf-8 -*-
"""TEMPORARY CI probe -- deliberately fails to verify the test-failure email.

This file exists only on the throwaway branch `ci-test/failure-email` to confirm
that a failing test triggers the notification email. It must NOT be merged to
main. Delete the branch after the email is confirmed.
"""


def test_ci_failure_email_probe():
    assert False, "intentional failure to test the CI notification email"
