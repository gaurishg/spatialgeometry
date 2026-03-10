#!/usr/bin/env python
"""
@author: Jesse Haviland
"""

from collections import UserList
from typing import Any, SupportsIndex, overload

from spatialgeometry.geom.SceneNode import SceneNode


class SceneGroup(SceneNode, UserList[SceneNode]):  # type: ignore[misc]
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

    @overload
    def __getitem__(self, i: SupportsIndex) -> SceneNode: ...

    @overload
    def __getitem__(self, i: slice) -> "SceneGroup": ...

    def __getitem__(self, i: SupportsIndex | slice) -> "SceneNode | SceneGroup":
        if isinstance(i, slice):
            return SceneGroup(scene_children=self._scene_children[i])
        return self._scene_children[i]

    @property
    def data(self) -> list[SceneNode]:
        return self._scene_children

    @data.setter
    def data(self, value: list[SceneNode]) -> None:
        self._scene_children = value
