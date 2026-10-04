from collections.abc import Callable, Iterator
from datetime import datetime
from typing import Any

import pytest

pytest.importorskip("vnpy_sopt.api", reason="缺少原生扩展")

from vnpy.event import EventEngine  # noqa: E402
from vnpy.trader.constant import (  # noqa: E402
    Direction,
    Exchange,
    Offset,
    OrderType,
    Product,
    Status,
)
from vnpy.trader.object import (  # noqa: E402
    ContractData,
    OrderData,
    OrderRequest,
    PositionData,
    TickData,
)

from vnpy_sopt.api import (  # noqa: E402
    THOST_FTDC_D_Buy,
    THOST_FTDC_OAS_Accepted,
    THOST_FTDC_OAS_Rejected,
    THOST_FTDC_OAS_Submitted,
    THOST_FTDC_OF_Open,
    THOST_FTDC_OPT_LimitPrice,
    THOST_FTDC_OST_AllTraded,
    THOST_FTDC_OST_Canceled,
    THOST_FTDC_OST_NoTradeQueueing,
    THOST_FTDC_OST_PartTradedQueueing,
    THOST_FTDC_PD_Long,
    THOST_FTDC_TC_GFD,
    THOST_FTDC_VC_AV,
)
from vnpy_sopt.gateway import sopt_gateway  # noqa: E402
from vnpy_sopt.gateway.sopt_gateway import (  # noqa: E402
    CHINA_TZ,
    SoptGateway,
    SoptMdApi,
    SoptTdApi,
)


class Sink:
    def __init__(self) -> None:
        self.logs: list[str] = []
        self.ticks: list[TickData] = []
        self.orders: list[OrderData] = []
        self.positions: list[PositionData] = []

    def attach(self, gateway: SoptGateway) -> None:
        gateway.write_log = self.logs.append
        gateway.on_tick = self.ticks.append
        gateway.on_order = self.orders.append
        gateway.on_position = self.positions.append


class CallRecorder:
    def __init__(self) -> None:
        self.calls: list[tuple[str, Any]] = []

    def patch(self, monkeypatch: pytest.MonkeyPatch, api: object, names: list[str]) -> None:
        for name in names:
            monkeypatch.setattr(api, name, self.make_stub(name))

    def make_stub(self, name: str) -> Callable[..., int]:
        def stub(*args: Any) -> int:
            self.calls.append((name, args[0] if args else None))
            return 0
        return stub

    def names(self) -> list[str]:
        return [name for name, _ in self.calls]


TD_METHODS: list[str] = [
    "createFtdcTraderApi",
    "subscribePrivateTopic",
    "subscribePublicTopic",
    "registerFront",
    "init",
    "exit",
    "reqAuthenticate",
    "reqUserLogin",
    "reqQryInstrument",
    "reqOrderInsert",
    "reqOrderAction",
    "reqQryTradingAccount",
    "reqQryInvestorPosition",
]

MD_METHODS: list[str] = [
    "createFtdcMdApi",
    "registerFront",
    "init",
    "exit",
    "reqUserLogin",
    "subscribeMarketData",
]


@pytest.fixture(autouse=True)
def clear_contracts() -> Iterator[None]:
    sopt_gateway.symbol_contract_map.clear()
    yield
    sopt_gateway.symbol_contract_map.clear()


@pytest.fixture
def sink() -> Sink:
    return Sink()


@pytest.fixture
def recorder() -> CallRecorder:
    return CallRecorder()


@pytest.fixture
def gateway(sink: Sink, recorder: CallRecorder, monkeypatch: pytest.MonkeyPatch) -> SoptGateway:
    engine: EventEngine = EventEngine()
    gateway: SoptGateway = SoptGateway(engine, "SOPT")
    sink.attach(gateway)
    recorder.patch(monkeypatch, gateway.td_api, TD_METHODS)
    recorder.patch(monkeypatch, gateway.md_api, MD_METHODS)
    return gateway


@pytest.fixture
def td_api(gateway: SoptGateway) -> SoptTdApi:
    return gateway.td_api


@pytest.fixture
def md_api(gateway: SoptGateway) -> SoptMdApi:
    return gateway.md_api


