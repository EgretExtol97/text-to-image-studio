"""CLI entrypoint: `ttis serve` and `ttis generate`."""
from __future__ import annotations

import argparse
import sys

from text_to_image_studio.bootstrap.runtime import init_runtime
from text_to_image_studio.bootstrap.app import build_app


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ttis", description="text-to-image-studio")
    sub = parser.add_subparsers(dest="cmd", required=True)

    serve = sub.add_parser("serve", help="run the local API server")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8188)

    sub.add_parser("scan", help="rescan models and exit")

    args = parser.parse_args(argv)
    ctx = init_runtime()

    if args.cmd == "scan":
        print(f"discovered {len(ctx.registry.list_ids())} assets")
        return 0

    if args.cmd == "serve":
        import uvicorn

        app = build_app(ctx)
        uvicorn.run(app, host=args.host, port=args.port, log_level="info")
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())