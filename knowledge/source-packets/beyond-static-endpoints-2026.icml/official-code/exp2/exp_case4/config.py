"""Hardcoded config for case4 MinIO and Memos endpoints."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MinioConfig:
    endpoint: str
    access_key: str
    secret_key: str
    secure: bool
    bucket_name: str


@dataclass(frozen=True)
class MemosConfig:
    base_url: str
    api_version: str
    access_token: str


@dataclass(frozen=True)
class Case4Config:
    minio: MinioConfig
    memos: MemosConfig


# NOTE:
# 这些值按用户要求从 experiment/mcp-server/settings.toml 固化而来，
# 在本流程中直接写死使用，不再运行时读取 settings.toml。
HARDCODED_MINIO_ENDPOINT = "127.0.0.1:9000"
HARDCODED_MINIO_ACCESS_KEY = "minioadmin"
HARDCODED_MINIO_SECRET_KEY = "minioadmin"
HARDCODED_MINIO_SECURE = False
HARDCODED_MINIO_BUCKET = "mybucket"

# 用户要求 memos 地址固定本地 localhost / 127.0.0.1，故这里固定 localhost。
HARDCODED_MEMOS_BASE_URL = "http://localhost:5230"
HARDCODED_MEMOS_API_VERSION = "v1"
HARDCODED_MEMOS_ACCESS_TOKEN = (
    "eyJhbGciOiJIUzI1NiIsImtpZCI6InYxIiwidHlwIjoiSldUIn0."
    "eyJuYW1lIjoibHNxIiwiaXNzIjoibWVtb3MiLCJzdWIiOiIxIiwiYXVkIjpbInVzZXIuYWNjZXNzLXRva2VuIl0sImlhdCI6MTc1ODUyMTgwNX0."
    "7FX26C0yi_N314hQ-iLdYkISe8Esfy-Dsz3ByR7eBq0"
)


def load_case4_config() -> Case4Config:
    return Case4Config(
        minio=MinioConfig(
            endpoint=HARDCODED_MINIO_ENDPOINT,
            access_key=HARDCODED_MINIO_ACCESS_KEY,
            secret_key=HARDCODED_MINIO_SECRET_KEY,
            secure=HARDCODED_MINIO_SECURE,
            bucket_name=HARDCODED_MINIO_BUCKET,
        ),
        memos=MemosConfig(
            base_url=HARDCODED_MEMOS_BASE_URL,
            api_version=HARDCODED_MEMOS_API_VERSION,
            access_token=HARDCODED_MEMOS_ACCESS_TOKEN,
        ),
    )
