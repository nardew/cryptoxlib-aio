# Changelog

All notable changes to this project will be documented in this file.

The project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Pending release]

## [3.2.0] - 2020-04-19

### Added

- `AAX` exchange added

### Changed

- `BTSE`'s `get_exchange_info` now supports mode to return info for all pairs and not just for the selected one
- Fixed: `BTSE` websockets are not losing connection when inactive

## [3.1.0] - 2020-04-10

### Added

- `BTSE` exchange added
- New unit tests for `bitpanda` and `bitforex`

### Changed

- Fixed: `bitvavo` callback invocation

## 3.0.0 - 2020-03-31

The official release of `cryptoxlib-aio`.

[Pending release]: https://github.com/nardew/cryptoxlib-aio/compare/3.2.0...HEAD
[3.2.0]: https://github.com/nardew/cryptoxlib-aio/compare/3.1.0...3.2.0
[3.1.0]: https://github.com/nardew/cryptoxlib-aio/compare/3.0.0...3.1.0
