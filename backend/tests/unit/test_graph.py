"""Unit tests for graph construction and community detection."""
from __future__ import annotations

import pytest
from vantage.intelligence.graph.builder import (
    build_entity_graph,
    compute_centralities,
    detect_communities,
    to_graph_data,
)
from vantage.models.domain import Entity, EntityType, GraphData


def _make_entity(name: str, etype: EntityType = EntityType.REPOSITORY) -> Entity:
    return Entity(name=name, entity_type=etype, domain="technology")


class TestBuildEntityGraph:
    def test_empty_inputs(self):
        G = build_entity_graph([], [])
        assert G.number_of_nodes() == 0
        assert G.number_of_edges() == 0

    def test_entities_become_nodes(self):
        entities = [_make_entity("repo/a"), _make_entity("repo/b")]
        G = build_entity_graph(entities, [])
        assert G.number_of_nodes() == 2

    def test_explicit_relationship_creates_edge(self):
        a = _make_entity("pkg/alpha")
        b = _make_entity("pkg/beta")
        rel = {
            "source_entity_id": a.id,
            "target_entity_id": b.id,
            "relation_type": "co_occurs_with",
            "weight": 1.0,
        }
        G = build_entity_graph([a, b], [rel])
        assert G.has_edge(a.id, b.id)

    def test_cooccurrence_edges_added_automatically(self):
        entities = [_make_entity(f"repo/{i}") for i in range(10)]
        G = build_entity_graph(entities, [])
        # Co-occurrence logic should add some edges
        assert G.number_of_edges() > 0


class TestComputeCentralities:
    def test_empty_graph(self):
        import networkx as nx
        G = nx.Graph()
        c = compute_centralities(G)
        assert c["degree"] == {}
        assert c["betweenness"] == {}
        assert c["pagerank"] == {}

    def test_all_nodes_have_centrality(self):
        entities = [_make_entity(f"repo/{i}") for i in range(5)]
        G = build_entity_graph(entities, [])
        c = compute_centralities(G)
        for node in G.nodes():
            assert node in c["degree"]

    def test_centrality_values_in_range(self):
        entities = [_make_entity(f"repo/{i}") for i in range(8)]
        G = build_entity_graph(entities, [])
        c = compute_centralities(G)
        for v in c["degree"].values():
            assert 0.0 <= v <= 1.0
        for v in c["betweenness"].values():
            assert 0.0 <= v <= 1.0


class TestDetectCommunities:
    def test_empty_graph(self):
        import networkx as nx
        G = nx.Graph()
        comm = detect_communities(G)
        assert comm == {}

    def test_all_nodes_assigned(self):
        entities = [_make_entity(f"repo/{i}") for i in range(10)]
        G = build_entity_graph(entities, [])
        comm = detect_communities(G)
        for node_id in G.nodes():
            assert str(node_id) in comm

    def test_community_ids_are_integers(self):
        entities = [_make_entity(f"repo/{i}") for i in range(6)]
        G = build_entity_graph(entities, [])
        comm = detect_communities(G)
        for v in comm.values():
            assert isinstance(v, int)


class TestToGraphData:
    def test_returns_graph_data(self):
        entities = [_make_entity(f"repo/{i}") for i in range(5)]
        G = build_entity_graph(entities, [])
        centralities = compute_centralities(G)
        communities = detect_communities(G)
        data = to_graph_data(G, centralities, communities)
        assert isinstance(data, GraphData)
        assert len(data.nodes) == G.number_of_nodes()

    def test_node_names_present(self):
        entities = [_make_entity("test/repo")]
        G = build_entity_graph(entities, [])
        centralities = compute_centralities(G)
        communities = detect_communities(G)
        data = to_graph_data(G, centralities, communities)
        node_names = {n.name for n in data.nodes}
        assert "test/repo" in node_names
