#!/usr/bin/env python3
"""Commit only named, checked TIL files and verify a normal push to the configured branch."""
import argparse
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from urllib.parse import unquote, urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parent))
from blog import lint, tokens_of


class SyncError(RuntimeError):
    pass


def git(root, *args, env=None, check=True):
    settings = os.environ.copy()
    # An inherited alternate index/worktree must not change which repository is published.
    for key in ('GIT_INDEX_FILE', 'GIT_DIR', 'GIT_WORK_TREE', 'GIT_COMMON_DIR'):
        settings.pop(key, None)
    settings.update({'GIT_TERMINAL_PROMPT': '0', 'GIT_LITERAL_PATHSPECS': '1'})
    settings.update(env or {})
    result = subprocess.run(['git', '-C', str(root), *args], env=settings,
                            capture_output=True, text=True, timeout=60)
    if check and result.returncode:
        raise SyncError(result.stderr.strip() or result.stdout.strip() or 'Git command failed')
    return result


def out(root, *args, **kwargs):
    return git(root, *args, **kwargs).stdout.strip()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    tmp = path.with_suffix('.tmp')
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
    tmp.replace(path)


def validate_target(root, settings):
    branch = settings['branch']
    remote = settings['remote']
    if branch.startswith('-') or remote.startswith('-'):
        raise SyncError('Invalid branch or remote')
    git(root, 'check-ref-format', 'refs/heads/' + branch)
    if out(root, 'symbolic-ref', '--quiet', '--short', 'HEAD') != branch:
        raise SyncError('Checked-out branch differs from configured TIL branch')
    for push in (False, True):
        args = ('remote', 'get-url', *(['--push'] if push else []), '--all', remote)
        if out(root, *args).splitlines() != [settings['expected_url']]:
            raise SyncError('Remote destination differs from the configured URL')


def setup(config_file):
    cfg_path = Path(config_file).resolve()
    cfg = json.loads(cfg_path.read_text())
    settings = cfg.get('git_sync', {})
    if settings.get('enabled') is not True:
        raise SyncError('git_sync.enabled is not true')
    root = (cfg_path.parent / cfg['notes_root']).resolve()
    if Path(out(root, 'rev-parse', '--show-toplevel')).resolve() != root:
        raise SyncError('notes_root must be the repository root')
    validate_target(root, settings)
    for marker in ('MERGE_HEAD', 'CHERRY_PICK_HEAD', 'REVERT_HEAD', 'rebase-merge', 'rebase-apply'):
        path = Path(out(root, 'rev-parse', '--git-path', marker))
        if not path.is_absolute(): path = root / path
        if path.exists(): raise SyncError('Finish the existing Git operation before syncing')
    if out(root, 'ls-files', '--unmerged'):
        raise SyncError('Unresolved merge entries exist')
    common = Path(out(root, 'rev-parse', '--git-common-dir'))
    if not common.is_absolute(): common = root / common
    return root, settings, common.resolve() / 'til-sync'


def remote_tip(root, settings):
    lines = out(root, 'ls-remote', '--heads', settings['remote'], 'refs/heads/' + settings['branch']).splitlines()
    if len(lines) != 1 or lines[0].split()[1] != 'refs/heads/' + settings['branch']:
        raise SyncError('Expected remote branch is missing or ambiguous')
    return lines[0].split()[0]


def relative(root, name):
    path = Path(name)
    if path.is_absolute() or '..' in path.parts or not path.parts:
        raise SyncError('Provide explicit repository-relative file paths')
    full = root / path
    if full.is_symlink() or full.resolve() != full.absolute() or not full.is_file():
        raise SyncError('Only existing regular files inside the repository can be synced: ' + name)
    return path.as_posix()