def add_contract(
    symbol: str = "10004829",
    exchange: Exchange = Exchange.SSE,
    size: int = 10000,
) -> None:
    contract: ContractData = ContractData(
        symbol=symbol,
        exchange=exchange,
        name=symbol,
        product=Product.OPTION,
        size=size,
        pricetick=0.0001,
        gateway_name="SOPT",
    )
    contract.extra = {"trading_active": True}
    sopt_gateway.symbol_contract_map[symbol] = contract


def order_request() -> OrderRequest:
    return OrderRequest(
        symbol="10004829",
        exchange=Exchange.SSE,
        direction=Direction.LONG,
        type=OrderType.LIMIT,
        volume=2,
        price=0.05,
        offset=Offset.OPEN,
    )


def depth_data(**overrides: Any) -> dict[str, Any]:
    data: dict[str, Any] = {
        "InstrumentID": "10004829",
        "UpdateTime": "09:30:00",
        "UpdateMillisec": 500,
        "TradingDay": "20240315",
        "ActionDay": "19990101",
        "ClosePrice": 0,
        "Volume": 10,
        "Turnover": 30000,
        "OpenInterest": 100,
        "LastPrice": 0.05,
        "UpperLimitPrice": 0.08,
        "LowerLimitPrice": 0.02,
        "OpenPrice": 0.045,
        "HighestPrice": 0.055,
        "LowestPrice": 0.04,
        "PreClosePrice": 0.048,
        "BidPrice1": 0.049,
        "AskPrice1": 0.051,
        "BidVolume1": 5,
        "AskVolume1": 6,
        "BidPrice2": 0.048,
        "BidPrice3": 0.047,
        "BidPrice4": 0.046,
        "BidPrice5": 0.045,
        "AskPrice2": 0.052,
        "AskPrice3": 0.053,
        "AskPrice4": 0.054,
        "AskPrice5": 0.055,
        "BidVolume2": 1,
        "BidVolume3": 1,
        "BidVolume4": 1,
        "BidVolume5": 1,
        "AskVolume2": 1,
        "AskVolume3": 1,
        "AskVolume4": 1,
        "AskVolume5": 1,
    }
    data.update(overrides)
    return data


def rtn_order(**overrides: Any) -> dict[str, Any]:
    data: dict[str, Any] = {
        "InstrumentID": "10004829",
        "InsertDate": "20250926",
        "InsertTime": "09:30:00",
        "OrderStatus": THOST_FTDC_OST_NoTradeQueueing,
        "FrontID": 1,
        "SessionID": 2,
        "OrderRef": "7",
        "OrderPriceType": THOST_FTDC_OPT_LimitPrice,
        "TimeCondition": THOST_FTDC_TC_GFD,
        "VolumeCondition": THOST_FTDC_VC_AV,
        "Direction": THOST_FTDC_D_Buy,
        "CombOffsetFlag": THOST_FTDC_OF_Open,
        "LimitPrice": 0.05,
        "VolumeTotalOriginal": 2,
        "VolumeTraded": 0,
        "OrderSysID": "SYS1",
    }
    data.update(overrides)
    return data


def position_data(**overrides: Any) -> dict[str, Any]:
    data: dict[str, Any] = {
        "InstrumentID": "10004829",
        "PosiDirection": THOST_FTDC_PD_Long,
        "YdPosition": 9,
        "TodayPosition": 2,
        "Position": 5,
        "PositionProfit": 12.5,
        "PositionCost": 2500,
        "ShortFrozen": 1,
        "LongFrozen": 4,
    }
    data.update(overrides)
    return data


def test_connect_prefixes_bare_address(gateway: SoptGateway, monkeypatch: pytest.MonkeyPatch) -> None:
    seen: dict[str, str] = {}
    monkeypatch.setattr(gateway.td_api, "connect", lambda *args: seen.__setitem__("td", args[0]))
    monkeypatch.setattr(gateway.md_api, "connect", lambda *args: seen.__setitem__("md", args[0]))

    setting: dict[str, Any] = dict(SoptGateway.default_setting)
    setting["交易服务器"] = "127.0.0.1:41205"
    setting["行情服务器"] = "tcp://127.0.0.1:41213"
    gateway.connect(setting)

    assert seen["td"] == "tcp://127.0.0.1:41205"
    assert seen["md"] == "tcp://127.0.0.1:41213"


