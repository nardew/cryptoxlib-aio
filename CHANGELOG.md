# Changelog

All notable changes to this project will be documented in this file.

The project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Pending release]

## [5.3.0] - 2022-06-22

### Added

- Python `3.10` supported

## [5.2.3] - 2022-05-31

### Fixed

- `PyJWT` version bumped

## [5.2.2] - 2021-11-22

### Added

- `binance`'s `cancel_all_open_orders(...)` added to spot

## [5.2.1] - 2021-10-07

### Added

- `binance`'s `get_exchange_info(...)` method supports requests for a single symbol, multiple symbols and all symbols

## [5.2.0] - 2021-09-19

### Added

- `coinmate` cryptoexchange added!

## [5.1.6] - 2021-08-23

### Fixed

- `binance` `get_all_open_orders` call for futures can be invoked without any symbol provided

## [5.1.5] - 2021-06-30

### Fixed

- `binance` account websockets renew listen key every 30 minutes
- `binance` websockets send technical ping every 30 seconds

## [5.1.4] - 2021-06-26

### Added

- `bitpanda` supports cancellation of all orders via websockets (`CancelAllOrdersMessage`, `AutoCancelAllOrdersMessage`, `DeactivateAutoCancelAllOrdersMessage`)

### Fixed

- `bitvavo` trades websocket messages routed to callbacks properly

## [5.1.3] - 2021-06-11

### Fixed

- `binance` account websocket implemented for cross and isolated margin account

## [5.1.2] - 2021-06-08

### Fixed

- `binance` `create_margin_order` fixed to work properly with `time in force` for both market and limit orders

## [5.1.1] - 2021-05-26

### Fixed

- `binance` COIN-M futures websockets listen on correct address

## [5.1.0] - 2021-05-25

### Added

- `binance` BSwap (liquidity pools) endpoints
- `binance` leveraged token (BLVT) endpoints 

## [5.0.0] - 2021-05-23

### Added

- `binance` COIN-M futures

### Changed

- due to unification of binance USDS-M and COIN-M futures API, a few signatures of USDS-M futures methods had to be amended (typically parameter `pair` was renamed to `symbol`). Click linked history of the changes to see all updates. 

## [4.1.0] - 2021-05-07

### Added

- proper unsubscription, re-subscription and shutdown of websockets. See `examples/ws_subscriptions.py` for numerous examples.


## [4.0.0] - 2021-04-24

### Added

- `binance` margin and USDS-M futures endpoints

### Changed

- following existing classes, methods and types were renamed:

```
binance.enums.CandelstickInterval -> binance.enums.Interval
binance.BinanceWebsocket.BestOrderBookTickerSubscription -> binance.BinanceWebsocket.OrderBookTickerSubscription
binance.BinanceWebsocket.BestOrderBookSymbolTickerSubscription -> binance.BinanceWebsocket.OrderBookSymbolTickerSubscription
binance.BinanceClient.get_candelsticks -> binance.BinanceClient.get_candlesticks
binance.BinanceClient.get_best_orderbook_ticker -> binance.BinanceClient.get_orderbook_ticker
bitforex.enums.CandelstickInterval -> bitforex.enums.CandlestickInterval
bitvavo.enums.CandelstickInterval -> bitvavo.enums.CandlestickInterval
```

## [3.10.0] - 2021-04-21

### Added

- `bitpanda` supports update of orders via streams (see `BitpandaWebsocket.py:UpdateOrderMessage`)

## [3.9.0] - 2021-03-14

### Added

- testnet endpoints added to `binance`, see `create_binance_testnet_client`
- different API clusters can now be selected in `binance`, see `binance.enums.APICluster`
- `get_best_orderbook_ticker` ticker added to `bitvavo`

## [3.8.1] - 2021-03-14

### Added

- following ticker calls added to the `bitvavo` client: `get_24h_price_ticker`, `get_price_ticker`.

## [3.8.0] - 2021-02-28

### Added

- `eterbase` exchange added

## [3.7.0] - 2021-01-15

### Added

- `bitpanda` REST API supports update of existing orders

## [3.6.1] - 2020-10-05

### Fixed

- `bitpanda` websocket order API supports missing `time_in_force` and `is_post_only` attributes