def inspect_files(root, names):
    files = list(dict.fromkeys(relative(root, name) for name in names))
    if not files: raise SyncError('Name the completed TIL files; automatic whole-repository staging is disabled')
    notes, assets = [], []
    for name in files:
        path = Path(name)
        if len(path.parts) == 1 and path.suffix.lower() == '.md':
            notes.append(name)
        elif path.parts[0] in ('img', 'images') and path.suffix.lower() in ('.png', '.jpg', '.jpeg', '.webp', '.gif', '.svg'):
            assets.append(name)
        else:
            raise SyncError('Outside the TIL note/image scope: ' + name)
        if git(root, 'check-ignore', '--quiet', '--', name, check=False).returncode == 0:
            raise SyncError('Ignored file cannot be synced: ' + name)
        if out(root, 'diff', '--cached', '--name-only', '--', name):
            raise SyncError('Selected file already has staged work; preserve or finish it first: ' + name)
    if not notes: raise SyncError('At least one TIL Markdown note is required')
    referenced = set()
    warnings = []
    for name in notes:
        text = (root / name).read_text()
        report = lint(text)
        if report['errors']: raise SyncError(name + ': ' + '; '.join(report['errors']))
        if re.search(r'/Users/|file://|-----BEGIN (?:RSA |OPENSSH )?PRIVATE KEY-----', text):
            raise SyncError('Remove a local private path or private key from the public note: ' + name)
        warnings.extend(report['warnings'])
        _, children = tokens_of(text)
        for token in children:
            if token.type not in ('image', 'link_open'): continue
            href = token.attrGet('src' if token.type == 'image' else 'href') or ''
            parsed = urlsplit(href)
            if parsed.scheme or parsed.netloc or not parsed.path: continue
            target = relative(root, (Path(name).parent / unquote(parsed.path)).as_posix())
            referenced.add(target)
            tracked = git(root, 'cat-file', '-e', 'HEAD:' + target, check=False).returncode == 0
            if target not in files and (not tracked or out(root, 'diff', 'HEAD', '--', target)):
                raise SyncError('A linked local file also needs to be selected: ' + target)
    if set(assets) - referenced:
        raise SyncError('Selected image is not referenced by a selected note')
    return files, {name: sha(root / name) for name in files}, warnings


def plan(config_file, names):
    root, settings, state = setup(config_file)
    files, hashes, warnings = inspect_files(root, names)
    head = out(root, 'rev-parse', 'HEAD')
    pending = json.loads((state / 'pending.json').read_text()) if (state / 'pending.json').exists() else None
    tip = remote_tip(root, settings)
    if head != tip and not (pending and head == pending.get('commit') and tip in (pending.get('parent'), head)):
        raise SyncError('Local and remote HEAD differ; inspect existing commits before publishing any of them')
    changed = [name for name in files if not git(root, 'ls-files', '--error-unmatch', '--', name, check=False).returncode == 0
               or out(root, 'diff', 'HEAD', '--', name)]
    return {'ok': True, 'status': 'pending' if pending else ('ready' if changed else 'no_changes'),
            'branch': settings['branch'], 'remote': settings['expected_url'], 'head': head,
            'remote_head': tip, 'files': files, 'changed_files': changed, 'sha256': hashes, 'warnings': warnings}


