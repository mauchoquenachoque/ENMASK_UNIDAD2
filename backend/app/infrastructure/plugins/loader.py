import importlib
import os
import sys
from typing import Any, Dict, List, Optional, Type

from app.core.config import settings
from app.core.logging import logger
from app.core.exceptions import PluginError
from app.infrastructure.plugins.base import EnmaskPlugin
from app.domain.interfaces.connector import DatabaseConnector
from app.domain.interfaces.masking_strategy import MaskingStrategy


class PluginLoader:
    def __init__(self, plugin_dir: Optional[str] = None):
        self._plugin_dir = plugin_dir or settings.PLUGIN_DIRECTORY
        self._plugins: Dict[str, EnmaskPlugin] = {}
        self._connectors: Dict[str, Type[DatabaseConnector]] = {}
        self._strategies: Dict[str, Type[MaskingStrategy]] = {}
        self._configs: Dict[str, Dict[str, Any]] = {}

    def discover_plugins(self) -> List[str]:
        if not os.path.isdir(self._plugin_dir):
            return []
        found = []
        for entry in os.listdir(self._plugin_dir):
            full_path = os.path.join(self._plugin_dir, entry)
            if os.path.isdir(full_path) and os.path.exists(os.path.join(full_path, "__init__.py")):
                found.append(entry)
            elif entry.endswith(".py") and entry != "__init__.py":
                found.append(entry[:-3])
        return found

    def load_plugin(self, name: str) -> EnmaskPlugin:
        if name in self._plugins:
            return self._plugins[name]

        try:
            if self._plugin_dir not in sys.path:
                sys.path.insert(0, self._plugin_dir)

            module = importlib.import_module(name)

            plugin_class = None
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (
                    isinstance(attr, type)
                    and issubclass(attr, EnmaskPlugin)
                    and attr is not EnmaskPlugin
                ):
                    plugin_class = attr
                    break

            if not plugin_class:
                raise PluginError(name, "No EnmaskPlugin subclass found in module")

            plugin_instance = plugin_class()
            plugin_instance.initialize()

            self._plugins[name] = plugin_instance

            for conn_name, conn_class in plugin_instance.get_connectors().items():
                self._connectors[conn_name] = conn_class

            for strat_name, strat_class in plugin_instance.get_strategies().items():
                self._strategies[strat_name] = strat_class

            logger.info("Loaded plugin: %s v%s", plugin_instance.name, plugin_instance.version)
            return plugin_instance

        except PluginError:
            raise
        except Exception as exc:
            raise PluginError(name, f"Failed to load: {str(exc)}") from exc

    def unload_plugin(self, name: str) -> None:
        plugin = self._plugins.pop(name, None)
        if not plugin:
            raise PluginError(name, "Plugin not loaded")

        try:
            plugin.shutdown()
        except Exception as exc:
            logger.warning("Error shutting down plugin %s: %s", name, exc)

        conn_names = list(plugin.get_connectors().keys())
        for cn in conn_names:
            self._connectors.pop(cn, None)

        strat_names = list(plugin.get_strategies().keys())
        for sn in strat_names:
            self._strategies.pop(sn, None)

        logger.info("Unloaded plugin: %s", name)

    def configure_plugin(self, name: str, config: Dict[str, Any]) -> None:
        if name not in self._plugins:
            raise PluginError(name, "Plugin not loaded")
        self._configs[name] = config

    def get_plugin_info(self, name: str) -> Optional[Dict[str, Any]]:
        plugin = self._plugins.get(name)
        if not plugin:
            return None
        return {
            "name": plugin.name,
            "version": plugin.version,
            "description": plugin.description,
            "enabled": True,
            "connectors": list(plugin.get_connectors().keys()),
            "strategies": list(plugin.get_strategies().keys()),
        }

    def list_plugins(self) -> List[Dict[str, Any]]:
        result = []
        for name, plugin in self._plugins.items():
            result.append({
                "name": plugin.name,
                "version": plugin.version,
                "description": plugin.description,
                "enabled": True,
                "connectors": list(plugin.get_connectors().keys()),
                "strategies": list(plugin.get_strategies().keys()),
            })
        return result

    def get_connector(self, name: str) -> Optional[Type[DatabaseConnector]]:
        return self._connectors.get(name)

    def get_strategy(self, name: str) -> Optional[Type[MaskingStrategy]]:
        return self._strategies.get(name)

    def load_all(self) -> None:
        for name in self.discover_plugins():
            try:
                self.load_plugin(name)
            except PluginError as exc:
                logger.warning("Skipping plugin %s: %s", name, str(exc))


plugin_loader = PluginLoader()
