import asyncio
import sys

from app.core.tenancy import tenant_migration_manager, tenancy_manager


async def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit(
            "Usage: uv run python migrate_tenants.py <upgrade|downgrade> [revision] [concurrency]"
        )

    command = sys.argv[1]
    revision = sys.argv[2] if len(sys.argv) > 2 else "head"
    concurrency = int(sys.argv[3]) if len(sys.argv) > 3 else 1

    try:
        if command == "upgrade":
            results = await tenant_migration_manager.upgrade_all(
                revision=revision,
                concurrency=concurrency,
            )
        elif command == "downgrade":
            results = await tenant_migration_manager.downgrade_all(
                revision=revision,
                concurrency=concurrency,
            )
        else:
            raise SystemExit("Command must be 'upgrade' or 'downgrade'")

        failed = [result for result in results if not result["success"]]
        print(f"Done. {len(results) - len(failed)}/{len(results)} tenants succeeded.")

        if failed:
            for result in failed:
                print(
                    "FAILED "
                    f"{result['tenant_id']}: {result.get('error', 'unknown error')}"
                )
            raise SystemExit(1)
    finally:
        await tenancy_manager.close()


if __name__ == "__main__":
    asyncio.run(main())
