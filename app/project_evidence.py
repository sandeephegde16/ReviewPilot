"""Project source resolution and bounded evidence collection for grading workflows."""

from __future__ import annotations

import shutil
import subprocess
import tempfile
import zipfile
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from urllib.parse import urlparse

from app.schemas import (
    ProjectEvidenceBundle,
    ProjectEvidenceFileSnippet,
    SubmissionSourceType,
)

IGNORED_DIRECTORY_NAMES = {
    ".git",
    ".hg",
    ".svn",
    ".venv",
    "venv",
    "__pycache__",
    "node_modules",
    "dist",
    "build",
    "target",
    ".next",
    ".turbo",
}
DOCUMENTATION_FILENAMES = {"readme.md", "readme.txt", "readme.rst"}
IMPLEMENTATION_EXTENSIONS = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".java",
    ".go",
    ".rs",
    ".kt",
    ".swift",
    ".rb",
    ".php",
    ".c",
    ".cc",
    ".cpp",
    ".cs",
    ".scala",
    ".sh",
    ".yml",
    ".yaml",
    ".toml",
    ".json",
}
TEST_PATH_TOKENS = {"test", "tests", "spec", "specs"}
MAX_FILE_INVENTORY = 200
MAX_DOCUMENTATION_SNIPPETS = 3
MAX_IMPLEMENTATION_SNIPPETS = 6
MAX_TEST_SNIPPETS = 4
MAX_SNIPPET_CHARS = 1800


class ProjectEvidenceCollectionError(Exception):
    """Raised when project evidence cannot be resolved or collected."""

    def __init__(self, code: str, message: str) -> None:
        """Store a stable error code and human-readable message."""
        super().__init__(message)
        self.code = code
        self.message = message


def collect_project_evidence(
    *,
    source_type: SubmissionSourceType,
    repo_url: str | None,
    local_path: str | None,
    zip_path: str | None,
) -> ProjectEvidenceBundle:
    """Resolve the project source and collect bounded evidence for grading."""
    with _materialize_project_root(
        source_type=source_type,
        repo_url=repo_url,
        local_path=local_path,
        zip_path=zip_path,
    ) as project_root:
        return _build_project_evidence_bundle(project_root)


@contextmanager
def _materialize_project_root(
    *,
    source_type: SubmissionSourceType,
    repo_url: str | None,
    local_path: str | None,
    zip_path: str | None,
) -> Iterator[Path]:
    """Yield a local project root path for the configured submission source."""
    if source_type == "local_folder":
        project_root = Path(local_path or "").expanduser().resolve()
        if not project_root.is_dir():
            raise ProjectEvidenceCollectionError(
                code="project_source_resolution_failed",
                message="Unable to resolve the local project folder for concept grading.",
            )
        yield project_root
        return

    tempdir = Path(tempfile.mkdtemp(prefix="reviewpilot-project-"))
    try:
        if source_type == "zip_upload":
            archive_path = Path(zip_path or "").expanduser().resolve()
            if not archive_path.is_file():
                raise ProjectEvidenceCollectionError(
                    code="project_source_resolution_failed",
                    message="Unable to resolve the uploaded zip archive for concept grading.",
                )
            try:
                with zipfile.ZipFile(archive_path) as archive:
                    archive.extractall(tempdir)
            except zipfile.BadZipFile as exc:
                raise ProjectEvidenceCollectionError(
                    code="project_source_resolution_failed",
                    message="Unable to extract the uploaded zip archive for concept grading.",
                ) from exc
            yield _select_project_root(tempdir)
            return

        _clone_repository_source(repo_url=repo_url, target_directory=tempdir)
        yield tempdir
    finally:
        shutil.rmtree(tempdir, ignore_errors=True)