def finish(root, settings, state, pending):
    validate_target(root, settings)
    if pending['remote'] != settings['expected_url'] or pending['branch'] != settings['branch']:
        raise SyncError('Pending sync belongs to another destination')
    if out(root, 'rev-parse', 'HEAD') != pending['commit']:
        raise SyncError('HEAD changed since the pending TIL commit; inspect before retrying')
    parents = out(root, 'rev-list', '--parents', '-n', '1', pending['commit']).split()
    if parents != [pending['commit'], pending['parent']]:
        raise SyncError('Pending commit parent differs from the reviewed base')
    actual = set(out(root, 'diff-tree', '--no-commit-id', '--name-only', '-r', '-z', pending['commit']).split('\0')) - {''}
    if actual != set(pending['files']) or any(out(root, 'rev-parse', pending['commit'] + ':' + name) != blob for name, blob in pending['blobs'].items()):
        raise SyncError('Commit scope or content changed after review; inspect before any push')
    # Reconcile only our paths after an interrupted commit. Never reset other staged work.
    for name in pending['files']:
        if out(root, 'diff', '--cached', pending['parent'], '--', name) and out(root, 'diff', '--cached', pending['commit'], '--', name):
            raise SyncError('Selected index entry changed after the pending commit: ' + name)
    git(root, 'reset', '-q', 'HEAD', '--', *pending['files'])
    tip = remote_tip(root, settings)
    if tip != pending['commit']:
        if tip != pending['parent']:
            raise SyncError('Remote advanced; pending TIL commit remains local for reconciliation')
        try:
            git(root, 'push', '--porcelain', '--no-follow-tags', settings['remote'], pending['commit'] + ':refs/heads/' + settings['branch'])
        except (SyncError, subprocess.TimeoutExpired):
            # A missing response is ambiguous: probe the branch before trying another push.
            if remote_tip(root, settings) != pending['commit']:
                raise SyncError('Push is not verified; the pending commit is retained for a safe retry')
    confirmed = remote_tip(root, settings)
    if confirmed != pending['commit']:
        raise SyncError('Remote HEAD verification failed; do not create another commit')
    event = {**pending, 'status': 'synced', 'verified_remote_head': confirmed,
             'verified_at': datetime.now(timezone.utc).isoformat()}
    save(state / 'last-success.json', event)
    with (state / 'history.jsonl').open('a') as stream:
        stream.write(json.dumps(event, ensure_ascii=False) + '\n')
    (state / 'pending.json').unlink()
    return {'ok': True, **event}


def sync(config_file, names, message):
    root, settings, state = setup(config_file)
    state.mkdir(parents=True, exist_ok=True)
    with (state / 'sync.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        pending_path = state / 'pending.json'
        if pending_path.exists():
            if names: raise SyncError('A previous sync is pending; run retry before starting another one')
            return finish(root, settings, state, json.loads(pending_path.read_text()))
        p = plan(config_file, names)
        if p['status'] == 'no_changes': return p
        if not message or not message.strip(): raise SyncError('A commit message is required')
        with tempfile.TemporaryDirectory(prefix='til-sync-', dir=state) as temp:
            env = {'GIT_INDEX_FILE': str(Path(temp) / 'index')}
            git(root, 'read-tree', p['head'], env=env)
            git(root, 'add', '--', *p['changed_files'], env=env)
            git(root, 'diff', '--cached', '--check', env=env)
            if any(sha(root / name) != p['sha256'][name] for name in p['files']):
                raise SyncError('A selected file changed during preparation; rerun validation')
            if out(root, 'rev-parse', 'HEAD') != p['head']:
                raise SyncError('HEAD changed during preparation')
            blobs = {name: out(root, 'rev-parse', ':' + name, env=env) for name in p['changed_files']}
            # A normal commit uses repository hooks/signing, but an isolated index omits unrelated staged files.
            git(root, 'commit', '-m', message, env=env)
        commit = out(root, 'rev-parse', 'HEAD')
        pending = {'commit': commit, 'parent': p['head'], 'branch': settings['branch'],
                   'remote': settings['expected_url'], 'files': p['changed_files'], 'sha256': p['sha256'], 'blobs': blobs}
        save(pending_path, pending)
        changed = set(out(root, 'diff-tree', '--no-commit-id', '--name-only', '-r', '-z', commit).split('\0')) - {''}
        if changed != set(p['changed_files']):
            raise SyncError('Commit hooks changed the file scope; inspect the local commit before any push')
        return finish(root, settings, state, pending)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('action', choices=['plan', 'sync', 'retry'])
    p.add_argument('--config', required=True)
    p.add_argument('--files', nargs='+', default=[])
    p.add_argument('--message')
    args = p.parse_args()
    try:
        if args.action == 'plan': result = plan(args.config, args.files)
        elif args.action == 'retry':
            _, _, state = setup(args.config)
            if args.files or args.message: raise SyncError('retry resumes the recorded commit without new files')
            if not (state / 'pending.json').exists(): raise SyncError('No pending TIL sync exists')
            result = sync(args.config, [], None)
        else: result = sync(args.config, args.files, args.message)
    except (SyncError, OSError, ValueError, KeyError, subprocess.TimeoutExpired) as exc:
        result = {'ok': False, 'error': str(exc)}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result['ok'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
