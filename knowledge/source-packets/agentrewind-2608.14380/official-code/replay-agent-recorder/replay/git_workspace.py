from __future__ import annotations

import errno
import fcntl
from fnmatch import fnmatchcase
import logging
import os
import shutil
import signal
import stat
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Sequence

from .errors import WorkspaceGitError, WorkspaceNotFoundError, WorkspaceRestoreError, WorkspaceSafetyError


logger = logging.getLogger(__name__)


DEFAULT_WORKSPACE_EXCLUDES = (
    ".git/**",
    "**/.git/**",
    ".replay/**",
    "**/.env",
    "**/.env.*",
    "**/secrets/**",
    "**/__pycache__/**",
    "**/.pytest_cache/**",
    "**/.venv/**",
    "**/node_modules/**",
)
STAGE_CURRENT_FILES_MAX_ATTEMPTS = 5
STAGE_CURRENT_FILES_RETRY_DELAYS = (0.05, 0.1, 0.2, 0.4)
STAGE_CURRENT_FILES_ADD_BATCH_SIZE = 512
DEFAULT_TRANSIENT_PATTERNS = ("**/.nfs*", "**/.fuse_hidden*")
WorkspaceRestorePolicy = Literal["generation-fallback", "quiesce-then-retry", "strict"]
RestoreProcessPolicy = Literal["child-process-group", "diagnose-only"]
RuntimeGitMode = Literal["workspace-native", "replay-managed"]


def _make_path_user_removable(path: Path) -> None:
    for candidate in (path.parent, path):
        try:
            mode = candidate.stat(follow_symlinks=False).st_mode
        except OSError:
            continue
        if candidate.is_symlink():
            continue
        if stat.S_ISDIR(mode):
            mode |= stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR
        else:
            mode |= stat.S_IRUSR | stat.S_IWUSR
        try:
            os.chmod(candidate, mode)
        except OSError:
            continue


def _make_path_user_readable(path: Path) -> None:
    try:
        mode = path.stat(follow_symlinks=False).st_mode
    except OSError:
        return
    if path.is_symlink():
        return
    desired_mode = mode
    if stat.S_ISDIR(mode):
        desired_mode |= stat.S_IRUSR | stat.S_IXUSR
    elif stat.S_ISREG(mode):
        desired_mode |= stat.S_IRUSR
    else:
        return
    if desired_mode != mode:
        os.chmod(path, desired_mode, follow_symlinks=False)


def _make_relative_path_stageable(root: Path, relative_path: str) -> None:
    relative = Path(relative_path)
    current = root
    for part in relative.parts[:-1]:
        current = current / part
        _make_path_user_readable(current)
    _make_path_user_readable(root / relative)


def _retry_after_making_path_user_removable(func, path: str, _exc_info) -> None:
    _make_path_user_removable(Path(path))
    func(path)


@dataclass(frozen=True)
class GitWorkspaceSpec:
    base_root: str | Path | None = None
    work_root: str | Path | None = None
    store_dir: str | Path | None = None
    include: tuple[str, ...] = ("**",)
    exclude: tuple[str, ...] = DEFAULT_WORKSPACE_EXCLUDES
    volatile_exclude: tuple[str, ...] = ()
    initial: Literal["base_root", "empty", "work_root"] = "base_root"
    allow_symlinks: bool = False
    allow_project_root: bool = False
    allow_nested_git: bool = False
    keep_worktree: bool = True
    chdir: bool = False
    direct: bool = False
    restore_policy: WorkspaceRestorePolicy = "generation-fallback"
    transient_patterns: tuple[str, ...] = DEFAULT_TRANSIENT_PATTERNS
    restore_process_policy: RestoreProcessPolicy = "child-process-group"
    path_aliases: tuple[str, ...] = ()
    path_denormalize_root: str | None = None


@dataclass(frozen=True)
class GitCheckpoint:
    commit: str
    tree: str
    parent: str | None
    changed_from_parent: bool


@dataclass(frozen=True)
class WorkspaceInitMetadata:
    workspace_id: str
    logical_root: str
    repo_dir: Path
    work_root: Path
    index_file: Path
    branch_ref: str
    initial_commit: str
    initial_tree: str
    generation_id: str
    runtime_git_mode: RuntimeGitMode


@dataclass(frozen=True)
class GitCommandResult:
    args: tuple[str, ...]
    returncode: int
    stdout: str
    stderr: str


def run_plain_git(args: Sequence[str], check: bool = True) -> GitCommandResult:
    command = ("git", *args)
    env = os.environ.copy()
    for key in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE"):
        env.pop(key, None)
    result = subprocess.run(command, env=env, text=True, capture_output=True)
    git_result = GitCommandResult(
        args=command,
        returncode=result.returncode,
        stdout=result.stdout,
        stderr=result.stderr,
    )
    if check and result.returncode != 0:
        raise WorkspaceGitError(
            f"Git command failed with exit code {result.returncode}",
            args=command,
            stderr=result.stderr,
        )
    return git_result


def contains_or_equals(parent: Path, child: Path) -> bool:
    parent_resolved = parent.resolve()
    child_resolved = child.resolve()
    return child_resolved == parent_resolved or parent_resolved in child_resolved.parents


def validate_no_symlink_ancestors(path: Path) -> None:
    current = path if path.exists() else path.parent
    for ancestor in (current, *current.parents):
        if ancestor.is_symlink():
            raise WorkspaceSafetyError(f"Path has symlink ancestor: {path}")


def validate_no_symlinks(root: Path) -> None:
    if root.is_symlink():
        raise WorkspaceSafetyError(f"Path is a symlink: {root}")
    for path in root.rglob("*"):
        if path.is_symlink():
            raise WorkspaceSafetyError(f"Symlink is not allowed in workspace source: {path}")


def _normalize_relative_parts(path: Path) -> tuple[str, ...] | None:
    parts: list[str] = []
    for part in path.parts:
        if part in ("", "."):
            continue
        if part == "..":
            if not parts:
                return None
            parts.pop()
            continue
        parts.append(part)
    return tuple(parts)


def _workspace_relative_alias_target(target_path: Path, path_aliases: Sequence[str]) -> Path | None:
    for alias in path_aliases:
        alias_path = Path(alias)
        if not alias_path.is_absolute():
            continue
        try:
            return target_path.relative_to(alias_path)
        except ValueError:
            continue
    return None