def _clone_repository_source(*, repo_url: str | None, target_directory: Path) -> None:
    """Clone one repository or pull request source into the target directory."""
    if not repo_url:
        raise ProjectEvidenceCollectionError(
            code="project_source_resolution_failed",
            message="Repository URL is required for github_pr concept grading.",
        )

    clone_url, pull_request_number = _normalize_repository_clone_target(repo_url)
    try:
        subprocess.run(
            ["git", "clone", "--depth", "1", clone_url, str(target_directory)],
            check=True,
            capture_output=True,
            text=True,
        )
        if pull_request_number is not None:
            branch_name = f"reviewpilot-pr-{pull_request_number}"
            subprocess.run(
                [
                    "git",
                    "-C",
                    str(target_directory),
                    "fetch",
                    "origin",
                    f"pull/{pull_request_number}/head:{branch_name}",
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            subprocess.run(
                ["git", "-C", str(target_directory), "checkout", branch_name],
                check=True,
                capture_output=True,
                text=True,
            )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise ProjectEvidenceCollectionError(
            code="project_source_resolution_failed",
            message="Unable to clone the repository required for concept grading.",
        ) from exc


def _normalize_repository_clone_target(repo_url: str) -> tuple[str, int | None]:
    """Return a cloneable repository target and an optional GitHub pull request number."""
    repository_path = Path(repo_url).expanduser()
    if repository_path.exists():
        return (str(repository_path.resolve()), None)

    parsed_url = urlparse(repo_url)
    if parsed_url.scheme == "file":
        local_path = Path(parsed_url.path).resolve()
        return (str(local_path), None)

    path_parts = [part for part in parsed_url.path.split("/") if part]
    if parsed_url.netloc == "github.com" and len(path_parts) >= 4 and path_parts[2] == "pull":
        owner, repository_name, _, pull_number = path_parts[:4]
        clone_url = f"https://github.com/{owner}/{repository_name}.git"
        return (clone_url, int(pull_number))

    return (repo_url, None)


def _select_project_root(extracted_root: Path) -> Path:
    """Return the most specific extracted project root after a zip archive is unpacked."""
    child_paths = [path for path in extracted_root.iterdir() if not path.name.startswith(".")]
    if len(child_paths) == 1 and child_paths[0].is_dir():
        return child_paths[0]
    return extracted_root


def _build_project_evidence_bundle(project_root: Path) -> ProjectEvidenceBundle:
    """Collect a bounded project evidence bundle from one resolved project root."""
    file_paths = _list_candidate_files(project_root)
    if not file_paths:
        raise ProjectEvidenceCollectionError(
            code="project_evidence_collection_failed",
            message="Unable to collect project evidence because no readable files were found.",
        )

    documentation_snippets = _build_snippets(
        project_root=project_root,
        file_paths=[path for path in file_paths if _is_documentation_file(path)],
        limit=MAX_DOCUMENTATION_SNIPPETS,
    )
    implementation_snippets = _build_snippets(
        project_root=project_root,
        file_paths=[
            path for path in file_paths if _is_implementation_file(path) and not _is_test_file(path)
        ],
        limit=MAX_IMPLEMENTATION_SNIPPETS,
    )
    test_snippets = _build_snippets(
        project_root=project_root,
        file_paths=[path for path in file_paths if _is_test_file(path)],
        limit=MAX_TEST_SNIPPETS,
    )
    file_inventory = [
        str(path.relative_to(project_root)).replace("\\", "/")
        for path in file_paths[:MAX_FILE_INVENTORY]
    ]
    summary_text = _build_summary_text(
        project_root=project_root,
        file_inventory=file_inventory,
        documentation_snippets=documentation_snippets,
        implementation_snippets=implementation_snippets,
        test_snippets=test_snippets,
    )
    return ProjectEvidenceBundle(
        project_root=str(project_root),
        file_inventory=file_inventory,
        documentation_snippets=documentation_snippets,
        implementation_snippets=implementation_snippets,
        test_snippets=test_snippets,
        summary_text=summary_text,
    )


def _list_candidate_files(project_root: Path) -> list[Path]:
    """Return bounded candidate files from the project root, excluding noisy directories."""
    candidate_files: list[Path] = []
    for path in sorted(project_root.rglob("*")):
        if not path.is_file():
            continue
        if any(part in IGNORED_DIRECTORY_NAMES for part in path.parts):
            continue
        if not _is_probably_text_file(path):
            continue
        candidate_files.append(path)
    return candidate_files


def _build_snippets(
    *,
    project_root: Path,
    file_paths: list[Path],
    limit: int,
) -> list[ProjectEvidenceFileSnippet]:
    """Return bounded file excerpts for the highest-priority files in one category."""
    snippets: list[ProjectEvidenceFileSnippet] = []
    for path in file_paths[:limit]:
        content_excerpt = _read_text_excerpt(path)
        if not content_excerpt:
            continue
        snippets.append(
            ProjectEvidenceFileSnippet(
                path=str(path.relative_to(project_root)).replace("\\", "/"),
                content_excerpt=content_excerpt,
            )
        )
    return snippets


def _build_summary_text(
    *,
    project_root: Path,
    file_inventory: list[str],
    documentation_snippets: list[ProjectEvidenceFileSnippet],
    implementation_snippets: list[ProjectEvidenceFileSnippet],
    test_snippets: list[ProjectEvidenceFileSnippet],
) -> str:
    """Format the collected evidence into one bounded prompt-friendly summary."""
    sections = [
        f"Project root: {project_root}",
        "File inventory:",
        *[f"- {path}" for path in file_inventory],
    ]
    sections.extend(_format_snippet_section("Documentation excerpts", documentation_snippets))
    sections.extend(_format_snippet_section("Implementation excerpts", implementation_snippets))
    sections.extend(_format_snippet_section("Test excerpts", test_snippets))
    return "\n".join(sections).strip()


def _format_snippet_section(
    heading: str,
    snippets: list[ProjectEvidenceFileSnippet],
) -> list[str]:
    """Format one snippet section for the evidence summary."""
    if not snippets:
        return [f"{heading}:", "(No matching files collected.)"]

    lines = [f"{heading}:"]
    for snippet in snippets:
        lines.extend([f"[{snippet.path}]", snippet.content_excerpt])
    return lines


def _read_text_excerpt(path: Path) -> str:
    """Read and trim one text excerpt for the project evidence summary."""
    try:
        content = path.read_text(encoding="utf-8", errors="ignore").strip()
    except OSError:
        return ""
    if not content:
        return ""
    return content[:MAX_SNIPPET_CHARS]


def _is_probably_text_file(path: Path) -> bool:
    """Return whether one file appears safe to treat as UTF-8 text."""
    try:
        sample = path.read_bytes()[:2048]
    except OSError:
        return False
    return b"\x00" not in sample


def _is_documentation_file(path: Path) -> bool:
    """Return whether the file is likely to contain project documentation."""
    normalized_name = path.name.lower()
    if normalized_name in DOCUMENTATION_FILENAMES:
        return True
    return path.suffix.lower() in {".md", ".rst", ".txt"} and "doc" in "/".join(
        part.lower() for part in path.parts
    )


def _is_test_file(path: Path) -> bool:
    """Return whether the file is likely to contain automated tests."""
    normalized_parts = [part.lower() for part in path.parts]
    normalized_name = path.name.lower()
    if any(token in TEST_PATH_TOKENS for token in normalized_parts):
        return True
    return normalized_name.startswith("test") or "_test." in normalized_name


def _is_implementation_file(path: Path) -> bool:
    """Return whether the file is likely to contain implementation or config details."""
    if _is_documentation_file(path):
        return False
    return path.suffix.lower() in IMPLEMENTATION_EXTENSIONS or path.name in {
        "Dockerfile",
        "Makefile",
    }
