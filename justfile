publish:
    #!/usr/bin/env bash
    set -euxo pipefail
    VERSION=`sed -En 's/version[[:space:]]*=[[:space:]]*"([^"]+)"/\1/p' Cargo.toml | head -1`
    cargo clippy
    cargo publish
    g at v${VERSION}
