from app.models import GraphEdge, GraphNode, GraphResponse
from app.services.store import search_rows


def build_graph() -> GraphResponse:
    rows = search_rows()
    nodes: list[GraphNode] = []
    edges: list[GraphEdge] = []

    story_ids_seen: set[str] = set()
    task_ids_seen: set[str] = set()

    for row in rows:
        if row.story_id not in story_ids_seen:
            nodes.append(GraphNode(id=row.story_id, label=row.story_title, kind="story"))
            story_ids_seen.add(row.story_id)

        if row.task_id not in task_ids_seen:
            nodes.append(GraphNode(id=row.task_id, label=row.task_title, kind="task"))
            task_ids_seen.add(row.task_id)

        edges.append(GraphEdge(source=row.story_id, target=row.task_id))

        if row.dependencies:
            for dep in [item.strip() for item in row.dependencies.split(",") if item.strip()]:
                edges.append(GraphEdge(source=dep, target=row.task_id))

    return GraphResponse(nodes=nodes, edges=edges)
