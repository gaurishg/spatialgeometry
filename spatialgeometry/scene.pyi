import numpy as np
from numpy.typing import NDArray

FloatArray = NDArray[np.float64]

def node_init(
    n_children: int,
    T: FloatArray,
    wT: FloatArray,
    wq: FloatArray,
    parent: object | None,
    children: list[object],
) -> object: ...
def node_update(
    node: object,
    n_children: int,
    parent: object | None,
    children: list[object],
) -> None: ...
def scene_graph_children(node: object) -> None: ...
def scene_graph_tree(node: object) -> None: ...