def test_send_order_returns_local_id(td_api: SoptTdApi, sink: Sink, recorder: CallRecorder) -> None:
    td_api.frontid = 1
    td_api.sessionid = 2

    vt_orderid: str = td_api.send_order(order_request())

    assert vt_orderid == "SOPT.1_2_1"
    request: dict[str, Any] = recorder.calls[0][1]
    assert recorder.names() == ["reqOrderInsert"]
    assert request["OrderRef"] == "1"
    assert sink.orders[0].orderid == "1_2_1"
    assert sink.orders[0].status == Status.SUBMITTING


@pytest.mark.parametrize(
    ("sopt_status", "vt_status"),
    [
        (THOST_FTDC_OAS_Submitted, Status.SUBMITTING),
        (THOST_FTDC_OAS_Accepted, Status.SUBMITTING),
        (THOST_FTDC_OAS_Rejected, Status.REJECTED),
        (THOST_FTDC_OST_NoTradeQueueing, Status.NOTTRADED),
        (THOST_FTDC_OST_PartTradedQueueing, Status.PARTTRADED),
        (THOST_FTDC_OST_AllTraded, Status.ALLTRADED),
        (THOST_FTDC_OST_Canceled, Status.CANCELLED),
    ],
)
def test_order_status_mapping(td_api: SoptTdApi, sink: Sink, sopt_status: str, vt_status: Status) -> None:
    add_contract()
    td_api.contract_inited = True
    td_api.onRtnOrder(rtn_order(OrderStatus=sopt_status))

    order: OrderData = sink.orders[0]
    assert order.orderid == "1_2_7"
    assert order.status == vt_status
    assert order.direction == Direction.LONG
    assert order.offset == Offset.OPEN
    assert order.type == OrderType.LIMIT
    assert order.datetime == datetime(2025, 9, 26, 9, 30, tzinfo=CHINA_TZ)


def test_position_yd_volume_subtracts_today(td_api: SoptTdApi, sink: Sink) -> None:
    add_contract(size=10000)
    td_api.onRspQryInvestorPosition(position_data(), {}, 1, True)

    position: PositionData = sink.positions[0]
    assert position.exchange == Exchange.SSE
    assert position.direction == Direction.LONG
    assert position.yd_volume == 3
    assert position.volume == 5
    assert position.price == 2500 / (5 * 10000)
    assert position.frozen == 1
    assert position.pnl == 12.5
    assert td_api.positions == {}


def test_combination_symbol_position_uses_sse(td_api: SoptTdApi, sink: Sink) -> None:
    symbol: str = "10004829&10004830"
    add_contract(symbol=symbol, exchange=Exchange.SZSE, size=10000)
    td_api.onRspQryInvestorPosition(
        position_data(InstrumentID=symbol, Position=5, TodayPosition=2),
        {},
        1,
        True,
    )

    assert sink.positions[0].exchange == Exchange.SSE
    assert sink.positions[0].yd_volume == 3
    assert sink.positions[0].volume == 5


def test_empty_position_tail_returns_without_flush(td_api: SoptTdApi, sink: Sink) -> None:
    add_contract()
    td_api.onRspQryInvestorPosition(position_data(), {}, 1, False)
    assert sink.positions == []

    td_api.onRspQryInvestorPosition({}, {}, 1, True)

    assert sink.positions == []
    assert len(td_api.positions) == 1


def test_depth_without_time_is_ignored(md_api: SoptMdApi, sink: Sink) -> None:
    add_contract()
    md_api.onRtnDepthMarketData(depth_data(UpdateTime=""))

    assert sink.ticks == []


def test_depth_without_contract_is_ignored(md_api: SoptMdApi, sink: Sink) -> None:
    md_api.onRtnDepthMarketData(depth_data())

    assert sink.ticks == []


def test_depth_uses_trading_day(md_api: SoptMdApi, sink: Sink) -> None:
    add_contract()
    md_api.onRtnDepthMarketData(depth_data())

    tick: TickData = sink.ticks[0]
    assert tick.exchange == Exchange.SSE
    assert tick.datetime == datetime(2024, 3, 15, 9, 30, 0, 500000, tzinfo=CHINA_TZ)
    assert tick.last_price == 0.05
    assert tick.extra["trading_active"] is True
    assert tick.extra["market_closed"] is False


def test_close_without_connection_does_not_exit(
    td_api: SoptTdApi,
    md_api: SoptMdApi,
    recorder: CallRecorder,
) -> None:
    td_api.close()
    md_api.close()

    assert recorder.calls == []
