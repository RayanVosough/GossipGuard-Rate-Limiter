from __future__ import annotations

import asyncio

from app.repositories.rate_limit_repository import DistributedRateLimitRepository


def test_repository_merges_by_node_and_expires_old_records() -> None:
    async def run() -> None:
        repository = DistributedRateLimitRepository(node_id="node-a", window_seconds=10)

        await repository.record_hit("user-1", now=100.0)
        await repository.merge_snapshot(
            {
                "user-1": {
                    "node-b": {"count": 2, "expires_at": 109.0},
                }
            },
            now=100.0,
        )

        assert await repository.current_total("user-1", now=100.0) == 3

        await repository.janitor(now=111.0)
        assert await repository.current_total("user-1", now=111.0) == 0

    asyncio.run(run())
