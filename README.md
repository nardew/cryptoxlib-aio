# cryptolib-aio 1.1.0

[![](https://img.shields.io/badge/python-3.6-blue.svg)](https://www.python.org/downloads/release/python-365/) [![](https://img.shields.io/badge/python-3.7-blue.svg)](https://www.python.org/downloads/release/python-374/)

`cryptolib-aio` is a compact Python library providing access to API of selected crypto exchanges.

`cryptolib-aio` is designed as an asynchronous library utilizing modern features of Python and those of supporting asynchronous libraries (mainly [async websockets](https://websockets.readthedocs.io/en/stable/) and [aiohttp](https://aiohttp.readthedocs.io/en/stable/)).

### Main mission
Today there are numerous existing libraries targeting similar audience as `cryptolib-aio`. In order to achieve the broadest coverage of exchanges the supported API is often limited, the most apparent example being lack of _websockets_.  

The mission of `cryptolib-aio` is to:

- serve as a single entry point for various crypto exchanges
- provide full REST API as well as full implementation of exchange's _**websockets**_

Full support of websockets is the corner stone of `cryptolib-aio` which attempts to set `cryptolib-aio` apart from existing solutions which either do not provide websocket support or do not provide it for free.

You will also find out that our subject of interest are often smaller exchanges (by world standards) not enjoying a seat in the mainstream crypto libraries.

Disclaimer: By no means we are suggesting that existing libraries are inferior to `cryptolib-aio`, they just appeal to different endusers.

### Features
- access to REST API as well as full support of websockets for selected exchanges (given websockets are provided by the exchange)
- automatic connection management (reconnecting after remote termination, ...)
- bundling of channels 
- lean architecture making it straightforward to implement API of a new exchange
- fully asynchronous design aiming for the best performance

For the history of changes see [CHANGELOG](https://github.com/nardew/bitpanda-aio/blob/master/CHANGELOG.md).

### List of supported exchanges

As mentioned earlier, all exchanges listed below include full support for websockets.

| Name | Docs |
| --- | --- |
| ![bibox](https://user-images.githubusercontent.com/51840849/77257418-3262b000-6c85-11ea-8fb8-20bdf20b3592.jpg) | [API](https://binance-docs.github.io/apidocs/spot/en/#change-log) |
| ![bibox_europe](https://raw.githubusercontent.com/nardew/cryptolib-aio/docu/images/bibox_europe.png) | [API](https://binance-docs.github.io/apidocs/spot/en/#change-log) |
| ![binance](https://user-images.githubusercontent.com/1294454/29604020-d5483cdc-87ee-11e7-94c7-d1a8d9169293.jpg) | [API](https://binance-docs.github.io/apidocs/spot/en/#change-log) | 
| ![bitforex](https://user-images.githubusercontent.com/1294454/44310033-69e9e600-a3d8-11e8-873d-54d74d1bc4e4.jpg) | [API](https://binance-docs.github.io/apidocs/spot/en/#change-log) |
| ![bitpanda](https://raw.githubusercontent.com/nardew/cryptolib-aio/docu/images/bitpanda.png) | [API](https://binance-docs.github.io/apidocs/spot/en/#change-log) |
| ![liquid](https://user-images.githubusercontent.com/1294454/45798859-1a872600-bcb4-11e8-8746-69291ce87b04.jpg) | [API](https://binance-docs.github.io/apidocs/spot/en/#change-log) |

Unlike REST API which is rather uniform across crypto exchanges websockets are often very exchange-specific and hence very time consuming to implement (which is the reason why they are not offered so broadly). Therefore `cryptolib-aio` comes at the cost of the number of exchanges it covers. This is in line with our ideology quality over quantity.

The list of supported exchanges will grow without any specific pattern, usually driven by personal needs. If there is a high demand for a new exchange to be added, there is a high chance for it to happen (but not guranteed). For business related inquiries concerning customized changes tailored for the client please reach out via e-mail mentioned in the contacts.

### Installation
```bash
pip install cryptolib-aio
```

### Examples

Examples for every exchange can be found in the folder `examples`.

### Contact

- to report issues, bugs, docu corrections or to propose new features use preferably Github Issues
- for topics requiring more personal approach feel free to send an e-mail to <img src="http://safemail.justlikeed.net/e/8701dfa9bd62d1de196684aa746f9d32.png" border="0" align="absbottom">

### Support

If you like the library and you feel like you want to support its further development, enhancements and bugfixing, then it will be of great help and most appreciated if you:
- file bugs, proposals, pull requests, ...
- spread the word
- donate an arbitrary tip
  * `BTC`: `15JUgVq3YFoPedEj5wgQgvkZRx5HQoKJC4`
  * `ETH`: `0xf29304b6af5831030ba99aceb290a3a2129b993d`
  * `ADA`: `DdzFFzCqrhshyLV3wktXFvConETEr9mCfrMo9V3dYz4pz6yNq9PjJusfnn4kzWKQR91pWecEbKoHodPaJzgBHdV2AKeDSfR4sckrEk79`
  * `XRP`: `rhVWrjB9EGDeK4zuJ1x2KXSjjSpsDQSaU6` **+ tag** `599790141`
