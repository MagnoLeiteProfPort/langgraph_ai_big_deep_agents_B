# app/graph_tracer.py
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Set, Tuple, Optional
import contextvars


# Context variable to know "who is the current node"
_current_node: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "current_node", default=None
)


@dataclass
class CallGraph:
    nodes: Set[str] = field(default_factory=set)
    edges: Set[Tuple[str, str]] = field(default_factory=set)

    def add_edge(self, src: str, dst: str) -> None:
        self.nodes.add(src)
        self.nodes.add(dst)
        self.edges.add((src, dst))

    def clear(self) -> None:
        self.nodes.clear()
        self.edges.clear()

    def as_mermaid_flowchart(self, direction: str = "LR") -> str:
        """
        Build a Mermaid flowchart definition based on the recorded edges.

        Example output:

        flowchart LR
          pipeline --> generate_axis_unit_context
          generate_axis_unit_context --> generate_ideal_roles
          ...
        """
        lines = [f"flowchart {direction}"]
        # deterministic order for nicer diffs
        for src, dst in sorted(self.edges):
            lines.append(f"  {src} --> {dst}")
        return "\n".join(lines)


# Global graph instance for "last run"
call_graph = CallGraph()


class trace_node:
    """
    Context manager / decorator to mark a logical node in the graph.

    Usage as context manager:
        with trace_node("pipeline"):
            ...

    Usage as decorator:
        @trace_node("generate_axis_unit_context")
        def my_tool(...):
            ...

    Whenever a traced node is entered from another traced node, we record
    an edge (caller -> callee).
    """

    def __init__(self, name: str):
        self.name = name
        self._token = None

    def __enter__(self):
        parent = _current_node.get()
        if parent is not None and parent != self.name:
            call_graph.add_edge(parent, self.name)
        self._token = _current_node.set(self.name)
        return self

    def __exit__(self, exc_type, exc, tb):
        if self._token is not None:
            _current_node.reset(self._token)

    def __call__(self, fn):
        # decorator mode
        name = self.name

        def wrapper(*args, **kwargs):
            parent = _current_node.get()
            if parent is not None and parent != name:
                call_graph.add_edge(parent, name)
            token = _current_node.set(name)
            try:
                return fn(*args, **kwargs)
            finally:
                _current_node.reset(token)

        wrapper.__name__ = fn.__name__
        wrapper.__doc__ = fn.__doc__
        return wrapper
