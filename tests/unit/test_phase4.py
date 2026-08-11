from faccp_common.replication.crdt import GCounter, LWWRegister, MVRegister, ORSet, PNCounter
from faccp_common.replication.regions import Region, RegionHealth, RegionManager, RegionStatus
from faccp_common.replication.vector_clock import VectorClock


def test_crdt_counters_converge_after_bidirectional_merge():
    east = GCounter(node_id="us-east")
    west = GCounter(node_id="us-west")
    east.increment(3)
    west.increment(2)

    east.merge(west)
    west.merge(east)

    assert east.value() == 5
    assert west.value() == 5

    stock_east = PNCounter(node_id="us-east")
    stock_west = PNCounter(node_id="us-west")
    stock_east.increment(10)
    stock_west.decrement(4)

    stock_east.merge(stock_west)
    stock_west.merge(stock_east)

    assert stock_east.value() == 6
    assert stock_west.value() == 6


def test_orset_preserves_concurrent_add_when_other_region_removes_observed_tag():
    east = ORSet(node_id="us-east")
    west = ORSet(node_id="us-west")
    east.add("tenant:acme")
    west.merge(east)

    east.add("tenant:acme")
    west.remove("tenant:acme")

    east.merge(west)
    west.merge(east)

    assert east.value() == {"tenant:acme"}
    assert west.value() == {"tenant:acme"}


def test_registers_resolve_conflicts_deterministically_or_preserve_versions():
    east = LWWRegister(node_id="us-east")
    west = LWWRegister(node_id="us-west")
    east.set({"theme": "blue"})
    west.set({"theme": "green"})

    east.merge(west)
    west.merge(east)

    assert east.value() == west.value()

    mv_east = MVRegister(node_id="us-east")
    mv_west = MVRegister(node_id="us-west")
    mv_east.set({"limit": 10})
    mv_west.set({"limit": 20})
    mv_east.merge(mv_west)

    assert {"limit": 10} in mv_east.value()
    assert {"limit": 20} in mv_east.value()


def test_vector_clock_detects_causal_and_concurrent_events():
    east = VectorClock("us-east")
    west = VectorClock("us-west")

    east.tick()
    west.tick()

    assert east.concurrent_with(west)

    east.observe(west)

    assert east.dominates(west)
    assert not east.concurrent_with(west)


def test_region_manager_prefers_explicit_healthy_region_then_lowest_latency():
    east = Region("us-east", "US East", "http://east", is_primary=True, priority=10)
    west = Region("us-west", "US West", "http://west", priority=20)
    manager = RegionManager([east, west])
    manager.health = {
        "us-east": RegionHealth("us-east", RegionStatus.HEALTHY, 120, 1),
        "us-west": RegionHealth("us-west", RegionStatus.HEALTHY, 40, 1),
    }

    assert manager.get_preferred_region({"preferred_region": "us-east"}).code == "us-east"
    assert manager.get_preferred_region().code == "us-west"

