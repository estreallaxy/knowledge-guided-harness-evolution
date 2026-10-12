"""Load native service settings and secrets into a child environment only."""
import argparse
import os
import re
import subprocess
from pathlib import Path
from dotenv import dotenv_values


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--service', default='bailian-personal')
    parser.add_argument('command', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    if not re.fullmatch(r'[a-z0-9-]+', args.service):
        parser.error('Invalid service name')
    command = args.command[1:] if args.command[:1] == ['--'] else args.command
    if not command:
        parser.error('A child command is required')
    secret = Path.home() / '.secrets' / (args.service + '.env')
    settings = Path.home() / '.config/credential-services' / (args.service + '.env')
    if not secret.is_file() or secret.stat().st_mode & 0o077 or not settings.is_file():
        parser.error('Missing service files or unsafe secret file permissions')
    configuration = dict(dotenv_values(settings, interpolate=False))
    credentials = dict(dotenv_values(secret, interpolate=False))
    if configuration.keys() & credentials.keys():
        parser.error('Duplicated variables in settings and secrets')
    merged = {**configuration, **credentials}
    keys = ('BAILIAN_API_KEY', 'BAILIAN_OPENAI_COMPATIBLE')
    if not all(merged.get(key) for key in keys):
        parser.error('Service is missing a required credential/endpoint variable')
    env = dict(os.environ)
    env.update({key: merged[key] for key in keys})
    return subprocess.call(command, env=env)


if __name__ == '__main__':
    raise SystemExit(main())
