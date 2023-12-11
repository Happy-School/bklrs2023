from openfx_api.OpenFxApi import OpenFxApi
from bot.trade_risk_calculator import get_trade_size
from models.trade_decision import TradeDecision

def trade_is_open(pair, api: OpenFxApi):

    open_trades = api.get_open_trades()

    for ot in open_trades:
        if ot.instrument == pair:
            return ot

    return None


def place_trade(trade_decision: TradeDecision, api: OpenFxApi, log_message, log_error, trade_risk):

    open_trade = trade_is_open(trade_decision.pair, api)

    if open_trade is not None:
        log_message(f"Failed to place a trade {trade_decision}, already open: {open_trade}", trade_decision.pair)
        return None

    trade_amount = get_trade_size(api, trade_decision.pair, 
                            trade_decision.loss, trade_risk, log_message)

    trade_id = api.place_trade(
        trade_decision.pair, 
        trade_amount,
        trade_decision.signal,
        trade_decision.sl,
        trade_decision.tp
    )

    if trade_id is None:
        log_error(f"ERROR placing {trade_decision}")
        log_message(f"ERROR placing {trade_decision}", trade_decision.pair)
    else:
        log_message(f"Initiated trade with ID:{trade_id}; Decision: {trade_decision}", trade_decision.pair)


