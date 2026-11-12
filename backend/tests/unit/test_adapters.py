"""Unit tests for source adapters using mocked HTTP responses."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from vantage.models.domain import EntityType, MetricType


class TestGitHubAdapter:
    @pytest.mark.asyncio
    async def test_normalize_extracts_entity_and_stars(self):
        from vantage.data.adapters.github_adapter import GitHubAdapter

        adapter = GitHubAdapter()
        raw = [
            {
                "full_name": "owner/awesome-repo",
                "html_url": "https://github.com/owner/awesome-repo",
                "description": "An awesome repository",
                "stargazers_count": 5000,
                "forks_count": 400,
                "language": "Python",
                "topics": ["ml", "ai"],
                "open_issues_count": 10,
                "created_at": "2023-01-01T00:00:00Z",
                "pushed_at": "2024-01-01T00:00:00Z",
                "default_branch": "main",
            }
        ]
        entities, observations = await adapter.normalize(raw)
        assert len(entities) == 1
        assert entities[0].name == "owner/awesome-repo"
        assert entities[0].entity_type == EntityType.REPOSITORY
        assert entities[0].metadata["language"] == "Python"

        star_obs = [o for o in observations if o.metric_name == MetricType.STARS.value]
        assert len(star_obs) == 1
        assert star_obs[0].metric_value == 5000.0

    @pytest.mark.asyncio
    async def test_deduplication(self):
        from vantage.data.adapters.github_adapter import GitHubAdapter

        adapter = GitHubAdapter()
        raw = [
            {
                "full_name": "owner/repo",
                "html_url": "https://github.com/owner/repo",
                "description": "desc",
                "stargazers_count": 100,
                "forks_count": 10,
                "language": "Go",
                "topics": [],
                "open_issues_count": 0,
                "created_at": "",
                "pushed_at": "",
                "default_branch": "main",
            }
        ] * 3  # Same repo three times
        entities, _ = await adapter.normalize(raw)
        assert len(entities) == 1  # Deduplication by full_name


class TestHuggingFaceAdapter:
    @pytest.mark.asyncio
    async def test_normalize_model(self):
        from vantage.data.adapters.huggingface_adapter import HuggingFaceAdapter

        adapter = HuggingFaceAdapter()
        raw = [
            {
                "modelId": "bert-base-uncased",
                "pipeline_tag": "fill-mask",
                "downloads": 1_000_000,
                "likes": 2500,
                "tags": ["transformers", "pytorch"],
                "library_name": "transformers",
                "private": False,
                "gated": False,
            }
        ]
        entities, observations = await adapter.normalize(raw)
        assert len(entities) == 1
        assert entities[0].entity_type == EntityType.MODEL
        assert entities[0].primary_url == "https://huggingface.co/bert-base-uncased"

        dl_obs = [o for o in observations if o.metric_name == MetricType.DOWNLOADS.value]
        assert dl_obs[0].metric_value == 1_000_000.0


class TestArXivAdapter:
    @pytest.mark.asyncio
    async def test_normalize_paper(self):
        import xml.etree.ElementTree as ET
        from vantage.data.adapters.arxiv_adapter import ArXivAdapter

        adapter = ArXivAdapter()
        entry_xml = """<entry xmlns="http://www.w3.org/2005/Atom">
            <id>http://arxiv.org/abs/2401.00001v1</id>
            <title>Attention Is All You Need: A Survey</title>
            <summary>This paper surveys attention mechanisms.</summary>
            <published>2024-01-01T00:00:00Z</published>
            <author><name>Jane Smith</name></author>
        </entry>"""
        entry = ET.fromstring(entry_xml)
        raw = [{"entry": entry, "category": "cs.AI"}]

        entities, observations = await adapter.normalize(raw)
        assert len(entities) == 1
        assert entities[0].entity_type == EntityType.PAPER
        assert "2401.00001" in entities[0].primary_url
        assert observations[0].metric_name == MetricType.MENTIONS.value
        assert observations[0].metric_value == 1.0


class TestHackerNewsAdapter:
    @pytest.mark.asyncio
    async def test_normalize_story(self):
        from vantage.data.adapters.hackernews_adapter import HackerNewsAdapter

        adapter = HackerNewsAdapter()
        raw = [
            {
                "id": 12345678,
                "type": "story",
                "title": "New AI framework released",
                "url": "https://example.com/ai",
                "score": 350,
                "descendants": 120,
                "by": "someuser",
                "time": 1700000000,
            }
        ]
        entities, observations = await adapter.normalize(raw)
        assert len(entities) == 1
        assert entities[0].entity_type == EntityType.TOPIC
        assert entities[0].name == "hn:12345678"

        eng_obs = [o for o in observations if o.metric_name == MetricType.ENGAGEMENT.value]
        assert eng_obs[0].metric_value == 350.0


class TestPyPIAdapter:
    @pytest.mark.asyncio
    async def test_normalize_package(self):
        from vantage.data.adapters.pypi_adapter import PyPIAdapter

        adapter = PyPIAdapter()
        raw = [
            {
                "pkg": "fastapi",
                "info": {
                    "name": "fastapi",
                    "version": "0.110.0",
                    "summary": "FastAPI framework",
                    "author": "Sebastián Ramírez",
                    "home_page": "https://fastapi.tiangolo.com",
                    "requires_python": ">=3.8",
                    "classifiers": [],
                },
                "stats": {"last_month": 5_000_000},
            }
        ]
        entities, observations = await adapter.normalize(raw)
        assert len(entities) == 1
        assert entities[0].entity_type == EntityType.PACKAGE
        assert entities[0].name == "fastapi"

        dl_obs = [o for o in observations if o.metric_name == MetricType.DOWNLOADS.value]
        assert dl_obs[0].metric_value == 5_000_000.0
