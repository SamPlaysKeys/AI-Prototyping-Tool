"""
Configuration Management Module

This module provides centralized configuration management for the AI Prototyping Tool,
supporting both TOML files and environment variables for configuration.
"""

import os
import json
import toml
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, asdict, field
from datetime import datetime
import logging


@dataclass
class ModelConfig:
    """Configuration for AI model settings."""

    name: str = ""
    max_tokens: int = 2048
    temperature: float = 0.7
    top_p: float = 0.9
    timeout: float = 60.0
    retries: int = 3


@dataclass
class OutputConfig:
    """Configuration for output preferences."""

    format: str = "markdown"  # markdown, html, json
    theme: str = "default"  # default, github, minimal, dark, professional
    merge_deliverables: bool = True
    include_toc: bool = True
    add_metadata: bool = True
    auto_save: bool = True
    output_directory: str = "./output"


@dataclass
class LMStudioConfig:
    """Configuration for LM Studio connection."""

    base_url: str = "http://localhost:1234/v1"
    api_key: Optional[str] = None
    auto_detect: bool = True
    health_check_interval: int = 30
    connection_timeout: float = 5.0


@dataclass
class DeliverableConfig:
    """Configuration for deliverable generation."""

    default_types: List[str] = field(default_factory=lambda: ["problem_statement"])
    completion_mode: str = "sequential"  # sequential, batch, streaming
    parallel_limit: int = 3
    template_directory: Optional[str] = None


@dataclass
class UserProfile:
    """User profile with preferences."""

    name: str = ""
    organization: str = ""
    role: str = ""
    preferred_models: List[str] = field(default_factory=list)
    favorite_deliverables: List[str] = field(default_factory=list)
    custom_templates: Dict[str, str] = field(default_factory=dict)
    usage_stats: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AppConfig:
    """Main application configuration."""

    # Core settings
    version: str = "1.0.0"
    environment: str = "development"  # development, staging, production
    debug: bool = False

    # Component configurations
    model: ModelConfig = field(default_factory=ModelConfig)
    output: OutputConfig = field(default_factory=OutputConfig)
    lm_studio: LMStudioConfig = field(default_factory=LMStudioConfig)
    deliverables: DeliverableConfig = field(default_factory=DeliverableConfig)
    user: UserProfile = field(default_factory=UserProfile)

    # System settings
    logging_level: str = "INFO"
    max_history: int = 100
    cache_enabled: bool = True
    auto_update: bool = True

    # Additional configuration sections from TOML
    server_config: Dict[str, Any] = field(default_factory=dict)
    error_handling_config: Dict[str, Any] = field(default_factory=dict)
    security_config: Dict[str, Any] = field(default_factory=dict)
    monitoring_config: Dict[str, Any] = field(default_factory=dict)

    # Last updated
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())

    def get_server_config(self) -> Dict[str, Any]:
        """Get server configuration with defaults."""
        defaults = {"host": "0.0.0.0", "port": 8000, "workers": 1, "reload": True}
        return {**defaults, **self.server_config}

    def get_error_handling_config(self) -> Dict[str, Any]:
        """Get error handling configuration with defaults."""
        defaults = {
            "enable_global_handler": True,
            "user_friendly_messages": True,
            "include_stack_traces": self.debug,
            "log_errors": True,
            "error_page_template": "error.html",
        }
        return {**defaults, **self.error_handling_config}

    def get_security_config(self) -> Dict[str, Any]:
        """Get security configuration with defaults."""
        defaults = {
            "enable_cors": True,
            "allowed_origins": ["*"],
            "api_key_header": "X-API-Key",
            "rate_limit_requests": 100,
            "rate_limit_window": 3600,
        }
        return {**defaults, **self.security_config}

    def get_monitoring_config(self) -> Dict[str, Any]:
        """Get monitoring configuration with defaults."""
        defaults = {
            "enable_metrics": True,
            "metrics_endpoint": "/metrics",
            "health_endpoint": "/health",
            "ready_endpoint": "/ready",
        }
        return {**defaults, **self.monitoring_config}


