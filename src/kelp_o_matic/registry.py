from __future__ import annotations

from pathlib import Path

from rich.console import Console

from kelp_o_matic.config import ModelConfig
from kelp_o_matic.model import ONNXModel


class ModelRegistry:
    """
    A model_registry for models that allows for dynamic registration and retrieval.
    """

    def __init__(self):
        self._models = {}

    def list_models(self):
        """
        List all registered models.
        """
        return list(self._models.keys())

    def register_model(self, model_config: ModelConfig):
        """
        Register a model configuration.
        """
        if not isinstance(model_config, ModelConfig):
            raise TypeError("model_config must be an instance of ModelConfig")

        self._models[model_config.name] = ONNXModel(model_config)

    @classmethod
    def from_config_dir(cls, config_dir: str | Path):
        """
        Create a ModelRegistry instance from a directory containing model configuration files.
        """
        reg = cls()
        config_path = Path(config_dir)

        for config_file in config_path.glob("*.json"):
            # Validate and parse the JSON configuration
            config_data = ModelConfig.model_validate_json(open(config_file).read())
            reg.register_model(config_data)

        return reg

    def __getitem__(self, key):
        """
        Retrieve a model by its name.
        """
        if key not in self._models:
            raise KeyError(f"Model '{key}' is not registered.")
        return self._models[key]

    def __contains__(self, key):
        """
        Check if a model is registered by its name.
        """
        return key in self._models

    def __repr__(self):
        """
        String representation of the ModelRegistry.
        """
        return f"ModelRegistry({list(self._models.keys())})"

    def __len__(self):
        """
        Get the number of registered models.
        """
        return len(self._models)


# Initialize the model registry from the default configuration directory
model_registry = ModelRegistry.from_config_dir(Path(__file__).parent / "configs")


if __name__ == "__main__":
    # Example usage
    console = Console()
    registry = ModelRegistry.from_config_dir("configs")
    console.print(f"[bold green]Registry:[/bold green] {registry}")

    # Access a specific model
    kelp_model = registry["kelp_ps8b"]
    console.print(
        f"[cyan]Model:[/cyan] {kelp_model.cfg.name}, [cyan]Description:[/cyan] {kelp_model.cfg.description}"
    )
