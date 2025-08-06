from __future__ import annotations

from pathlib import Path


from kelp_o_matic.config import ModelConfig
from kelp_o_matic.model import ONNXModel


class ModelRegistry:
    """
    A model_registry for models that allows for dynamic registration and retrieval.
    Supports multiple versions of the same model with calendar versioning.
    """

    def __init__(self):
        # Changed to nested dict: {name: {version: model}}
        self._models = {}

    def list_models(self):
        """
        List all registered model names and versions.
        Returns list of (name, version) tuples.
        """
        models = []
        for name, versions in self._models.items():
            for version in versions.keys():
                models.append((name, version))
        return models

    def list_model_names(self):
        """
        List unique model names (without versions).
        """
        return list(self._models.keys())

    def register_model(self, model_config: ModelConfig):
        """
        Register a model configuration.
        """
        if not isinstance(model_config, ModelConfig):
            raise TypeError("model_config must be an instance of ModelConfig")

        name = model_config.name
        version = model_config.version

        if name not in self._models:
            self._models[name] = {}

        self._models[name][version] = ONNXModel(model_config)

    @classmethod
    def from_config_dir(cls, config_dir: str | Path):
        """
        Create a ModelRegistry instance from a directory containing model configuration files.
        Config files should be named with pattern: {name}_{version}.json
        """
        reg = cls()
        config_path = Path(config_dir)

        for config_file in config_path.glob("*.json"):
            # Validate and parse the JSON configuration
            config_data = ModelConfig.model_validate_json(open(config_file).read())
            reg.register_model(config_data)

        return reg

    def get_latest_version(self, name: str) -> str:
        """
        Get the latest version of a model by calendar versioning.
        """
        if name not in self._models:
            raise KeyError(f"Model '{name}' is not registered.")

        versions = list(self._models[name].keys())
        # Sort by version string (calendar versioning works with string sort)
        return max(versions)

    def __getitem__(self, key: str | tuple[str, str]):
        """
        Retrieve a model by its name (latest version) or by (name, version) tuple.

        Args:
            key: Either model name (str) for latest version, or (name, version) tuple

        Returns:
            ONNXModel instance
        """
        if isinstance(key, tuple):
            name, version = key
            if name not in self._models:
                raise KeyError(f"Model '{name}' is not registered.")
            if version not in self._models[name]:
                available_versions = list(self._models[name].keys())
                raise KeyError(
                    f"Version '{version}' of model '{name}' is not registered. "
                    f"Available versions: {available_versions}"
                )
            return self._models[name][version]
        else:
            # Single string key - get latest version
            name = key
            if name not in self._models:
                raise KeyError(f"Model '{name}' is not registered.")
            latest_version = self.get_latest_version(name)
            return self._models[name][latest_version]

    def __contains__(self, key: str | tuple[str, str]) -> bool:
        """
        Check if a model is registered by its name or (name, version).
        """
        if isinstance(key, tuple):
            name, version = key
            return name in self._models and version in self._models[name]
        else:
            return key in self._models

    def __repr__(self):
        """
        String representation of the ModelRegistry.
        """
        model_info = []
        for name, versions in self._models.items():
            version_list = list(versions.keys())
            model_info.append(f"{name}: {version_list}")
        return f"ModelRegistry({model_info})"

    def __len__(self):
        """
        Get the total number of registered model versions.
        """
        return sum(len(versions) for versions in self._models.values())


# Initialize the model registry from the default configuration directory
model_registry = ModelRegistry.from_config_dir(Path(__file__).parent / "configs")


if __name__ == "__main__":
    # Example usage
    from kelp_o_matic.utils import console

    registry = ModelRegistry.from_config_dir("configs")
    console.print(f"[bold green]Registry:[/bold green] {registry}")

    # Access a specific model
    kelp_model = registry["kelp_ps8b"]
    console.print(
        f"[cyan]Model:[/cyan] {kelp_model.cfg.name}, [cyan]Description:[/cyan] {kelp_model.cfg.description}"
    )
