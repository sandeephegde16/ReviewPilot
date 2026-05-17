"""Serve the lightweight web UI for the ReviewPilot workspace."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import FileResponse, RedirectResponse

UI_DIRECTORY = Path(__file__).resolve().parent / "ui"
UI_STATIC_DIRECTORY = UI_DIRECTORY / "static"
APP_SHELL_PATH = UI_DIRECTORY / "index.html"

ui_router = APIRouter(include_in_schema=False)


def get_ui_static_directory() -> Path:
    """Return the static asset directory used by the browser UI."""
    return UI_STATIC_DIRECTORY


def _serve_app_shell() -> FileResponse:
    """Return the single-page application shell used for every UI route."""
    return FileResponse(APP_SHELL_PATH)


@ui_router.get("/")
def redirect_to_assignments() -> RedirectResponse:
    """Send the browser to the assignments workspace by default."""
    return RedirectResponse(url="/assignments", status_code=307)


@ui_router.get("/assignments")
def serve_assignments_workspace() -> FileResponse:
    """Serve the assignments workspace shell."""
    return _serve_app_shell()


@ui_router.get("/dashboard")
def serve_dashboard_page() -> FileResponse:
    """Serve the dashboard shell."""
    return _serve_app_shell()


@ui_router.get("/courses")
def serve_courses_page() -> FileResponse:
    """Serve the courses shell."""
    return _serve_app_shell()


@ui_router.get("/calendar")
def serve_calendar_page() -> FileResponse:
    """Serve the calendar shell."""
    return _serve_app_shell()


@ui_router.get("/grades")
def serve_grades_page() -> FileResponse:
    """Serve the grades shell."""
    return _serve_app_shell()


@ui_router.get("/settings")
def serve_settings_page() -> FileResponse:
    """Serve the settings shell."""
    return _serve_app_shell()
