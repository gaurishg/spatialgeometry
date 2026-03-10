#!/usr/bin/env python
"""
@author: Jesse Haviland
"""

import os
from collections.abc import Iterator
from io import StringIO
from typing import Any, TypeAlias
from warnings import warn

import numpy as np
from numpy.typing import ArrayLike, NDArray
from spatialmath.base.argcheck import getvector

from spatialgeometry.geom.Shape import Shape, update

FloatArray: TypeAlias = NDArray[np.float64]
ClosestPointResult: TypeAlias = tuple[
    float | None,
    FloatArray | None,
    FloatArray | None,
]

p: Any = None
_pyb: bool | None = None


def _import_pyb() -> None:
    import importlib

    global _pyb
    global p

    try:
        from spatialgeometry.tools.stdout_supress import pipes
    except Exception:  # pragma nocover
        from contextlib import contextmanager

        @contextmanager
        def pipes(
            stdout: Any = None,
            stderr: Any = None,
            encoding: Any = None,
        ) -> Iterator[tuple[None, None]]:
            yield (None, None)

    try:
        out = StringIO()
        try:
            with pipes(stdout=out, stderr=None):
                p = importlib.import_module("pybullet")
        except Exception:  # pragma nocover
            p = importlib.import_module("pybullet")

        cid = p.connect(p.SHARED_MEMORY)
        if cid < 0:
            p.connect(p.DIRECT)
        _pyb = True
    except ImportError:  # pragma nocover
        _pyb = False


class CollisionShape(Shape):
    def __init__(self, collision: bool = True, **kwargs: Any) -> None:
        self.co: int | None = None
        self.pinit: bool = False
        super().__init__(**kwargs)
        self._collision = collision

    # def __copy__(self):
    #     """
    #     Copy of CollisionShape object

    #     :return: Shallow copy of CollisionShape object
    #     :rtype: CollisionShape
    #     """
    #     print("HELLO")
    #     # new = copy.copy(super())
    #     # for k, v in self.__dict__.items():
    #     #     if k.startswith("_") and isinstance(v, np.ndarray):
    #     #         setattr(new, k, np.copy(v))

    def _update_pyb(self) -> None:
        if _pyb and self.co is not None:
            p.resetBasePositionAndOrientation(self.co, self._wT[:3, 3], self._wq)

    def _s_init_pob(self, col: int) -> None:
        self.co = p.createMultiBody(
            baseMass=1, baseInertialFramePosition=[0, 0, 0], baseCollisionShapeIndex=col
        )
        self.pinit = True

    def _init_pob(self) -> None:  # pragma nocover
        pass

    def _check_pyb(self) -> None:
        if _pyb is None:
            _import_pyb()

    def closest_point(
        self, shape: "CollisionShape", inf_dist: float = 1.0
    ) -> ClosestPointResult:
        """
        closest_point(shape, inf_dist) returns the minimum euclidean
        distance between self and shape, provided it is less than inf_dist.
        It will also return the points on self and shape in the world frame
        which connect the line of length distance between the shapes. If the
        distance is negative then the shapes are collided.

        :param shape: The shape to compare distance to
        :type shape: Shape
        :param inf_dist: The minimum distance within which to consider
            the shape
        :type inf_dist: float
        :returns: d, p1, p2 where d is the distance between the shapes,
            p1 and p2 are the points in the world frame on the respective
            shapes. The points returned are [x, y, z].
        :rtype: float, ndarray(1x3), ndarray(1x3)
        """

        self._check_pyb()

        if not _pyb:  # pragma nocover
            raise ImportError(
                "The package PyBullet is required for collision "
                "functionality. Install using pip install pybullet"
            )

        if not self.pinit:
            self._init_pob()
            self._update_pyb()

        self._update_pyb()

        if not shape.pinit:
            shape._init_pob()
            shape._update_pyb()

        shape._update_pyb()

        ret = p.getClosestPoints(self.co, shape.co, inf_dist)

        try:
            return ret[0][8], np.array(ret[0][5]), np.array(ret[0][6])
        except ValueError:
            return None, None, None
        except IndexError:
            # Obstacle is further away than inf_dist
            return None, None, None

    def iscollided(self, shape: "CollisionShape") -> bool:
        """
        iscollided(shape) checks if self and shape have collided

        :param shape: The shape to compare distance to
        :type shape: Shape
        :returns: True if shapes have collided
        :rtype: bool
        """

        d, _, _ = self.closest_point(shape)

        if d is not None and d <= 0:
            return True
        else:
            return False

    def collided(self, shape: "CollisionShape") -> bool:
        """
        collided(shape) checks if self and shape have collided

        :param shape: The shape to compare distance to
        :type shape: Shape
        :returns: True if shapes have collided
        :rtype: bool
        """
        warn("collided is deprecated, use iscollided instead", FutureWarning)
        return self.iscollided(shape)


