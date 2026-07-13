"""GitHub Issues plugin: fetches issues from GitHub API for blog content."""

from __future__ import annotations

import json
import urllib.request
from dataclasses import dataclass

from rich.console import Console

from ..core.config import Config
from ..core.file import Page
from .base import PluginBase

console = Console()


@dataclass
class GitHubIssue:
    """Represents a GitHub issue."""

    number: int
    title: str
    body: str
    created_at: str
    updated_at: str
    labels: list[str]
    url: str
    author: str


class GitHubIssuesPlugin(PluginBase):
    """Fetches issues from GitHub API and generates blog content."""

    name = "github-issues"

    def __init__(self) -> None:
        self.config: Config | None = None
        self.issues: list[GitHubIssue] = []

    def on_config_loaded(self, config: Config) -> None:
        self.config = config
        self._fetch_issues()

    def _fetch_issues(self) -> None:
        """Fetch issues from GitHub API."""
        if self.config is None:
            return

        # Get GitHub config from theme settings
        github_repo = getattr(self.config.theme_config.theme.iw, "github_repo", None)
        github_token = getattr(self.config.theme_config.theme.iw, "github_token", None)

        if not github_repo:
            console.print("[yellow]GitHub repo not configured[/]")
            return

        # Build API URL
        api_url = f"https://api.github.com/repos/{github_repo}/issues"
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "iw-generator",
        }

        if github_token:
            headers["Authorization"] = f"token {github_token}"

        try:
            # Fetch issues
            req = urllib.request.Request(api_url, headers=headers)
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode())

            # Parse issues (exclude pull requests)
            for item in data:
                if "pull_request" not in item:
                    issue = GitHubIssue(
                        number=item["number"],
                        title=item["title"],
                        body=item["body"] or "",
                        created_at=item["created_at"],
                        updated_at=item["updated_at"],
                        labels=[label["name"] for label in item["labels"]],
                        url=item["html_url"],
                        author=item["user"]["login"],
                    )
                    self.issues.append(issue)

            console.print(f"Fetched [cyan]{len(self.issues)}[/] issues from GitHub")

        except Exception as e:
            console.print(f"[yellow]Failed to fetch issues: {e}[/]")

    def on_page_read(self, page: Page) -> None:
        """Add issue metadata to page."""
        # Check if this page corresponds to an issue
        issue_number = self._get_issue_number(page)
        if issue_number is not None:
            issue = self._find_issue(issue_number)
            if issue:
                page.frontmatter["issue"] = {
                    "number": issue.number,
                    "url": issue.url,
                    "author": issue.author,
                    "labels": issue.labels,
                    "created_at": issue.created_at,
                    "updated_at": issue.updated_at,
                }

    def _get_issue_number(self, page: Page) -> int | None:
        """Extract issue number from page filename or frontmatter."""
        # Check frontmatter first
        if "issue_number" in page.frontmatter:
            return int(page.frontmatter["issue_number"])

        # Check filename pattern: issue-123.md or 123.md
        stem = page.source_path.stem
        if stem.startswith("issue-"):
            try:
                return int(stem[6:])
            except ValueError:
                pass
        elif stem.isdigit():
            return int(stem)

        return None

    def _find_issue(self, number: int) -> GitHubIssue | None:
        """Find issue by number."""
        for issue in self.issues:
            if issue.number == number:
                return issue
        return None


# Plugin registry entry
plugin_class = GitHubIssuesPlugin