def validate_safe_internal_symlink(
    root: Path,
    path: Path,
    relative_path: str,
    *,
    path_aliases: Sequence[str] = (),
) -> None:
    target = os.readlink(path)
    target_path = Path(target)
    if target_path.is_absolute():
        alias_relative = _workspace_relative_alias_target(target_path, path_aliases)
        if alias_relative is None:
            raise WorkspaceSafetyError(f"Unsafe symlink target escapes workspace: {relative_path} -> {target}")
        normalized = _normalize_relative_parts(alias_relative)
    else:
        normalized = _normalize_relative_parts(Path(relative_path).parent / target_path)
    if normalized is None:
        raise WorkspaceSafetyError(f"Unsafe symlink target escapes workspace: {relative_path} -> {target}")
    root_parts = _normalize_relative_parts(path.relative_to(root))
    if root_parts is None:
        raise WorkspaceSafetyError(f"Unsafe symlink path in workspace: {relative_path}")


def validate_no_nested_git(root: Path) -> None:
    for path in root.rglob(".git"):
        raise WorkspaceSafetyError(f"Nested Git repository is not allowed: {path}")


def validate_workspace_paths(
    base_root: Path | None,
    work_root: Path,
    repo_dir: Path,
    log_dir: Path,
    *,
    allow_project_root: bool = False,
    direct: bool = False,
) -> None:
    work_resolved = work_root.resolve()
    repo_resolved = repo_dir.resolve()
    log_resolved = log_dir.resolve()
    project_root = Path.cwd().resolve()
    home = Path.home().resolve()

    if work_resolved == Path("/"):
        raise WorkspaceSafetyError("Workspace root cannot be filesystem root")
    if work_resolved == home:
        raise WorkspaceSafetyError("Workspace root cannot be the home directory")
    if not allow_project_root and work_resolved == project_root:
        raise WorkspaceSafetyError("Workspace root cannot be the project root")
    if not allow_project_root and contains_or_equals(work_root, project_root):
        raise WorkspaceSafetyError("Workspace root cannot contain the project root")

    if direct:
        if work_resolved == repo_resolved or work_resolved == log_resolved:
            raise WorkspaceSafetyError("Workspace root overlaps replay storage")
        if contains_or_equals(repo_dir, work_root):
            raise WorkspaceSafetyError("Workspace root cannot be inside repository directory")
        validate_no_symlink_ancestors(work_root)
        validate_no_symlink_ancestors(repo_dir)
        validate_no_symlink_ancestors(log_dir)
        if base_root is not None:
            validate_no_symlink_ancestors(base_root)
        return

    if contains_or_equals(work_root, repo_dir):
        raise WorkspaceSafetyError("Repository directory cannot be inside workspace root")
    if contains_or_equals(repo_dir, work_root):
        raise WorkspaceSafetyError("Workspace root cannot be inside repository directory")
    if contains_or_equals(work_root, log_dir / "_fs"):
        raise WorkspaceSafetyError("Workspace root cannot contain replay filesystem store")
    if contains_or_equals(work_root, log_dir):
        raise WorkspaceSafetyError("Workspace root cannot contain log directory")
    if contains_or_equals(work_root, repo_dir):
        raise WorkspaceSafetyError("Workspace root cannot contain repository directory")
    if work_resolved == repo_resolved or work_resolved == log_resolved:
        raise WorkspaceSafetyError("Workspace root overlaps replay storage")

    validate_no_symlink_ancestors(work_root)
    validate_no_symlink_ancestors(repo_dir)
    validate_no_symlink_ancestors(log_dir)

    if base_root is None:
        return

    base_resolved = base_root.resolve()
    if base_resolved == work_resolved:
        raise WorkspaceSafetyError("Base root and workspace root must differ")
    if contains_or_equals(base_root, work_root):
        raise WorkspaceSafetyError("Workspace root cannot be inside base root")
    if contains_or_equals(work_root, base_root):
        raise WorkspaceSafetyError("Base root cannot be inside workspace root")
    validate_no_symlink_ancestors(base_root)