class ConfigManager:
    """Centralized configuration manager supporting TOML and environment variables."""

    def __init__(
        self,
        config_file: Optional[Union[str, Path]] = None,
        config_dir: Optional[str] = None,
    ):
        """
        Initialize the configuration manager.

        Args:
            config_file: Path to TOML configuration file (defaults to config.toml in project root)
            config_dir: Directory to store user configuration files
        """
        # Determine config file location
        if config_file:
            self.config_file = Path(config_file)
        else:
            # Look for config.toml in current directory, then parent directories
            current_dir = Path.cwd()
            for path in [current_dir] + list(current_dir.parents):
                candidate = path / "config.toml"
                if candidate.exists():
                    self.config_file = candidate
                    break
            else:
                # Default to config.toml in current directory
                self.config_file = current_dir / "config.toml"

        self.config_dir = (
            Path(config_dir) if config_dir else self._get_default_config_dir()
        )
        self.user_config_file = (
            self.config_dir / "config.json"
        )  # User-specific overrides
        self.profiles_dir = self.config_dir / "profiles"
        self.templates_dir = self.config_dir / "templates"

        # Ensure directories exist
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.profiles_dir.mkdir(parents=True, exist_ok=True)
        self.templates_dir.mkdir(parents=True, exist_ok=True)

        # Setup logging first
        self.logger = logging.getLogger(__name__)

        # Environment variable prefix
        self.env_prefix = "AIPROTO"

        # Load configuration (TOML + env vars + user overrides)
        self._config = self._load_config()

    def _get_default_config_dir(self) -> Path:
        """Get the default configuration directory."""
        if os.name == "nt":  # Windows
            base_dir = Path(os.environ.get("APPDATA", Path.home()))
        else:  # Unix-like (Linux, macOS)
            base_dir = Path.home() / ".config"

        return base_dir / "ai-prototyping-tool"

    def _load_config(self) -> AppConfig:
        """Load configuration from TOML file, environment variables, and user overrides."""
        config = AppConfig()

        # 1. Load from TOML file if it exists
        toml_data = self._load_toml_config()
        if toml_data:
            self._apply_toml_config(config, toml_data)

        # 2. Load user-specific overrides from JSON
        user_data = self._load_user_config()
        if user_data:
            self._apply_user_config(config, user_data)

        # 3. Apply environment variable overrides
        self._apply_env_overrides(config)

        return config

    def _load_toml_config(self) -> Optional[Dict[str, Any]]:
        """Load configuration from TOML file."""
        if not self.config_file.exists():
            self.logger.info(f"TOML config file not found: {self.config_file}")
            return None

        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                data = toml.load(f)
            self.logger.info(f"Loaded TOML config from: {self.config_file}")
            return data
        except (toml.TomlDecodeError, OSError) as e:
            self.logger.warning(f"Failed to load TOML config: {e}")
            return None

    def _load_user_config(self) -> Optional[Dict[str, Any]]:
        """Load user-specific configuration overrides from JSON file."""
        if not self.user_config_file.exists():
            return None

        try:
            with open(self.user_config_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.logger.debug(f"Loaded user config from: {self.user_config_file}")
            return data
        except (json.JSONDecodeError, OSError) as e:
            self.logger.warning(f"Failed to load user config: {e}")
            return None

    def _apply_toml_config(self, config: AppConfig, toml_data: Dict[str, Any]) -> None:
        """Apply TOML configuration data to AppConfig."""
        # Map TOML sections to config attributes
        section_mapping = {
            "app": ["version", "environment", "debug"],
            "logging": ["logging_level"],
            "model": "model",
            "output": "output",
            "lm_studio": "lm_studio",
            "deliverables": "deliverables",
        }

        for section, fields in section_mapping.items():
            if section not in toml_data:
                continue

            section_data = toml_data[section]

            if isinstance(fields, str):
                # Direct mapping to dataclass
                if fields == "model":
                    for key, value in section_data.items():
                        if hasattr(config.model, key):
                            setattr(config.model, key, value)
                elif fields == "output":
                    for key, value in section_data.items():
                        if hasattr(config.output, key):
                            setattr(config.output, key, value)
                elif fields == "lm_studio":
                    for key, value in section_data.items():
                        if hasattr(config.lm_studio, key):
                            setattr(config.lm_studio, key, value)
                elif fields == "deliverables":
                    for key, value in section_data.items():
                        if hasattr(config.deliverables, key):
                            setattr(config.deliverables, key, value)
            else:
                # Direct field mapping
                for field in fields:
                    if field in section_data:
                        if field == "logging_level":
                            config.logging_level = section_data.get(
                                "level", config.logging_level
                            )
                        else:
                            setattr(config, field, section_data[field])

        # Handle additional TOML sections
        if "server" in toml_data:
            server_data = toml_data["server"]
            # Store server config in a new attribute
            config.server_config = server_data

        if "error_handling" in toml_data:
            config.error_handling_config = toml_data["error_handling"]

        if "security" in toml_data:
            config.security_config = toml_data["security"]

        if "monitoring" in toml_data:
            config.monitoring_config = toml_data["monitoring"]

    def _apply_user_config(self, config: AppConfig, user_data: Dict[str, Any]) -> None:
        """Apply user-specific configuration overrides."""
        # Same logic as before for user JSON config
        for key, value in user_data.items():
            if hasattr(config, key):
                if key == "model" and isinstance(value, dict):
                    for k, v in value.items():
                        if hasattr(config.model, k):
                            setattr(config.model, k, v)
                elif key == "output" and isinstance(value, dict):
                    for k, v in value.items():
                        if hasattr(config.output, k):
                            setattr(config.output, k, v)
                elif key == "lm_studio" and isinstance(value, dict):
                    for k, v in value.items():
                        if hasattr(config.lm_studio, k):
                            setattr(config.lm_studio, k, v)
                elif key == "deliverables" and isinstance(value, dict):
                    for k, v in value.items():
                        if hasattr(config.deliverables, k):
                            setattr(config.deliverables, k, v)
                elif key == "user" and isinstance(value, dict):
                    for k, v in value.items():
                        if hasattr(config.user, k):
                            setattr(config.user, k, v)
                else:
                    setattr(config, key, value)

    def _apply_env_overrides(self, config: AppConfig) -> None:
        """Apply environment variable overrides."""
        env_mappings = {
            # App settings
            f"{self.env_prefix}_APP_ENVIRONMENT": ("environment", str),
            f"{self.env_prefix}_APP_DEBUG": ("debug", self._parse_bool),
            # Logging settings
            f"{self.env_prefix}_LOGGING_LEVEL": ("logging_level", str),
            # LM Studio settings
            f"{self.env_prefix}_LM_STUDIO_BASE_URL": ("lm_studio.base_url", str),
            f"{self.env_prefix}_LM_STUDIO_API_KEY": ("lm_studio.api_key", str),
            f"{self.env_prefix}_LM_STUDIO_CONNECTION_TIMEOUT": (
                "lm_studio.connection_timeout",
                float,
            ),
            # Model settings
            f"{self.env_prefix}_MODEL_NAME": ("model.name", str),
            f"{self.env_prefix}_MODEL_MAX_TOKENS": ("model.max_tokens", int),
            f"{self.env_prefix}_MODEL_TEMPERATURE": ("model.temperature", float),
            f"{self.env_prefix}_MODEL_TOP_P": ("model.top_p", float),
            # Output settings
            f"{self.env_prefix}_OUTPUT_FORMAT": ("output.format", str),
            f"{self.env_prefix}_OUTPUT_DIRECTORY": ("output.output_directory", str),
            f"{self.env_prefix}_OUTPUT_MERGE_DELIVERABLES": (
                "output.merge_deliverables",
                self._parse_bool,
            ),
        }

        for env_var, (attr_path, converter) in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                try:
                    converted_value = converter(value)
                    self._set_nested_attr(config, attr_path, converted_value)
                    self.logger.debug(
                        f"Applied env override: {env_var} = {converted_value}"
                    )
                except (ValueError, TypeError) as e:
                    self.logger.warning(f"Failed to apply env override {env_var}: {e}")

    def _parse_bool(self, value: str) -> bool:
        """Parse boolean value from string."""
        return value.lower() in ("true", "1", "yes", "on")

    def _set_nested_attr(self, obj: Any, attr_path: str, value: Any) -> None:
        """Set nested attribute using dot notation."""
        parts = attr_path.split(".")
        for part in parts[:-1]:
            obj = getattr(obj, part)
        setattr(obj, parts[-1], value)

    def save_config(self, config: Optional[AppConfig] = None) -> None:
        """Save configuration to file."""
        if config:
            self._config = config

        # Update timestamp
        self._config.last_updated = datetime.now().isoformat()

        # Convert to dictionary
        config_dict = asdict(self._config)

        # Save to file
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(config_dict, f, indent=2)
            self.logger.info(f"Configuration saved to {self.config_file}")
        except OSError as e:
            self.logger.error(f"Failed to save configuration: {e}")

    def get_config(self) -> AppConfig:
        """Get the current configuration."""
        return self._config

    def update_config(self, updates: Dict[str, Any]) -> None:
        """Update configuration with new values."""
        for key, value in updates.items():
            if hasattr(self._config, key):
                setattr(self._config, key, value)

        self.save_config()

    def reset_config(self) -> None:
        """Reset configuration to defaults."""
        self._config = AppConfig()
        self.save_config()
        self.logger.info("Configuration reset to defaults")

    def export_config(self, export_path: str) -> None:
        """Export configuration to a file."""
        export_file = Path(export_path)
        config_dict = asdict(self._config)

        try:
            with open(export_file, "w", encoding="utf-8") as f:
                json.dump(config_dict, f, indent=2)
            self.logger.info(f"Configuration exported to {export_file}")
        except OSError as e:
            self.logger.error(f"Failed to export configuration: {e}")

    def import_config(self, import_path: str) -> None:
        """Import configuration from a file."""
        import_file = Path(import_path)

        if not import_file.exists():
            raise FileNotFoundError(f"Config file not found: {import_file}")

        try:
            with open(import_file, "r", encoding="utf-8") as f:
                config_data = json.load(f)

            # Create new config from imported data
            config = AppConfig(**config_data)
            self.save_config(config)
            self.logger.info(f"Configuration imported from {import_file}")

        except (json.JSONDecodeError, TypeError) as e:
            self.logger.error(f"Failed to import configuration: {e}")
            raise

    def create_profile(self, profile_name: str, profile_data: UserProfile) -> None:
        """Create a new user profile."""
        profile_file = self.profiles_dir / f"{profile_name}.json"

        try:
            with open(profile_file, "w", encoding="utf-8") as f:
                json.dump(asdict(profile_data), f, indent=2)
            self.logger.info(f"Profile '{profile_name}' created")
        except OSError as e:
            self.logger.error(f"Failed to create profile: {e}")

    def load_profile(self, profile_name: str) -> UserProfile:
        """Load a user profile."""
        profile_file = self.profiles_dir / f"{profile_name}.json"

        if not profile_file.exists():
            raise FileNotFoundError(f"Profile not found: {profile_name}")

        try:
            with open(profile_file, "r", encoding="utf-8") as f:
                profile_data = json.load(f)
            return UserProfile(**profile_data)
        except (json.JSONDecodeError, TypeError) as e:
            self.logger.error(f"Failed to load profile: {e}")
            raise

    def list_profiles(self) -> List[str]:
        """List available user profiles."""
        profiles = []
        for profile_file in self.profiles_dir.glob("*.json"):
            profiles.append(profile_file.stem)
        return profiles

    def switch_profile(self, profile_name: str) -> None:
        """Switch to a different user profile."""
        profile = self.load_profile(profile_name)
        self._config.user = profile
        self.save_config()
        self.logger.info(f"Switched to profile: {profile_name}")

    def get_model_config(self) -> ModelConfig:
        """Get model configuration."""
        return self._config.model

    def update_model_config(self, **kwargs) -> None:
        """Update model configuration."""
        for key, value in kwargs.items():
            if hasattr(self._config.model, key):
                setattr(self._config.model, key, value)
        self.save_config()

    def get_output_config(self) -> OutputConfig:
        """Get output configuration."""
        return self._config.output

    def update_output_config(self, **kwargs) -> None:
        """Update output configuration."""
        for key, value in kwargs.items():
            if hasattr(self._config.output, key):
                setattr(self._config.output, key, value)
        self.save_config()

    def get_lm_studio_config(self) -> LMStudioConfig:
        """Get LM Studio configuration."""
        return self._config.lm_studio

    def update_lm_studio_config(self, **kwargs) -> None:
        """Update LM Studio configuration."""
        for key, value in kwargs.items():
            if hasattr(self._config.lm_studio, key):
                setattr(self._config.lm_studio, key, value)
        self.save_config()

    def track_usage(self, action: str, details: Dict[str, Any] = None) -> None:
        """Track usage statistics."""
        if "usage_history" not in self._config.user.usage_stats:
            self._config.user.usage_stats["usage_history"] = []

        usage_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "details": details or {},
        }

        self._config.user.usage_stats["usage_history"].append(usage_entry)

        # Keep only recent history
        if (
            len(self._config.user.usage_stats["usage_history"])
            > self._config.max_history
        ):
            self._config.user.usage_stats["usage_history"] = (
                self._config.user.usage_stats["usage_history"][
                    -self._config.max_history :
                ]
            )

        self.save_config()

    def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics."""
        return self._config.user.usage_stats

    def validate_config(self) -> Dict[str, Any]:
        """Validate current configuration."""
        validation_results = {"is_valid": True, "warnings": [], "errors": []}

        # Validate model config
        if self._config.model.max_tokens <= 0:
            validation_results["errors"].append("Max tokens must be positive")
            validation_results["is_valid"] = False

        if not (0.0 <= self._config.model.temperature <= 2.0):
            validation_results["errors"].append(
                "Temperature must be between 0.0 and 2.0"
            )
            validation_results["is_valid"] = False

        # Validate output config
        if self._config.output.format not in ["markdown", "html", "json"]:
            validation_results["errors"].append("Invalid output format")
            validation_results["is_valid"] = False

        # Validate directories
        output_dir = Path(self._config.output.output_directory)
        if not output_dir.parent.exists():
            validation_results["warnings"].append(
                f"Output directory parent does not exist: {output_dir.parent}"
            )

        return validation_results


# Global configuration manager instance
_config_manager = None


def get_config_manager(config_file: Optional[Union[str, Path]] = None) -> ConfigManager:
    """Get the global configuration manager instance."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager(config_file=config_file)
    return _config_manager


def get_config() -> AppConfig:
    """Get the current application configuration."""
    return get_config_manager().get_config()


def update_config(updates: Dict[str, Any]) -> None:
    """Update the application configuration."""
    get_config_manager().update_config(updates)


def save_config() -> None:
    """Save the current configuration."""
    get_config_manager().save_config()
