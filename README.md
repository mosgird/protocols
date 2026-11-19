# protocols

Protocol specification for an open-source, end-to-end encrypted chat platform with servers, channels, direct messages and roles.

The relay server stores and forwards ciphertext only. Clients perform all encryption and decryption.

**Status:** specification in draft (v0.1). No client or server implementation exists yet.

**License:** Mulan Permissive Software License, Version 2 (Mulan PSL v2). See [LICENSE](LICENSE).

## Contents

| Path | Description |
|------|-------------|
| [spec/v0.1/overview.md](spec/v0.1/overview.md) | Goals, non-goals, architecture, terminology, message flow |
| [spec/v0.1/open-questions.md](spec/v0.1/open-questions.md) | Unresolved decisions, with options and trade-offs |
| [spec/decisions/0001-relay-based-e2ee.md](spec/decisions/0001-relay-based-e2ee.md) | Decision record: relay server with end-to-end encryption |
| [spec/decisions/0002-signal-for-direct-messages.md](spec/decisions/0002-signal-for-direct-messages.md) | Decision record: Signal protocol design for direct messages |
| [spec/decisions/0003-mls-for-groups.md](spec/decisions/0003-mls-for-groups.md) | Decision record: MLS (RFC 9420) for group chats and channels |
| [test-vectors/README.md](test-vectors/README.md) | Placeholder for test vectors (added with the spec) |
| [client/](client/) | Client implementation (empty; not started) |
| [server/](server/) | Relay server implementation (empty; not started) |