class GitWorkspace:
    def __init__(
        self,
        *,
        workspace_id: str,
        spec: GitWorkspaceSpec,
        log_dir: Path,
        run_id: str,
        mode: Literal["record", "replay", "fork"],
        base_run: str | None = None,
    ) -> None:
        self._workspace_id = workspace_id
        self._spec = spec
        self._log_dir = Path(log_dir).resolve()
        self._run_id = run_id
        self._mode = mode
        self._base_run = base_run
        self._logical_root = f"replay://workspace/{workspace_id}"
        self._root = (
            Path(spec.work_root).resolve()
            if spec.work_root is not None
            else self._log_dir / "_workspaces" / run_id / workspace_id
        )
        self._generation_counter = 0
        self._generation_id = "gen_000"
        self._runtime_git_mode: RuntimeGitMode = "workspace-native" if spec.direct else "replay-managed"
        self._last_restore_report: dict[str, object] | None = None
        self._repo_dir = (
            Path(spec.store_dir).resolve() / f"{workspace_id}.git"
            if spec.store_dir is not None
            else self._log_dir / "_fs" / f"{workspace_id}.git"
        )
        self._index_file = self._log_dir / "_workspaces" / run_id / f"{workspace_id}.index"
        if mode == "replay":
            ref_kind = "replays"
        else:
            ref_kind = "runs"
        self._branch_ref = f"refs/replay/{ref_kind}/{run_id}/workspaces/{workspace_id}"
        self._initial_ref = f"refs/replay/runs/{run_id}/workspace-initials/{workspace_id}"

    @property
    def workspace_id(self) -> str:
        return self._workspace_id

    @property
    def spec(self) -> GitWorkspaceSpec:
        return self._spec

    @property
    def log_dir(self) -> Path:
        return self._log_dir

    @property
    def run_id(self) -> str:
        return self._run_id

    @property
    def mode(self) -> Literal["record", "replay", "fork"]:
        return self._mode

    @property
    def root(self) -> Path:
        return self._root

    @property
    def generation_id(self) -> str:
        return self._generation_id

    @property
    def runtime_git_mode(self) -> RuntimeGitMode:
        return self._runtime_git_mode

    @property
    def logical_root(self) -> str:
        return self._logical_root

    @property
    def repo_dir(self) -> Path:
        return self._repo_dir

    @property
    def index_file(self) -> Path:
        return self._index_file

    @property
    def branch_ref(self) -> str:
        return self._branch_ref

    @property
    def initial_ref(self) -> str:
        return self._initial_ref

    @property
    def nested_git_metadata_dir(self) -> Path:
        return self._log_dir / "_fs_nested_git" / self.workspace_id

    def _git_env(self) -> dict[str, str]:
        env = os.environ.copy()
        env.update(
            {
                "GIT_DIR": str(self.repo_dir),
                "GIT_WORK_TREE": str(self.root),
                "GIT_INDEX_FILE": str(self.index_file),
                "GIT_AUTHOR_NAME": "replay-agent-recorder",
                "GIT_AUTHOR_EMAIL": "replay@example.invalid",
                "GIT_COMMITTER_NAME": "replay-agent-recorder",
                "GIT_COMMITTER_EMAIL": "replay@example.invalid",
                "GIT_LITERAL_PATHSPECS": "1",
            }
        )
        return env

    def _run_git(
        self,
        args: Sequence[str],
        check: bool = True,
        input_text: str | None = None,
    ) -> GitCommandResult:
        command = ("git", *args)
        cwd = self.root if self.root.exists() else self.log_dir
        cwd.mkdir(parents=True, exist_ok=True)
        result = subprocess.run(
            command,
            env=self._git_env(),
            cwd=cwd,
            text=True,
            capture_output=True,
            input=input_text,
        )
        if result.returncode != 0 and self._clear_stale_index_lock(result.stderr):
            result = subprocess.run(
                command,
                env=self._git_env(),
                cwd=cwd,
                text=True,
                capture_output=True,
                input=input_text,
            )
        git_result = GitCommandResult(
            args=command,
            returncode=result.returncode,
            stdout=result.stdout,
            stderr=result.stderr,
        )
        if check and result.returncode != 0:
            raise WorkspaceGitError(
                "Git workspace command failed"
                f" cwd={cwd}"
                f" worktree={self.root}"
                f" returncode={result.returncode}",
                args=command,
                stderr=result.stderr,
            )
        return git_result

    def _clear_stale_index_lock(self, stderr: str) -> bool:
        """Drop a leftover ``<index>.lock`` and report whether a retry is worth it.

        Git refuses to touch the index while a lock file exists. A command that
        was interrupted mid-write (a killed runner, or the model client's SIGALRM
        request timeout firing inside ``subprocess.run``) leaves that file
        behind, and then every later workspace command fails with
        ``Unable to create '<index>.lock': File exists`` — the run is stuck for
        good. The index file is private to this workspace and only ever used by
        this process, so the lock cannot belong to a live sibling git process.
        """
        lock_path = self.index_file.with_name(f"{self.index_file.name}.lock")
        if "index.lock" not in stderr or "File exists" not in stderr:
            return False
        if str(lock_path) not in stderr:
            return False
        try:
            lock_path.unlink()
        except OSError:
            return False
        logger.warning("Removed stale Git index lock before retrying: %s", lock_path)
        return True

    def ensure_bare_repo(self) -> None:
        self.repo_dir.parent.mkdir(parents=True, exist_ok=True)
        lock_path = self.repo_dir.parent / f".{self.repo_dir.name}.init.lock"
        with lock_path.open("w", encoding="utf-8") as lock_file:
            fcntl.flock(lock_file, fcntl.LOCK_EX)
            if not (self.repo_dir / "HEAD").exists():
                run_plain_git(["init", "--bare", str(self.repo_dir)])

    def rev_parse(self, rev: str) -> str:
        return self._run_git(["rev-parse", "--verify", rev]).stdout.strip()

    def commit_tree(self, commit: str) -> str:
        return self._run_git(["show", "-s", "--format=%T", commit]).stdout.strip()

    def setup_record(self) -> WorkspaceInitMetadata:
        self._validate()
        self.ensure_bare_repo()
        checkpoint = self.import_initial_commit()
        self._save_nested_git_metadata(checkpoint.commit)
        self._run_git(["update-ref", self.branch_ref, checkpoint.commit])
        self.restore_commit(checkpoint.commit)
        return self._metadata(checkpoint)

    def setup_replay(
        self,
        initial_commit: str,
        branch_ref: str | None = None,
    ) -> WorkspaceInitMetadata:
        self._validate(require_base=False)
        if not self.repo_dir.exists():
            raise WorkspaceNotFoundError(f"Workspace repository does not exist: {self.repo_dir}")
        if branch_ref is not None:
            self._branch_ref = branch_ref
        else:
            self._branch_ref = (
                f"refs/replay/replays/{self.run_id}/workspaces/{self.workspace_id}"
            )
        commit = self.rev_parse(initial_commit)
        tree = self.commit_tree(commit)
        self._run_git(["update-ref", self.branch_ref, commit])
        self.restore_commit(commit)
        return self._metadata(GitCheckpoint(commit, tree, None, True))

    def setup_replay_preserve_current(
        self,
        initial_commit: str,
        branch_ref: str | None = None,
    ) -> WorkspaceInitMetadata:
        self._validate(require_base=False)
        if not self.repo_dir.exists():
            raise WorkspaceNotFoundError(f"Workspace repository does not exist: {self.repo_dir}")
        if branch_ref is not None:
            self._branch_ref = branch_ref
        else:
            self._branch_ref = (
                f"refs/replay/replays/{self.run_id}/workspaces/{self.workspace_id}"
            )
        commit = self.rev_parse(initial_commit)
        self._run_git(["update-ref", self.branch_ref, commit])
        checkpoint = self.commit_current(
            commit,
            f"preserve current workspace for replay {self.run_id}:{self.workspace_id}",
            allow_empty=True,
            update_ref=True,
        )
        return self._metadata(checkpoint)

    def validate_for_replay(self) -> None:
        self._validate(require_base=False)

    def setup_fork(self, fork_from_commit: str) -> GitCheckpoint:
        self._validate(require_base=False)
        self.ensure_bare_repo()
        commit = self.rev_parse(fork_from_commit)
        self._branch_ref = f"refs/replay/runs/{self.run_id}/workspaces/{self.workspace_id}"
        self._run_git(["update-ref", self.branch_ref, commit])
        return self.restore_commit(commit)

    def import_initial_commit(self) -> GitCheckpoint:
        self.index_file.parent.mkdir(parents=True, exist_ok=True)
        self.root.mkdir(parents=True, exist_ok=True)
        if self.spec.initial == "base_root":
            if self.spec.base_root is None:
                raise WorkspaceSafetyError("base_root is required when initial='base_root'")
            self._copy_initial_files(Path(self.spec.base_root), self.root)
        elif self.spec.initial == "empty":
            self._clear_work_root()
        elif self.spec.initial == "work_root":
            # Direct workspace mode: the work tree is the user's real workspace.
            # Snapshot what is already there; do not copy from base_root and do
            # not clear the directory.
            pass
        else:
            raise WorkspaceSafetyError(f"Unsupported initial mode: {self.spec.initial}")
        self._reset_index()
        tree = self.current_tree()
        commit = self._run_git(
            ["commit-tree", tree],
            input_text="Initial workspace import\n",
        ).stdout.strip()
        self._run_git(["update-ref", self.initial_ref, commit])
        return GitCheckpoint(commit=commit, tree=tree, parent=None, changed_from_parent=True)

    def restore_commit(self, commit: str) -> GitCheckpoint:
        resolved = self.rev_parse(commit)
        self.root.mkdir(parents=True, exist_ok=True)
        self.index_file.parent.mkdir(parents=True, exist_ok=True)
        if self.spec.direct:
            self._restore_commit_direct_with_policy(resolved)
            self._restore_nested_git_metadata(resolved)
        else:
            self._run_git(["read-tree", "--reset", "-u", resolved])
            self.clean_untracked()
            self._last_restore_report = {
                "strategy": "git-read-tree",
                "generation_id": self.generation_id,
                "work_root": str(self.root),
            }
        tree = self.commit_tree(resolved)
        parent = self._commit_parent(resolved)
        changed = True if parent is None else self.commit_tree(parent) != tree
        return GitCheckpoint(
            commit=resolved,
            tree=tree,
            parent=parent,
            changed_from_parent=changed,
        )

    def checkout_commit(self, commit: str) -> GitCheckpoint:
        return self.restore_commit(commit)

    def commit_current(
        self,
        parent: str | None,
        message: str,
        *,
        allow_empty: bool = True,
        update_ref: bool = True,
    ) -> GitCheckpoint:
        tree = self.current_tree()
        resolved_parent = self.rev_parse(parent) if parent else None
        parent_tree = self.commit_tree(resolved_parent) if resolved_parent else None
        changed = parent_tree != tree if resolved_parent else True
        if not changed and not allow_empty:
            if resolved_parent is None:
                raise WorkspaceGitError("Refusing to create empty root commit")
            return GitCheckpoint(
                commit=resolved_parent,
                tree=tree,
                parent=self._commit_parent(resolved_parent),
                changed_from_parent=False,
            )
        args = ["commit-tree", tree]
        if resolved_parent:
            args.extend(["-p", resolved_parent])
        commit = self._run_git(args, input_text=f"{message}\n").stdout.strip()
        self._save_nested_git_metadata(commit)
        if update_ref:
            self._run_git(["update-ref", self.branch_ref, commit])
        return GitCheckpoint(
            commit=commit,
            tree=tree,
            parent=resolved_parent,
            changed_from_parent=changed,
        )

    def materialize_tree_as_commit(
        self,
        tree: str,
        parent: str | None,
        message: str,
        *,
        update_ref: bool = True,
        restore: bool = True,
    ) -> GitCheckpoint:
        resolved_tree = self.rev_parse(f"{tree}^{{tree}}")
        resolved_parent = self.rev_parse(parent) if parent else None
        args = ["commit-tree", resolved_tree]
        if resolved_parent:
            args.extend(["-p", resolved_parent])
        commit = self._run_git(args, input_text=f"{message}\n").stdout.strip()
        self._save_nested_git_metadata(commit)
        if update_ref:
            self._run_git(["update-ref", self.branch_ref, commit])
        checkpoint = GitCheckpoint(
            commit=commit,
            tree=resolved_tree,
            parent=resolved_parent,
            changed_from_parent=(
                True if resolved_parent is None else self.commit_tree(resolved_parent) != resolved_tree
            ),
        )
        if restore:
            self.restore_commit(commit)
        return checkpoint

    def current_commit(self) -> str:
        return self.rev_parse(self.branch_ref)

    def current_tree(self) -> str:
        self._stage_current_files()
        return self._run_git(["write-tree"]).stdout.strip()

    def diff_summary(self, before_tree: str, after_tree: str) -> list[dict[str, str]]:
        result = self._run_git(["diff", "--name-status", "-z", before_tree, after_tree])
        rows: list[dict[str, str]] = []
        for status, path in _parse_name_status_z(result.stdout):
            rows.append({"status": status, "path": path})
        return rows

    def clean_untracked(self) -> None:
        self._run_git(["clean", "-fdx", "--", "."])

    def last_restore_report(self) -> dict[str, object]:
        return dict(self._last_restore_report or {"strategy": "none", "generation_id": self.generation_id})

    def consume_last_restore_report(self) -> dict[str, object]:
        report = self.last_restore_report()
        self._last_restore_report = None
        return report

    def _metadata(self, checkpoint: GitCheckpoint) -> WorkspaceInitMetadata:
        return WorkspaceInitMetadata(
            workspace_id=self.workspace_id,
            logical_root=self.logical_root,
            repo_dir=self.repo_dir,
            work_root=self.root,
            index_file=self.index_file,
            branch_ref=self.branch_ref,
            initial_commit=checkpoint.commit,
            initial_tree=checkpoint.tree,
            generation_id=self.generation_id,
            runtime_git_mode=self.runtime_git_mode,
        )

    def _validate(self, *, require_base: bool = True) -> None:
        base_root = Path(self.spec.base_root) if self.spec.base_root is not None else None
        if require_base and self.spec.initial == "base_root":
            if base_root is None:
                raise WorkspaceSafetyError("base_root is required when initial='base_root'")
            if not base_root.exists() or not base_root.is_dir():
                raise WorkspaceSafetyError(f"base_root must be an existing directory: {base_root}")
        if require_base and self.spec.initial == "work_root":
            if not self.root.exists() or not self.root.is_dir():
                raise WorkspaceSafetyError(f"work_root must be an existing directory: {self.root}")
        validate_workspace_paths(
            base_root,
            self.root,
            self.repo_dir,
            self.log_dir,
            allow_project_root=self.spec.allow_project_root,
            direct=self.spec.direct,
        )
        if base_root is not None:
            if not self.spec.allow_symlinks:
                validate_no_symlinks(base_root)
            if not self.spec.allow_nested_git:
                validate_no_nested_git(base_root)

    def _copy_initial_files(self, base_root: Path, work_root: Path) -> None:
        self._clear_work_root()
        for source, relative in self._included_file_paths(base_root):
            target = work_root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            if source.is_symlink():
                os.symlink(os.readlink(source), target)
            else:
                shutil.copy2(source, target)

    def _restore_commit_direct(self, commit: str) -> None:
        """Restore a commit into work_root without clearing unrelated files."""

        target_tree = self.commit_tree(commit)
        self.clean_volatile(commit=commit, target_tree=target_tree)
        current_tree = self.current_tree()
        result = self._run_git(["diff", "--name-status", "-z", current_tree, target_tree])

        checkout_paths: list[str] = []
        delete_paths: list[str] = []
        for status, path in _parse_name_status_z(result.stdout):
            if status == "D":
                delete_paths.append(path)
            else:
                checkout_paths.append(path)

        self._run_git(["read-tree", "--reset", commit])

        for relative in delete_paths:
            self._remove_worktree_path(relative, commit=commit, target_tree=target_tree)

        if checkout_paths:
            self._run_git(["checkout-index", "-f", "--", *checkout_paths])
        self.clean_volatile(commit=commit, target_tree=target_tree)

    def _restore_commit_direct_with_policy(self, commit: str) -> None:
        target_tree = self.commit_tree(commit)
        try:
            self._restore_commit_direct(commit)
            self._last_restore_report = {
                "strategy": "direct",
                "generation_id": self.generation_id,
                "work_root": str(self.root),
                "target_commit": commit,
                "target_tree": target_tree,
            }
            return
        except WorkspaceRestoreError as exc:
            if self.spec.restore_policy == "strict":
                raise
            failures = [exc]
            actions = ["initial-restore-failed"]

        retry_delays = (0.02, 0.05)
        for delay in retry_delays:
            time.sleep(delay)
            try:
                self._restore_commit_direct(commit)
                self._last_restore_report = {
                    "strategy": "retry",
                    "generation_id": self.generation_id,
                    "work_root": str(self.root),
                    "target_commit": commit,
                    "target_tree": target_tree,
                    "attempted_actions": actions + [f"retry-after-{delay:.2f}s"],
                }
                return
            except WorkspaceRestoreError as exc:
                failures.append(exc)
                actions.append(f"retry-after-{delay:.2f}s-failed")

        holders = self._workspace_holder_processes()
        terminated = self._terminate_workspace_holders(holders)
        if holders:
            actions.append("scan-holder-processes")
        if terminated:
            actions.append("terminate-holder-processes")
            time.sleep(0.05)
            try:
                self._restore_commit_direct(commit)
                self._last_restore_report = {
                    "strategy": "quiesce-then-retry",
                    "generation_id": self.generation_id,
                    "work_root": str(self.root),
                    "target_commit": commit,
                    "target_tree": target_tree,
                    "holder_processes": holders,
                    "terminated_processes": terminated,
                    "attempted_actions": actions,
                }
                return
            except WorkspaceRestoreError as exc:
                failures.append(exc)
                actions.append("post-quiesce-retry-failed")

        if self.spec.restore_policy == "generation-fallback" and all(failure.is_transient for failure in failures):
            self._fallback_to_generation(
                commit,
                target_tree=target_tree,
                failures=failures,
                attempted_actions=actions,
                holder_processes=holders,
                terminated_processes=terminated,
            )
            return

        last = failures[-1]
        last.attempted_actions.extend(actions)
        last.holder_processes = holders
        raise last

    def _remove_worktree_path(
        self,
        relative_path: str,
        *,
        commit: str | None = None,
        target_tree: str | None = None,
    ) -> None:
        relative = Path(relative_path)
        if relative.is_absolute() or ".." in relative.parts:
            raise WorkspaceSafetyError(f"Unsafe workspace path in checkpoint: {relative_path}")
        path = self.root / relative
        root = self.root
        try:
            if path.is_symlink():
                try:
                    path.unlink()
                except OSError:
                    _make_path_user_removable(path)
                    path.unlink()
            elif path.is_dir():
                shutil.rmtree(path, onerror=_retry_after_making_path_user_removable)
            elif path.exists():
                try:
                    path.unlink()
                except OSError:
                    _make_path_user_removable(path)
                    path.unlink()
        except OSError as exc:
            raise self._restore_error_from_oserror(
                exc,
                fallback_path=path,
                fallback_relative=relative_path,
                commit=commit,
                target_tree=target_tree,
            ) from exc

        parent = path.parent
        while parent != root and root in parent.parents:
            try:
                parent.rmdir()
            except OSError:
                break
            parent = parent.parent

    def _clear_work_root(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        for path in self.root.iterdir():
            if path.is_dir() and not path.is_symlink():
                shutil.rmtree(path)
            else:
                path.unlink()

    def _nested_git_metadata_paths(self) -> list[tuple[Path, str]]:
        if not self.spec.allow_nested_git:
            return []
        if not self.root.exists():
            return []
        resolved_root = self.root.resolve()
        metadata_paths: list[tuple[Path, str]] = []
        for current, dirnames, filenames in os.walk(resolved_root, topdown=True):
            current_path = Path(current)
            kept_dirs: list[str] = []
            for dirname in sorted(dirnames):
                child = current_path / dirname
                if dirname == ".git" and current_path != resolved_root:
                    metadata_paths.append((child, child.relative_to(resolved_root).as_posix()))
                    continue
                kept_dirs.append(dirname)
            dirnames[:] = kept_dirs
            for filename in sorted(filenames):
                if filename != ".git" or current_path == resolved_root:
                    continue
                child = current_path / filename
                metadata_paths.append((child, child.relative_to(resolved_root).as_posix()))
        return metadata_paths

    def _save_nested_git_metadata(self, commit: str) -> None:
        metadata_paths = self._nested_git_metadata_paths()
        destination_root = self.nested_git_metadata_dir / commit
        if destination_root.exists():
            shutil.rmtree(destination_root)
        if not metadata_paths:
            return
        for source, relative in metadata_paths:
            destination = destination_root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            if source.is_dir() and not source.is_symlink():
                _copy_tree_missing(source, destination)
            else:
                if not destination.exists():
                    shutil.copy2(source, destination, follow_symlinks=False)

    def _restore_nested_git_metadata(self, commit: str) -> None:
        source_root = self.nested_git_metadata_dir / commit
        if not self.spec.allow_nested_git or not source_root.exists():
            return
        metadata_paths: list[tuple[Path, str]] = []
        for current, dirnames, filenames in os.walk(source_root, topdown=True):
            current_path = Path(current)
            kept_dirs: list[str] = []
            for dirname in sorted(dirnames):
                child = current_path / dirname
                if dirname == ".git":
                    metadata_paths.append((child, child.relative_to(source_root).as_posix()))
                    continue
                kept_dirs.append(dirname)
            dirnames[:] = kept_dirs
            for filename in sorted(filenames):
                if filename != ".git":
                    continue
                child = current_path / filename
                metadata_paths.append((child, child.relative_to(source_root).as_posix()))

        for source, relative in metadata_paths:
            destination = self.root / relative
            if not destination.parent.exists():
                continue
            if destination.exists() or destination.is_symlink():
                if destination.is_dir() and not destination.is_symlink():
                    shutil.rmtree(destination, onerror=_retry_after_making_path_user_removable)
                else:
                    destination.unlink()
            if source.is_dir() and not source.is_symlink():
                shutil.copytree(source, destination, symlinks=True)
            else:
                shutil.copy2(source, destination, follow_symlinks=False)

    def _stage_current_files(self) -> None:
        for attempt in range(STAGE_CURRENT_FILES_MAX_ATTEMPTS):
            self.index_file.parent.mkdir(parents=True, exist_ok=True)
            self.root.mkdir(parents=True, exist_ok=True)
            baseline = self._current_index_baseline()
            if baseline:
                self._run_git(["read-tree", "--reset", baseline])
                files, deleted_files = self._changed_files_from_index()
            else:
                self._reset_index()
                files = self._included_files()
                deleted_files = []
            if not files and not deleted_files:
                return
            try:
                if deleted_files:
                    self._run_git(["rm", "-q", "--cached", "--ignore-unmatch", "--", *deleted_files])
                if files:
                    manual_files = [file for file in files if self._requires_manual_stage(file)]
                    manual_file_set = set(manual_files)
                    normal_files = [file for file in files if file not in manual_file_set]
                    for file in normal_files:
                        _make_relative_path_stageable(self.root, file)
                    for batch_start in range(0, len(normal_files), STAGE_CURRENT_FILES_ADD_BATCH_SIZE):
                        batch = normal_files[batch_start : batch_start + STAGE_CURRENT_FILES_ADD_BATCH_SIZE]
                        if batch:
                            self._run_git(["add", "-f", "--", *batch])
                    for file in manual_files:
                        self._stage_file_by_hash(file)
                return
            except WorkspaceGitError as exc:
                if attempt < STAGE_CURRENT_FILES_MAX_ATTEMPTS - 1 and (
                    _is_disappearing_file_error(exc) or _is_permission_denied_error(exc)
                ):
                    time.sleep(STAGE_CURRENT_FILES_RETRY_DELAYS[attempt])
                    continue
                raise

    def _current_index_baseline(self) -> str | None:
        result = self._run_git(["rev-parse", "--verify", self.branch_ref], check=False)
        if result.returncode == 0:
            return result.stdout.strip()
        return None

    def _changed_files_from_index(self) -> tuple[list[str], list[str]]:
        changed = {
            relative
            for relative in (
                *self._git_z_paths(["ls-files", "-m", "-z"]),
                *self._git_z_paths(["ls-files", "-o", "-z"]),
            )
            if self._is_stageable_existing_path(relative)
        }
        deleted = {
            relative
            for relative in self._git_z_paths(["ls-files", "-d", "-z"])
            if self._is_included(relative)
        }
        return sorted(changed), sorted(deleted)

    def _git_z_paths(self, args: Sequence[str]) -> list[str]:
        output = self._run_git(args).stdout
        return [item for item in output.split("\0") if item]

    def _is_stageable_existing_path(self, relative_path: str) -> bool:
        if not self._is_included(relative_path):
            return False
        path = self.root / relative_path
        try:
            _make_relative_path_stageable(self.root, relative_path)
            if path.is_symlink():
                if not self.spec.allow_symlinks:
                    raise WorkspaceSafetyError(f"Symlink is not allowed in workspace: {path}")
                # Git stores symlink targets as blob text, so staging a runtime-created
                # symlink does not follow the target or read outside the workspace.
                return True
            if not path.is_file():
                return False
            if not os.access(path, os.R_OK):
                # A container process running as root can leave a workspace file
                # unreadable to the host Replay process (e.g. john.rec, rewritten
                # every second as root by a background John-the-Ripper run). Such a
                # transient side-effect file cannot be hashed into the snapshot, so
                # skip it rather than aborting the whole task with a WorkspaceGitError.
                logger.warning("Skipping unreadable workspace file from snapshot: %s", path)
                return False
            return True
        except OSError as exc:
            if exc.errno != errno.ENAMETOOLONG:
                raise
            # A runaway agent script can nest directories until the absolute path
            # exceeds PATH_MAX (reshard-c4-data recursed into 275 `segment-*`
            # levels). Git lists the entry relative to the work tree, but no host
            # syscall can reach it, so it can never be hashed into a snapshot:
            # skip it instead of killing the whole task.
            logger.warning("Skipping workspace path that exceeds PATH_MAX: %s", path)
            return False

    def _requires_manual_stage(self, relative_path: str) -> bool:
        if not self.spec.allow_nested_git:
            return False
        relative = Path(relative_path)
        if relative.is_absolute() or ".." in relative.parts:
            return False
        parts = relative.parts
        for depth in range(1, len(parts)):
            if (self.root.joinpath(*parts[:depth]) / ".git").exists():
                return True
        return False

    def _stage_file_by_hash(self, relative_path: str) -> None:
        relative = Path(relative_path)
        if relative.is_absolute() or ".." in relative.parts:
            raise WorkspaceSafetyError(f"Unsafe workspace path in checkpoint: {relative_path}")
        path = self.root / relative
        if path.is_symlink():
            if not self.spec.allow_symlinks:
                raise WorkspaceSafetyError(f"Symlink is not allowed in workspace: {path}")
            blob = self._run_git(["hash-object", "-w", "--stdin"], input_text=os.readlink(path)).stdout.strip()
            mode = "120000"
        else:
            blob = self._run_git(["hash-object", "-w", "--", str(path)]).stdout.strip()
            mode = "100755" if os.access(path, os.X_OK) else "100644"
        self._run_git(["update-index", "--add", "--cacheinfo", f"{mode},{blob},{relative.as_posix()}"])

    def _reset_index(self) -> None:
        if self.index_file.exists():
            self.index_file.unlink()
        self._run_git(["read-tree", "--empty"])

    def _included_files(self) -> list[str]:
        return [relative for _path, relative in self._included_file_paths(self.root)]

    def _included_file_paths(self, root: Path) -> list[tuple[Path, str]]:
        files: list[tuple[Path, str]] = []
        if not root.exists():
            return files
        resolved_root = root.resolve()
        for current, dirnames, filenames in os.walk(resolved_root, topdown=True):
            current_path = Path(current)
            kept_dirs: list[str] = []
            for dirname in sorted(dirnames):
                child = current_path / dirname
                relative_dir = child.relative_to(resolved_root).as_posix()
                if child.is_symlink():
                    if not self.spec.allow_symlinks:
                        raise WorkspaceSafetyError(f"Symlink is not allowed in workspace: {child}")
                    validate_safe_internal_symlink(
                        resolved_root,
                        child,
                        relative_dir,
                        path_aliases=self.spec.path_aliases,
                    )
                    if self._is_included(relative_dir) and not self._is_excluded_directory(relative_dir):
                        files.append((child, relative_dir))
                    continue
                if self._is_excluded_directory(relative_dir):
                    continue
                kept_dirs.append(dirname)
            dirnames[:] = kept_dirs

            for filename in sorted(filenames):
                path = current_path / filename
                relative = path.relative_to(resolved_root).as_posix()
                if path.is_symlink():
                    if not self.spec.allow_symlinks:
                        raise WorkspaceSafetyError(f"Symlink is not allowed in workspace: {path}")
                    validate_safe_internal_symlink(
                        resolved_root,
                        path,
                        relative,
                        path_aliases=self.spec.path_aliases,
                    )
                    if self._is_included(relative):
                        files.append((path, relative))
                    continue
                if not path.is_file():
                    continue
                if self._is_included(relative):
                    files.append((path, relative))
        return files

    def _restore_error_from_oserror(
        self,
        exc: OSError,
        *,
        fallback_path: Path,
        fallback_relative: str,
        commit: str | None,
        target_tree: str | None,
    ) -> WorkspaceRestoreError:
        raw_path = Path(exc.filename) if exc.filename else fallback_path
        path = raw_path if raw_path.is_absolute() else fallback_path
        relative = self._relative_for_error_path(path, fallback_relative)
        is_transient = self._is_transient_residue(relative)
        if not is_transient and fallback_path.is_dir():
            is_transient = self._path_contains_only_transient_residue(fallback_path)
        return WorkspaceRestoreError(
            "Workspace restore failed",
            path=path,
            relative_path=relative,
            errno_value=exc.errno,
            commit=commit,
            target_tree=target_tree,
            is_transient=is_transient and exc.errno == errno.EBUSY,
            holder_processes=[],
            attempted_actions=["remove"],
        )

    def _relative_for_error_path(self, path: Path, fallback_relative: str) -> str:
        try:
            return path.resolve().relative_to(self.root.resolve()).as_posix()
        except (OSError, ValueError):
            return fallback_relative

    def _fallback_to_generation(
        self,
        commit: str,
        *,
        target_tree: str,
        failures: list[WorkspaceRestoreError],
        attempted_actions: list[str],
        holder_processes: list[dict[str, object]],
        terminated_processes: list[dict[str, object]],
    ) -> None:
        old_root = self.root
        new_root = self._next_generation_root()
        new_root.mkdir(parents=True, exist_ok=False)
        self._root = new_root.resolve()
        self._runtime_git_mode = "replay-managed"
        self._sync_runtime_environment()
        self._run_git(["read-tree", "--reset", commit])
        self._run_git(["checkout-index", "-a", "-f"])
        current_tree = self.current_tree()
        if current_tree != target_tree:
            raise WorkspaceRestoreError(
                "Workspace generation fallback materialized the wrong tree",
                path=self.root,
                relative_path=".",
                commit=commit,
                target_tree=target_tree,
                is_transient=False,
                holder_processes=holder_processes,
                attempted_actions=[*attempted_actions, "generation-fallback"],
            )
        self._last_restore_report = {
            "strategy": "generation-fallback",
            "generation_id": self.generation_id,
            "old_work_root": str(old_root),
            "new_work_root": str(self.root),
            "work_root": str(self.root),
            "target_commit": commit,
            "target_tree": target_tree,
            "failures": [self._restore_failure_record(failure) for failure in failures],
            "holder_processes": holder_processes,
            "terminated_processes": terminated_processes,
            "attempted_actions": [*attempted_actions, "generation-fallback"],
        }

    def _next_generation_root(self) -> Path:
        self._generation_counter += 1
        self._generation_id = f"gen_{self._generation_counter:03d}"
        return self.log_dir / "_workspaces" / self.run_id / self.workspace_id / "generations" / self.generation_id

    def _restore_failure_record(self, failure: WorkspaceRestoreError) -> dict[str, object]:
        return {
            "path": str(failure.path) if failure.path is not None else None,
            "relative_path": failure.relative_path,
            "errno": failure.errno,
            "is_transient": failure.is_transient,
            "attempted_actions": list(failure.attempted_actions),
        }

    def _sync_runtime_environment(self) -> None:
        if os.environ.get("REPLAY_WORKSPACE_ID") != self.workspace_id:
            return
        os.environ["REPLAY_WORKSPACE_ROOT"] = str(self.root)
        os.environ["REPLAY_WORKSPACE_LOGICAL_ROOT"] = self.logical_root
        if self.runtime_git_mode == "replay-managed":
            os.environ["GIT_DIR"] = str(self.repo_dir)
            os.environ["GIT_WORK_TREE"] = str(self.root)
            os.environ["GIT_INDEX_FILE"] = str(self.index_file)

    def _workspace_holder_processes(self) -> list[dict[str, object]]:
        proc_root = Path("/proc")
        if not proc_root.exists():
            return []
        root = self.root.resolve()
        current_pid = os.getpid()
        current_pgid = os.getpgrp()
        ppid_by_pid = self._process_parent_map(proc_root)
        descendants = self._process_descendants(current_pid, ppid_by_pid)
        holders: list[dict[str, object]] = []
        for entry in proc_root.iterdir():
            if not entry.name.isdigit():
                continue
            pid = int(entry.name)
            if pid == current_pid:
                continue
            try:
                pgid = os.getpgid(pid)
            except OSError:
                continue
            paths: list[str] = []
            for probe in ("cwd", "exe"):
                try:
                    target = (entry / probe).resolve()
                except OSError:
                    continue
                if target == root or root in target.parents:
                    paths.append(f"{probe}:{target}")
            fd_dir = entry / "fd"
            try:
                fd_entries = list(fd_dir.iterdir())
            except OSError:
                fd_entries = []
            for fd_entry in fd_entries[:256]:
                try:
                    target = fd_entry.resolve()
                except OSError:
                    continue
                if target == root or root in target.parents:
                    paths.append(f"fd:{fd_entry.name}:{target}")
                    break
            if not paths:
                continue
            try:
                cmdline = (entry / "cmdline").read_bytes().replace(b"\0", b" ").decode("utf-8", "replace").strip()
            except OSError:
                cmdline = ""
            holders.append(
                {
                    "pid": pid,
                    "pgid": pgid,
                    "ppid": ppid_by_pid.get(pid),
                    "safe_to_terminate": pid in descendants or (
                        pgid == current_pgid and ppid_by_pid.get(pid) == current_pid
                    ),
                    "cmdline": cmdline,
                    "paths": paths,
                }
            )
        return holders

    def _process_parent_map(self, proc_root: Path) -> dict[int, int]:
        parents: dict[int, int] = {}
        for entry in proc_root.iterdir():
            if not entry.name.isdigit():
                continue
            try:
                status = (entry / "status").read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            ppid = None
            for line in status.splitlines():
                if line.startswith("PPid:"):
                    try:
                        ppid = int(line.split()[1])
                    except (IndexError, ValueError):
                        ppid = None
                    break
            if ppid is not None:
                parents[int(entry.name)] = ppid
        return parents

    def _process_descendants(self, pid: int, ppid_by_pid: dict[int, int]) -> set[int]:
        descendants: set[int] = set()
        changed = True
        while changed:
            changed = False
            for child, parent in ppid_by_pid.items():
                if child in descendants:
                    continue
                if parent == pid or parent in descendants:
                    descendants.add(child)
                    changed = True
        return descendants

    def _terminate_workspace_holders(self, holders: list[dict[str, object]]) -> list[dict[str, object]]:
        if self.spec.restore_process_policy != "child-process-group":
            return []
        terminated: list[dict[str, object]] = []
        for holder in holders:
            if not holder.get("safe_to_terminate"):
                continue
            pid = holder.get("pid")
            if not isinstance(pid, int):
                continue
            try:
                os.kill(pid, signal.SIGTERM)
            except OSError:
                continue
            terminated.append(holder)
        return terminated

    def clean_volatile(self, *, commit: str | None = None, target_tree: str | None = None) -> None:
        """Remove volatile paths from the worktree without touching regular excludes."""

        if not self.spec.volatile_exclude or not self.root.exists():
            return
        paths = self._volatile_paths()
        for relative in sorted(paths, key=lambda value: len(Path(value).parts), reverse=True):
            try:
                self._remove_worktree_path(relative, commit=commit, target_tree=target_tree)
            except WorkspaceRestoreError as exc:
                # A live container process (e.g. a background QEMU run writing to a
                # volatile logs/ dir) can repopulate a volatile path faster than we
                # remove it, so the final rmdir sees ENOTEMPTY. Volatile paths are
                # runtime junk outside the tracked tree, so leaving a transiently
                # busy one is safe; skip it rather than aborting the whole restore
                # (which would crash an otherwise-successful backtrack/abort).
                if exc.errno != errno.ENOTEMPTY:
                    raise
                logger.warning("Skipping volatile path busy with concurrent writes: %s", relative)

    def _volatile_paths(self) -> list[str]:
        paths: list[str] = []
        resolved_root = self.root.resolve()
        for current, dirnames, filenames in os.walk(resolved_root, topdown=True):
            current_path = Path(current)
            kept_dirs: list[str] = []
            for dirname in sorted(dirnames):
                child = current_path / dirname
                relative_dir = child.relative_to(resolved_root).as_posix()
                if self._is_volatile_directory(relative_dir):
                    paths.append(relative_dir)
                    continue
                kept_dirs.append(dirname)
            dirnames[:] = kept_dirs

            for filename in sorted(filenames):
                path = current_path / filename
                relative = path.relative_to(resolved_root).as_posix()
                if self._is_volatile(relative):
                    paths.append(relative)
        return paths

    def _is_excluded_directory(self, relative_path: str) -> bool:
        path = relative_path.strip("/")
        probe = f"{path}/__replay_dir__" if path else "__replay_dir__"
        return any(
            _matches_pattern(path, pattern) or _matches_pattern(probe, pattern)
            for pattern in (*self.spec.exclude, *self.spec.volatile_exclude)
        )

    def _is_included(self, relative_path: str) -> bool:
        if self._is_transient_residue(relative_path):
            return False
        included = any(_matches_pattern(relative_path, pattern) for pattern in self.spec.include)
        excluded = any(
            _matches_pattern(relative_path, pattern)
            for pattern in (*self.spec.exclude, *self.spec.volatile_exclude)
        )
        return included and not excluded

    def _is_transient_residue(self, relative_path: str) -> bool:
        return any(_matches_pattern(relative_path, pattern) for pattern in self.spec.transient_patterns)

    def _path_contains_only_transient_residue(self, path: Path) -> bool:
        if not path.exists() and not path.is_symlink():
            return False
        if path.is_symlink() or path.is_file():
            relative = self._relative_for_error_path(path, path.name)
            return self._is_transient_residue(relative)
        if not path.is_dir():
            return False
        saw_residue = False
        for current, dirnames, filenames in os.walk(path):
            current_path = Path(current)
            for filename in filenames:
                saw_residue = True
                relative = self._relative_for_error_path(current_path / filename, filename)
                if not self._is_transient_residue(relative):
                    return False
            for dirname in list(dirnames):
                child = current_path / dirname
                if child.is_symlink():
                    saw_residue = True
                    relative = self._relative_for_error_path(child, dirname)
                    if not self._is_transient_residue(relative):
                        return False
                    dirnames.remove(dirname)
        return saw_residue

    def _is_volatile_directory(self, relative_path: str) -> bool:
        path = relative_path.strip("/")
        probe = f"{path}/__replay_dir__" if path else "__replay_dir__"
        return any(
            _matches_pattern(path, pattern) or _matches_pattern(probe, pattern)
            for pattern in self.spec.volatile_exclude
        )

    def _is_volatile(self, relative_path: str) -> bool:
        return any(_matches_pattern(relative_path, pattern) for pattern in self.spec.volatile_exclude)

    def _commit_parent(self, commit: str) -> str | None:
        result = self._run_git(["show", "-s", "--format=%P", commit]).stdout.strip()
        return result.split()[0] if result else None


def _parse_name_status_z(output: str) -> list[tuple[str, str]]:
    fields = output.split("\0")
    if fields and fields[-1] == "":
        fields.pop()

    rows: list[tuple[str, str]] = []
    index = 0
    while index < len(fields):
        status = fields[index]
        index += 1
        if not status:
            continue
        if status.startswith("R"):
            if index + 1 >= len(fields):
                break
            old_path = fields[index]
            new_path = fields[index + 1]
            index += 2
            rows.append(("D", old_path))
            rows.append(("A", new_path))
            continue
        if index >= len(fields):
            break
        rows.append((status[:1], fields[index]))
        index += 1
    return rows


def _copy_tree_missing(source: Path, destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    for child in sorted(source.iterdir()):
        target = destination / child.name
        if child.is_symlink():
            if target.exists() or target.is_symlink():
                continue
            os.symlink(os.readlink(child), target)
            shutil.copystat(child, target, follow_symlinks=False)
            continue
        if child.is_dir():
            _copy_tree_missing(child, target)
            continue
        if target.exists():
            continue
        shutil.copy2(child, target, follow_symlinks=False)
    try:
        shutil.copystat(source, destination)
    except OSError:
        pass


def _matches_pattern(relative_path: str, pattern: str) -> bool:
    path = relative_path.strip("/")
    pat = pattern.strip("/")
    if pat == "**":
        return True
    return _match_path_parts(path.split("/"), pat.split("/"))


def _match_path_parts(path_parts: list[str], pattern_parts: list[str]) -> bool:
    if not pattern_parts:
        return not path_parts
    pattern_part = pattern_parts[0]
    if pattern_part == "**":
        if len(pattern_parts) == 1:
            return True
        return any(
            _match_path_parts(path_parts[index:], pattern_parts[1:])
            for index in range(len(path_parts) + 1)
        )
    if not path_parts:
        return False
    return fnmatchcase(path_parts[0], pattern_part) and _match_path_parts(
        path_parts[1:],
        pattern_parts[1:],
    )


def _is_disappearing_file_error(exc: WorkspaceGitError) -> bool:
    message = str(exc)
    if "unstable object source data" in message:
        return True
    if "pathspec" in message and "did not match any files" in message:
        return True
    return (
        "No such file or directory" in message
        and ("unable to stat" in message or "pathspec" in message)
    )


def _is_permission_denied_error(exc: WorkspaceGitError) -> bool:
    message = str(exc)
    return "Permission denied" in message or (
        "could not open" in message and "for reading" in message
    )
