from __future__ import annotations

import json
from pathlib import Path
import re
from typing import Generic, TypeVar
from uuid import uuid4

from pydantic import BaseModel

from core.projects.loader import PROJECTS_ROOT, resolve_project_dir, validate_project_id


ENTITY_ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9_-]*$")
ModelT = TypeVar("ModelT", bound=BaseModel)


def build_entity_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


class FileSystemProjectModelRepository(Generic[ModelT]):
    def __init__(self, collection: str, model_type: type[ModelT], projects_root: Path | None = None) -> None:
        self._collection = collection
        self._model_type = model_type
        self._projects_root = projects_root or PROJECTS_ROOT

    @property
    def projects_root(self) -> Path:
        return self._projects_root

    def list_models(self, project_id: str) -> list[ModelT]:
        validate_project_id(project_id)
        data_dir = self._project_data_dir(project_id)
        if not data_dir.exists():
            return []

        items = [
            self._model_type.model_validate(json.loads(file_path.read_text(encoding="utf-8")))
            for file_path in sorted(data_dir.glob("*.json"))
        ]
        return sorted(items, key=lambda item: getattr(item, "created_at", None), reverse=True)

    def load_model(self, project_id: str, entity_id: str, *, entity_name: str) -> ModelT:
        validate_project_id(project_id)
        safe_entity_id = self._validate_entity_id(entity_id, entity_name)
        file_path = self._project_data_dir(project_id) / f"{safe_entity_id}.json"
        if not file_path.exists():
            raise FileNotFoundError(
                f"{entity_name} '{safe_entity_id}' not found for project_id '{project_id}': {file_path}"
            )
        return self._model_type.model_validate(json.loads(file_path.read_text(encoding="utf-8")))

    def save_model(self, project_id: str, entity_id: str, model: ModelT) -> ModelT:
        safe_entity_id = self._validate_entity_id(entity_id, "entity_id")
        data_dir = self._project_data_dir(project_id)
        data_dir.mkdir(parents=True, exist_ok=True)
        file_path = data_dir / f"{safe_entity_id}.json"
        file_path.write_text(json.dumps(model.model_dump(mode="json"), indent=2, ensure_ascii=False), encoding="utf-8")
        return model

    def _project_data_dir(self, project_id: str) -> Path:
        project_dir = resolve_project_dir(project_id, self._projects_root)
        return project_dir / "data" / self._collection

    @staticmethod
    def _validate_entity_id(entity_id: str, entity_name: str) -> str:
        if not isinstance(entity_id, str):
            raise ValueError(f"{entity_name} must be a string")

        normalized = entity_id.strip()
        if not normalized:
            raise ValueError(f"{entity_name} must not be empty")
        if not ENTITY_ID_PATTERN.fullmatch(normalized):
            raise ValueError(
                f"{entity_name} must match ^[a-z0-9][a-z0-9_-]*$ and must not contain path separators"
            )
        return normalized