class Mesh(CollisionShape):
    """
    A mesh object described by an stl or collada file.

    :param filename: The path to the mesh that contains this object.
        This is the absolute path.
    :type filename: str
    :param scale: The scaling value for the mesh along the XYZ axes. If
        ``None``, assumes no scale is applied.
    :type scale: list (3) float, optional
    :param base: Local reference frame of the shape
    :type base: SE3
    :param collision: This shape is being used as a collision object
    :type collision: bool

    """

    def __init__(
        self,
        filename: str | None = None,
        scale: ArrayLike | None = (1, 1, 1),
        **kwargs: Any,
    ) -> None:
        super().__init__(stype="mesh", **kwargs)

        self.filename = filename
        self.scale = scale

    def _init_pob(self) -> None:
        if self.filename is None:
            raise ValueError("A mesh filename must be supplied")

        _, file_extension = os.path.splitext(self.filename)
        if (file_extension == ".stl" or file_extension == ".STL") and self.collision:

            col = p.createCollisionShape(
                shapeType=p.GEOM_MESH, fileName=self.filename, meshScale=self.scale
            )

            super()._s_init_pob(col)
        else:
            raise ValueError(
                "This shape has self.collision=False meaning it "
                "is not to be used as a collision object"
            )

    @property
    def scale(self) -> FloatArray:
        return self._scale

    @scale.setter
    @update
    def scale(self, value: ArrayLike | None) -> None:
        if value is not None:
            value = getvector(value, 3)
        else:
            value = getvector([1, 1, 1], 3)
        self._scale = np.array(value)

    @property
    def filename(self) -> str | None:
        return self._filename

    @filename.setter
    @update
    def filename(self, value: str | None) -> None:
        self._filename = value

    def to_dict(self) -> dict[str, Any]:
        """
        to_dict() returns the shapes information in dictionary form

        :returns: All information about the shape
        :rtype: dict
        """

        shape = super().to_dict()
        shape["filename"] = self.filename
        shape["scale"] = self.scale.tolist()
        return shape


class Cylinder(CollisionShape):
    """A cylinder whose center is at the local origin.
    Parameters

    :param radius: The radius of the cylinder in meters.
    :type radius: float
    :param length: The length of the cylinder in meters.
    :type length: float
    :param base: Local reference frame of the shape
    :type base: SE3
    :param collision: This shape is being used as a collision object
    :type collision: bool

    """

    def __init__(self, radius: float, length: float, **kwargs: Any) -> None:
        super().__init__(stype="cylinder", **kwargs)
        self.radius = radius
        self.length = length

    def _init_pob(self) -> None:
        if self.collision:
            col = p.createCollisionShape(
                shapeType=p.GEOM_CYLINDER, radius=self.radius, height=self.length
            )

            super()._s_init_pob(col)
        else:
            raise ValueError(
                "This shape has self.collision=False meaning it "
                "is not to be used as a collision object"
            )

    @property
    def radius(self) -> float:
        return self._radius

    @radius.setter
    @update
    def radius(self, value: float) -> None:
        self._radius = float(value)

    @property
    def length(self) -> float:
        return self._length

    @length.setter
    @update
    def length(self, value: float) -> None:
        self._length = float(value)

    def to_dict(self) -> dict[str, Any]:
        """
        to_dict() returns the shapes information in dictionary form

        :returns: All information about the shape
        :rtype: dict
        """

        shape = super().to_dict()
        shape["radius"] = self.radius
        shape["length"] = self.length
        return shape


class Sphere(CollisionShape):
    """
    A sphere whose center is at the local origin.

    :param radius: The radius of the sphere in meters.
    :type radius: float
    :param base: Local reference frame of the shape
    :type base: SE3
    :param collision: This shape is being used as a collision object
    :type collision: bool

    """

    def __init__(self, radius: float, **kwargs: Any) -> None:
        super().__init__(stype="sphere", **kwargs)
        self.radius = radius

    def _init_pob(self) -> None:
        if self.collision:
            col = p.createCollisionShape(shapeType=p.GEOM_SPHERE, radius=self.radius)

            super()._s_init_pob(col)
        else:
            raise ValueError(
                "This shape has self.collision=False meaning it "
                "is not to be used as a collision object"
            )

    @property
    def radius(self) -> float:
        return self._radius

    @radius.setter
    @update
    def radius(self, value: float) -> None:
        self._radius = float(value)

    def to_dict(self) -> dict[str, Any]:
        """
        to_dict() returns the shapes information in dictionary form

        :returns: All information about the shape
        :rtype: dict
        """

        shape = super().to_dict()
        shape["radius"] = self.radius
        return shape


class Cuboid(CollisionShape):
    """
    A rectangular prism whose center is at the local origin.

    :param scale: The length, width, and height of the cuboid in meters.
    :type scale: list (3) float
    :param base: Local reference frame of the shape
    :type base: SE3
    :param collision: This shape is being used as a collision object
    :type collision: bool

    """

    def __init__(self, scale: ArrayLike | None, **kwargs: Any) -> None:
        super().__init__(stype="cuboid", **kwargs)
        self.scale = scale

    def _init_pob(self) -> None:

        if self.collision:
            col = p.createCollisionShape(
                shapeType=p.GEOM_BOX,
                halfExtents=self.scale / 2,
            )

            super()._s_init_pob(col)
        else:
            raise ValueError(
                "This shape has self.collision=False meaning it "
                "is not to be used as a collision object"
            )

    @property
    def scale(self) -> FloatArray:
        return self._scale

    @scale.setter
    @update
    def scale(self, value: ArrayLike | None) -> None:
        if value is not None:
            value = getvector(value, 3)
        else:
            value = getvector([1, 1, 1], 3)
        self._scale = np.array(value)

    def to_dict(self) -> dict[str, Any]:
        """
        to_dict() returns the shapes information in dictionary form

        :returns: All information about the shape
        :rtype: dict
        """

        shape = super().to_dict()
        shape["scale"] = self.scale.tolist()
        return shape


class Box(Cuboid):
    def __init__(self, scale: ArrayLike | None, **kwargs: Any) -> None:
        warn("Box is deprecated, use Cuboid instead", FutureWarning)
        super().__init__(scale, **kwargs)
