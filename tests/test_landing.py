from jinja2 import TemplateNotFound
import pytest
from flask.testing import FlaskClient
from typing import Any, Callable


def test_landing_page(client: FlaskClient) -> None:
    response = client.get("/")
    assert response.status_code == 200
    # If your landing page has "Welcome" text:
    assert b"Welcome" in response.data


def test_missing_template(client: FlaskClient, monkeypatch: pytest.MonkeyPatch) -> None:
    # Simulate a missing template scenario
    def mock_render_template(*args: Any, **kwargs: Any) -> None:
        raise TemplateNotFound("landing.html")

    monkeypatch.setattr("flaskr.landing.render_template", mock_render_template)

    with pytest.raises(TemplateNotFound):
        client.get("/")
