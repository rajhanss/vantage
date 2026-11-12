"""Co-occurrence entity graph construction and community detection."""
from __future__ import annotations

from collections import defaultdict

import networkx as nx

from vantage.models.domain import Entity, EntityType, GraphData, GraphEdge, GraphNode


def build_entity_graph(
    entities: list[Entity],
    relationships: list[dict],
) -> nx.Graph:
    """Build a weighted undirected graph from entities and stored relationships."""
    G: nx.Graph = nx.Graph()

    for entity in entities:
        G.add_node(
            entity.id,
            name=entity.name,
            entity_type=entity.entity_type.value,
            domain=entity.domain,
        )

    for rel in relationships:
        src = rel.get("source_entity_id")
        tgt = rel.get("target_entity_id")
        weight = float(rel.get("weight", 1.0))
        rtype = rel.get("relation_type", "co_occurs_with")
        if src and tgt and G.has_node(src) and G.has_node(tgt):
            if G.has_edge(src, tgt):
                G[src][tgt]["weight"] += weight
            else:
                G.add_edge(src, tgt, weight=weight, relation_type=rtype)

    # Lightweight co-occurrence edges within same domain
    _add_cooccurrence_edges(G, entities)

    return G


def _add_cooccurrence_edges(G: nx.Graph, entities: list[Entity]) -> None:
    """Connect entities from the same domain with weak co-occurrence edges."""
    by_type: dict[str, list[str]] = defaultdict(list)
    for e in entities:
        by_type[e.entity_type.value].append(e.id)

    for entity_type, ids in by_type.items():
        # Only connect within reasonably small groups to avoid O(n²) blowup
        sample = ids[:30]
        for i in range(len(sample)):
            for j in range(i + 1, min(i + 5, len(sample))):
                src, tgt = sample[i], sample[j]
                if G.has_node(src) and G.has_node(tgt) and not G.has_edge(src, tgt):
                    G.add_edge(src, tgt, weight=0.3, relation_type="same_category")


def compute_centralities(G: nx.Graph) -> dict[str, dict[str, float]]:
    """Compute degree, betweenness and PageRank centralities."""
    if G.number_of_nodes() == 0:
        return {"degree": {}, "betweenness": {}, "pagerank": {}}

    degree = nx.degree_centrality(G)

    if G.number_of_nodes() > 2:
        betweenness = nx.betweenness_centrality(G, normalized=True, weight="weight")
    else:
        betweenness = {n: 0.0 for n in G.nodes()}

    if G.number_of_edges() > 0:
        pagerank = nx.pagerank(G, alpha=0.85, weight="weight")
    else:
        pagerank = {n: 1.0 / max(G.number_of_nodes(), 1) for n in G.nodes()}

    return {"degree": degree, "betweenness": betweenness, "pagerank": pagerank}


def detect_communities(G: nx.Graph) -> dict[str, int]:
    """Detect communities using greedy modularity maximisation."""
    if G.number_of_nodes() == 0:
        return {}
    if G.number_of_edges() == 0:
        return {n: i for i, n in enumerate(G.nodes())}
    try:
        communities = nx.algorithms.community.greedy_modularity_communities(
            G, weight="weight"
        )
        mapping: dict[str, int] = {}
        for comm_id, community in enumerate(communities):
            for node in community:
                mapping[str(node)] = comm_id
        return mapping
    except Exception:
        return {n: 0 for n in G.nodes()}


def to_graph_data(
    G: nx.Graph,
    centralities: dict[str, dict[str, float]],
    communities: dict[str, int],
) -> GraphData:
    """Serialise NetworkX graph to Vantage GraphData DTO."""
    nodes: list[GraphNode] = []
    for node_id, attrs in G.nodes(data=True):
        entity_type_str = attrs.get("entity_type", "topic")
        try:
            etype = EntityType(entity_type_str)
        except ValueError:
            etype = EntityType.TOPIC

        nodes.append(
            GraphNode(
                id=str(node_id),
                name=attrs.get("name", str(node_id)[:12]),
                entity_type=etype,
                degree=G.degree(node_id),
                betweenness=round(
                    centralities.get("betweenness", {}).get(node_id, 0.0), 4
                ),
                community_id=communities.get(str(node_id), 0),
            )
        )

    edges: list[GraphEdge] = []
    for src, tgt, attrs in G.edges(data=True):
        edges.append(
            GraphEdge(
                source=str(src),
                target=str(tgt),
                weight=round(float(attrs.get("weight", 1.0)), 2),
                relation_type=attrs.get("relation_type", "co_occurs_with"),
            )
        )

    comm_ids = sorted(set(communities.values()))
    comm_names = [f"cluster_{i}" for i in comm_ids]

    # Cap size for API response
    return GraphData(
        nodes=nodes[:300],
        edges=edges[:1000],
        communities=comm_names,
    )
