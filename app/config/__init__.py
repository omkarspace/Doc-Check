from .settings import get_settings

# Create a settings instance that can be imported throughout the application
settings = get_settings()

__all__ = ["settings"]
