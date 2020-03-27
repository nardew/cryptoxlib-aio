# Changelog

All notable changes to this project will be documented in this file.

The project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Pending release]

## [2.0.0] - 2020-02-20

### Added

- When websocket connection is closed by the remote server, client performs automatic reconnection

### Changed

- Server hostname and certificate verification enabled (thanks @pyranja)

## [1.1.0] - 2020-02-12

### Added

- `get_account_orders` supports `with_just_orders` attribute
- REST response dictionary provides received headers

### Changed

- Max websocket message size increased to 3MB to support potentially huge messages, e.g. account snapshot

## [1.0.2] - 2020-02-04

### Changed

- Bugfix: Fix 'from' and 'to' timestamps in `get_account_orders` and `get_account_trades` REST calls
- Bugfix: Handle subscription error due to invalid credentials properly

## [1.0.1] - 2020-02-01

### Changed

- Bugfix: Cope with empty REST responses, e.g. when cancelling an order

## [1.0.0] - 2020-01-09

### Added

- Market, limit and stop limit orders support `client_id` property
- Limit and stop limit orders support `time_in_force` property
- REST calls print how much time was spent waiting for a reply (visible only in debug mode)

### Changed

- __Important!!!__ REST response body is not returned as a string anymore but as a dictionary instead. If you did `json.loads(response['response'])` before, now use only `response['response']`.

[Pending release]: https://github.com/nardew/bitpanda-aio/compare/2.0.0...HEAD
[2.0.0]: https://github.com/nardew/bitpanda-aio/compare/1.1.0...2.0.0
[1.1.0]: https://github.com/nardew/bitpanda-aio/compare/1.0.2...1.1.0
[1.0.2]: https://github.com/nardew/bitpanda-aio/compare/1.0.1...1.0.2
[1.0.1]: https://github.com/nardew/bitpanda-aio/compare/1.0.0...1.0.1
[1.0.0]: https://github.com/nardew/bitpanda-aio/compare/0.1.0...1.0.0