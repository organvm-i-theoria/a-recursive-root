"""
Configuration Management System

Centralized configuration for the AI Council System.
Supports environment variables, config files, and defaults.
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional
import yaml
import json
from dataclasses import dataclass, field, asdict


@dataclass
class LLMConfig:
    """LLM provider configuration"""
    # Anthropic Claude
    anthropic_api_key: Optional[str] = None
    claude_model: str = "claude-3-5-sonnet-20250219"
    claude_temperature: float = 0.7
    claude_max_tokens: int = 1000

    # OpenAI GPT
    openai_api_key: Optional[str] = None
    gpt_model: str = "gpt-4-turbo"
    gpt_temperature: float = 0.7
    gpt_max_tokens: int = 1000

    # xAI Grok
    xai_api_key: Optional[str] = None
    grok_model: str = "grok-1"
    grok_temperature: float = 0.7
    grok_max_tokens: int = 1000

    # General
    timeout: int = 30
    retry_attempts: int = 3
    retry_delay: float = 1.0


@dataclass
class EventSourceConfig:
    """Event source configuration"""
    # Twitter/X
    twitter_api_key: Optional[str] = None
    twitter_api_secret: Optional[str] = None
    twitter_access_token: Optional[str] = None
    twitter_access_secret: Optional[str] = None
    twitter_keywords: list = field(default_factory=lambda: ["AI", "crypto"])
    twitter_poll_interval: int = 60

    # News API
    news_api_key: Optional[str] = None
    news_sources: list = field(default_factory=lambda: ["techcrunch", "bbc-news"])
    news_categories: list = field(default_factory=lambda: ["technology"])
    news_poll_interval: int = 300

    # RSS Feeds
    rss_feed_urls: list = field(default_factory=list)
    rss_poll_interval: int = 600

    # General
    event_queue_size: int = 1000
    min_controversy: float = 0.5


@dataclass
class DebateConfig:
    """Debate configuration"""
    council_size: int = 5
    max_rounds: int = 3
    response_timeout: int = 30
    voting_enabled: bool = True
    formation_method: str = "diverse"  # diverse, random, rng


@dataclass
class TTSConfig:
    """Text-to-speech configuration"""
    engine: str = "elevenlabs"  # elevenlabs, pyttsx3, gtts
    elevenlabs_api_key: Optional[str] = None
    voice_mapping: Dict[str, str] = field(default_factory=dict)
    speed: float = 1.0
    volume: float = 1.0
    output_dir: str = "output/audio"


@dataclass
class StreamingConfig:
    """Streaming configuration"""
    enabled: bool = False
    output_dir: str = "output/streams"
    video_width: int = 1280
    video_height: int = 720
    fps: int = 30
    audio_bitrate: str = "192k"
    video_bitrate: str = "2M"


@dataclass
class WebConfig:
    """Web server configuration"""
    enabled: bool = True
    host: str = "0.0.0.0"
    port: int = 8000
    cors_origins: list = field(default_factory=lambda: ["*"])
    api_prefix: str = "/api/v1"


@dataclass
class LoggingConfig:
    """Logging configuration"""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file: Optional[str] = None
    console: bool = True


@dataclass
class Config:
    """Master configuration"""
    llm: LLMConfig = field(default_factory=LLMConfig)
    events: EventSourceConfig = field(default_factory=EventSourceConfig)
    debate: DebateConfig = field(default_factory=DebateConfig)
    tts: TTSConfig = field(default_factory=TTSConfig)
    streaming: StreamingConfig = field(default_factory=StreamingConfig)
    web: WebConfig = field(default_factory=WebConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)

    # General settings
    environment: str = "development"  # development, staging, production
    debug: bool = True


class ConfigManager:
    """
    Configuration manager

    Loads config from:
    1. Default values
    2. Config file (config.yaml or config.json)
    3. Environment variables (highest priority)
    """

    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path
        self.config = self._load_config()

    def _load_config(self) -> Config:
        """Load configuration from all sources"""
        # Start with defaults
        config = Config()

        # Load from file if exists
        if self.config_path and self.config_path.exists():
            config = self._load_from_file(self.config_path, config)
        else:
            # Try default locations
            for path in [Path("config.yaml"), Path("config.json"), Path("../config.yaml")]:
                if path.exists():
                    config = self._load_from_file(path, config)
                    break

        # Override with environment variables
        config = self._load_from_env(config)

        return config

    def _load_from_file(self, path: Path, config: Config) -> Config:
        """Load config from YAML or JSON file"""
        with open(path, 'r') as f:
            if path.suffix == '.yaml' or path.suffix == '.yml':
                data = yaml.safe_load(f)
            elif path.suffix == '.json':
                data = json.load(f)
            else:
                return config

        # Update config with file data
        if data:
            config = self._update_config(config, data)

        return config

    def _load_from_env(self, config: Config) -> Config:
        """Load config from environment variables"""
        # LLM
        if os.getenv("ANTHROPIC_API_KEY"):
            config.llm.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        if os.getenv("OPENAI_API_KEY"):
            config.llm.openai_api_key = os.getenv("OPENAI_API_KEY")
        if os.getenv("XAI_API_KEY"):
            config.llm.xai_api_key = os.getenv("XAI_API_KEY")

        # Events
        if os.getenv("TWITTER_API_KEY"):
            config.events.twitter_api_key = os.getenv("TWITTER_API_KEY")
        if os.getenv("TWITTER_API_SECRET"):
            config.events.twitter_api_secret = os.getenv("TWITTER_API_SECRET")
        if os.getenv("NEWS_API_KEY"):
            config.events.news_api_key = os.getenv("NEWS_API_KEY")

        # TTS
        if os.getenv("ELEVENLABS_API_KEY"):
            config.tts.elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")

        # General
        if os.getenv("ENVIRONMENT"):
            config.environment = os.getenv("ENVIRONMENT")
        if os.getenv("DEBUG"):
            config.debug = os.getenv("DEBUG").lower() == "true"

        return config

    def _update_config(self, config: Config, data: Dict[str, Any]) -> Config:
        """Update config object from dictionary"""
        # LLM
        if "llm" in data:
            for key, value in data["llm"].items():
                if hasattr(config.llm, key):
                    setattr(config.llm, key, value)

        # Events
        if "events" in data:
            for key, value in data["events"].items():
                if hasattr(config.events, key):
                    setattr(config.events, key, value)

        # Debate
        if "debate" in data:
            for key, value in data["debate"].items():
                if hasattr(config.debate, key):
                    setattr(config.debate, key, value)

        # TTS
        if "tts" in data:
            for key, value in data["tts"].items():
                if hasattr(config.tts, key):
                    setattr(config.tts, key, value)

        # Streaming
        if "streaming" in data:
            for key, value in data["streaming"].items():
                if hasattr(config.streaming, key):
                    setattr(config.streaming, key, value)

        # Web
        if "web" in data:
            for key, value in data["web"].items():
                if hasattr(config.web, key):
                    setattr(config.web, key, value)

        # Logging
        if "logging" in data:
            for key, value in data["logging"].items():
                if hasattr(config.logging, key):
                    setattr(config.logging, key, value)

        # General
        if "environment" in data:
            config.environment = data["environment"]
        if "debug" in data:
            config.debug = data["debug"]

        return config

    def get(self, key: str, default: Any = None) -> Any:
        """Get config value by dot notation key"""
        parts = key.split('.')
        value = self.config

        for part in parts:
            if hasattr(value, part):
                value = getattr(value, part)
            else:
                return default

        return value

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary"""
        return asdict(self.config)

    def save(self, path: Path, format: str = "yaml") -> None:
        """Save config to file"""
        data = self.to_dict()

        with open(path, 'w') as f:
            if format == "yaml":
                yaml.dump(data, f, default_flow_style=False)
            elif format == "json":
                json.dump(data, f, indent=2)

    def validate(self) -> tuple[bool, list[str]]:
        """Validate configuration"""
        errors = []

        # Check required API keys based on enabled features
        if not self.config.llm.anthropic_api_key and not self.config.llm.openai_api_key:
            errors.append("No LLM API key configured (ANTHROPIC_API_KEY or OPENAI_API_KEY required)")

        # Validate debate config
        if self.config.debate.council_size < 3:
            errors.append("Council size must be at least 3")

        if self.config.debate.max_rounds < 1:
            errors.append("Max rounds must be at least 1")

        # Validate streaming config
        if self.config.streaming.enabled:
            if self.config.streaming.video_width < 640:
                errors.append("Video width must be at least 640")

        return len(errors) == 0, errors


# Global config instance
_config_manager: Optional[ConfigManager] = None


def get_config(config_path: Optional[Path] = None) -> ConfigManager:
    """Get global config manager instance"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager(config_path)
    return _config_manager


def reload_config(config_path: Optional[Path] = None) -> ConfigManager:
    """Reload configuration"""
    global _config_manager
    _config_manager = ConfigManager(config_path)
    return _config_manager
