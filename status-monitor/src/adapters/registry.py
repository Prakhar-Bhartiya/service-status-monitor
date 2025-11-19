from typing import Type, Dict, Any
from .base import BaseAdapter

class AdapterRegistry:
    def __init__(self):
        self.adapters: Dict[str, Type[BaseAdapter]] = {}

    def register_adapter(self, name: str, adapter: Type[BaseAdapter]) -> None:
        if name in self.adapters:
            raise ValueError(f"Adapter '{name}' is already registered.")
        self.adapters[name] = adapter

    def get_adapter(self, name: str) -> Type[BaseAdapter]:
        adapter = self.adapters.get(name)
        if adapter is None:
            raise ValueError(f"Adapter '{name}' is not registered.")
        return adapter

    def list_adapters(self) -> Dict[str, Type[BaseAdapter]]:
        return self.adapters.keys()