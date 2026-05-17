"""应用配置管理."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field


class LLMBackendConfig(BaseModel):
    """单个 LLM 后端配置."""

    enabled: bool = True
    model: str = ""
    priority: int = 0  # 数字越小优先级越高


class OllamaConfig(LLMBackendConfig):
    """Ollama 本地配置."""

    enabled: bool = True
    base_url: str = "http://localhost:11434"
    model: str = "qwen3:14b"
    priority: int = 1


class ClaudeConfig(LLMBackendConfig):
    """Claude API 配置."""

    enabled: bool = False
    api_key: str = ""
    model: str = "claude-sonnet-4-6-20250514"
    priority: int = 2


class OpenAIConfig(LLMBackendConfig):
    """OpenAI API 配置."""

    enabled: bool = False
    api_key: str = ""
    base_url: str = "https://api.openai.com/v1"
    model: str = "gpt-4o"
    priority: int = 3


class DeepSeekConfig(LLMBackendConfig):
    """DeepSeek API 配置."""

    enabled: bool = False
    api_key: str = ""
    base_url: str = "https://api.deepseek.com"
    model: str = "deepseek-chat"
    priority: int = 3


class LLMConfig(BaseModel):
    """LLM 总配置."""

    ollama: OllamaConfig = Field(default_factory=OllamaConfig)
    claude: ClaudeConfig = Field(default_factory=ClaudeConfig)
    openai: OpenAIConfig = Field(default_factory=OpenAIConfig)
    deepseek: DeepSeekConfig = Field(default_factory=DeepSeekConfig)
    temperature: float = 0.3
    max_tokens: int = 4096
    auto_fallback: bool = True  # 本地不可用时自动切云端


class AppConfig(BaseModel):
    """应用总配置."""

    app_name: str = "GIS Agent"
    version: str = "0.1.0"
    language: Literal["zh", "en"] = "zh"

    data_dir: Path = Path.home() / "gis_agent_data"
    project_dir: Path = Path.home() / "gis_agent_projects"

    auto_save: bool = True
    auto_save_interval_minutes: int = 5

    llm: LLMConfig = Field(default_factory=LLMConfig)

    class Config:
        arbitrary_types_allowed = True


def load_config() -> AppConfig:
    """加载配置（优先环境变量，其次默认值）."""
    config = AppConfig()

    # Ollama 环境变量覆盖
    if url := os.getenv("OLLAMA_BASE_URL"):
        config.llm.ollama.base_url = url
    if model := os.getenv("OLLAMA_MODEL"):
        config.llm.ollama.model = model

    # Claude API Key
    if key := os.getenv("ANTHROPIC_API_KEY"):
        config.llm.claude.api_key = key
        config.llm.claude.enabled = True

    # OpenAI API Key
    if key := os.getenv("OPENAI_API_KEY"):
        config.llm.openai.api_key = key
        config.llm.openai.enabled = True

    # DeepSeek API Key
    if key := os.getenv("DEEPSEEK_API_KEY"):
        config.llm.deepseek.api_key = key
        config.llm.deepseek.enabled = True

    return config
