import argparse
import json
import os
import sys

from detect_secrets.core.scan import scan_file
from detect_secrets.settings import transient_settings

def scan_secrets(gitingest_file_path: str, output_file: str):
    """
    Scans the gitingest file for secrets.
    """
    config = {
        'plugins_used': [
            {'name': 'AWSKeyDetector'},
            {'name': 'Base64HighEntropyString', 'limit': 3},
            {'name': 'DiscordBotTokenDetector'},
            {'name': 'GitHubTokenDetector'},
            {'name': 'HexHighEntropyString', 'limit': 3},
            {'name': 'JwtTokenDetector'},
            {'name': 'MailchimpDetector'},
            {'name': 'NpmDetector'},
            {'name': 'PrivateKeyDetector'},
            {'name': 'SendGridDetector'},
            {'name': 'SlackDetector'},
            {'name': 'StripeDetector'},
            {'name': 'TwilioKeyDetector'},
        ],
    }

    secrets = {}
    with transient_settings(config):
        for secret in scan_file(gitingest_file_path):
            if gitingest_file_path not in secrets:
                secrets[gitingest_file_path] = []
            secrets[gitingest_file_path].append(str(secret))

    with open(output_file, "w") as f:
        json.dump(secrets, f, indent=4)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("gitingest_file_path", help="The path to the gitingest file.")
    parser.add_argument("output_file", help="The path to the output file.")
    args = parser.parse_args()
    scan_secrets(args.gitingest_file_path, args.output_file)