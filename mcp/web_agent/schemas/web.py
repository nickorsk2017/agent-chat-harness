"""Domain models for web_agent."""

from __future__ import annotations

from pydantic import BaseModel, Field


class NewsItem(BaseModel):
    title: str
    source: str
    url: str
    summary: str


class NewsResult(BaseModel):
    query: str
    items: list[NewsItem] = Field(default_factory=list)


class Weather(BaseModel):
    location: str
    temperature_c: float
    condition: str
    humidity_pct: int


class WebPage(BaseModel):
    url: str
    title: str
    text: str
