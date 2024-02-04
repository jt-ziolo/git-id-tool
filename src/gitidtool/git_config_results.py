from dataclasses import dataclass


@dataclass
class GitConfigResults:
    names = set()
    emails = set()
    signing_keys = set()
    unconfigured_hostnames = set()
    mismatched_email_entries = []