## [3.6.0] - 2020-09-15

### Added

- dead man's switch added into `bitpanda`

### Fixed

- support for python 3.6

## [3.5.0] - 2020-09-08

### Added

- new REST endpoints (mainly deposits and withdrawals) added into `bitpanda`
- an option to start websockets in a delayed mode (see `CryptoXLibClient.start_websockets(...)`). Useful when server does not support too many websocket connections opened at the same time
- support for `hitbtc`'s duplex websockets including order creation/cancellation

## [3.4.0] - 2020-09-01

### Added

- new `TRADING` subscription added into `bitpanda`
- new `ORDERS` subscription added into `bitpanda`
- additional `Time In Force` options added into `bitpanda`

## [3.3.0] - 2020-08-30

### Added

- `HitBTC` exchange added
-  `candlestick` websocket added into `binance`

## [3.2.1] - 2020-04-29

### Added

- `binance`'s `all market ticker` subscription added 

### Changed

- Fixed: `BTSE` websocket authorization complies with the new authorization handshake

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

[Pending release]: https://github.com/nardew/cryptoxlib-aio/compare/5.3.0...HEAD
[5.3.0]: https://github.com/nardew/cryptoxlib-aio/compare/5.2.3...5.3.0
[5.2.3]: https://github.com/nardew/cryptoxlib-aio/compare/5.2.2...5.2.3
[5.2.2]: https://github.com/nardew/cryptoxlib-aio/compare/5.2.1...5.2.2
[5.2.1]: https://github.com/nardew/cryptoxlib-aio/compare/5.2.0...5.2.1
[5.2.0]: https://github.com/nardew/cryptoxlib-aio/compare/5.1.6...5.2.0
[5.1.6]: https://github.com/nardew/cryptoxlib-aio/compare/5.1.5...5.1.6
[5.1.5]: https://github.com/nardew/cryptoxlib-aio/compare/5.1.4...5.1.5
[5.1.4]: https://github.com/nardew/cryptoxlib-aio/compare/5.1.3...5.1.4
[5.1.3]: https://github.com/nardew/cryptoxlib-aio/compare/5.1.2...5.1.3
[5.1.2]: https://github.com/nardew/cryptoxlib-aio/compare/5.1.1...5.1.2
[5.1.1]: https://github.com/nardew/cryptoxlib-aio/compare/5.1.0...5.1.1
[5.1.0]: https://github.com/nardew/cryptoxlib-aio/compare/5.0.0...5.1.0
[5.0.0]: https://github.com/nardew/cryptoxlib-aio/compare/4.1.0...5.0.0
[4.1.0]: https://github.com/nardew/cryptoxlib-aio/compare/4.0.0...4.1.0
[4.0.0]: https://github.com/nardew/cryptoxlib-aio/compare/3.10.0...4.0.0
[3.10.0]: https://github.com/nardew/cryptoxlib-aio/compare/3.9.0...3.10.0
[3.9.0]: https://github.com/nardew/cryptoxlib-aio/compare/3.8.1...3.9.0
[3.8.1]: https://github.com/nardew/cryptoxlib-aio/compare/3.8.0...3.8.1
[3.8.0]: https://github.com/nardew/cryptoxlib-aio/compare/3.7.0...3.8.0
[3.7.0]: https://github.com/nardew/cryptoxlib-aio/compare/3.6.1...3.7.0
[3.6.1]: https://github.com/nardew/cryptoxlib-aio/compare/3.6.0...3.6.1
[3.6.0]: https://github.com/nardew/cryptoxlib-aio/compare/3.5.0...3.6.0
[3.5.0]: https://github.com/nardew/cryptoxlib-aio/compare/3.4.0...3.5.0
[3.4.0]: https://github.com/nardew/cryptoxlib-aio/compare/3.3.0...3.4.0
[3.3.0]: https://github.com/nardew/cryptoxlib-aio/compare/3.2.1...3.3.0
[3.2.1]: https://github.com/nardew/cryptoxlib-aio/compare/3.2.0...3.2.1
[3.2.0]: https://github.com/nardew/cryptoxlib-aio/compare/3.1.0...3.2.0
[3.1.0]: https://github.com/nardew/cryptoxlib-aio/compare/3.0.0...3.1.0
