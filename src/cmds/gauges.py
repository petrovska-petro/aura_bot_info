import requests
from pycoingecko import CoinGeckoAPI

from brownie import Contract
from helpers.addresses import r

from utils.blame_ref import blame_timestamp
from utils.subgraph import (
    TVL_QUERY,
    BALANCER_SUBGRAPH,
    POOL_ID_BADGER,
    POOL_ID_GRAVIAURA,
    POOL_ID_DIGG,
)
from utils.ecosystem_values import BALANCER_WEEKLY_EMISSION, WEEKS_PER_YEAR


async def _gauges_info(ctx):
    # coingecko prices
    bal_price = CoinGeckoAPI().get_price(["balancer"], "usd")["balancer"]["usd"]

    # gauges contracts
    gauge_controller = Contract(r.balancer.gauge_controller)
    gauge_badger = Contract(r.balancer.B_20_BTC_80_BADGER_GAUGE)
    gauge_graviaura = Contract(r.balancer.B_33_GRAVIAURA_33_AURBAL_33_WETH_GAUGE)
    gauge_digg = Contract(r.balancer.B_40WBTC_40DIGG_20GRAVIAURA_GAUGE)

    # pools contracts
    badger_pool = Contract(r.balancer.B_20_BTC_80_BADGER)
    graviaura_pool = Contract(r.balancer.B_33_GRAVIAURA_33_AURBAL_33_WETH)
    digg_pool = Contract(r.balancer.bpt_40wbtc_40digg_20graviaura)

    # working supplies & total supply of pool
    working_supply_badger_pool = gauge_badger.working_supply() / 1e18
    badger_pool_ts = badger_pool.totalSupply() / 1e18

    working_supply_graviaura_pool = gauge_graviaura.working_supply() / 1e18
    graviaura_pool_ts = graviaura_pool.totalSupply() / 1e18

    working_supply_digg_pool = gauge_digg.working_supply() / 1e18
    digg_pool_ts = digg_pool.totalSupply() / 1e18

    badger_gauge_relative_weight = (
        gauge_controller.gauge_relative_weight(gauge_badger.address) / 1e18
    )
    graviaura_gauge_relative_weight = (
        gauge_controller.gauge_relative_weight(gauge_graviaura.address) / 1e18
    )
    digg_gauge_relative_weight = (
        gauge_controller.gauge_relative_weight(gauge_digg) / 1e18
    )

    response_tvl_badger = requests.post(
        BALANCER_SUBGRAPH,
        json={"query": TVL_QUERY, "variables": {"pool_id": POOL_ID_BADGER}},
    ).json()
    tvl_badger = response_tvl_badger["data"]["pool"]["totalLiquidity"]

    response_tvl_graviaura = requests.post(
        BALANCER_SUBGRAPH,
        json={"query": TVL_QUERY, "variables": {"pool_id": POOL_ID_GRAVIAURA}},
    ).json()
    tvl_graviaura = response_tvl_graviaura["data"]["pool"]["totalLiquidity"]

    response_tvl_digg = requests.post(
        BALANCER_SUBGRAPH,
        json={"query": TVL_QUERY, "variables": {"pool_id": POOL_ID_DIGG}},
    ).json()
    tvl_digg = response_tvl_digg["data"]["pool"]["totalLiquidity"]

    await ctx.send(blame_timestamp())
    await ctx.send(
        f"Current gauge relative weight(badger_pool): {'{0:.3%}'.format(badger_gauge_relative_weight)}. Pool TVL: {'${:,.2f}'.format(float(tvl_badger))}"
    )
    await ctx.send(
        f"Current gauge relative weight(graviaura_pool): {'{0:.3%}'.format(graviaura_gauge_relative_weight)}. Pool TVL: {'${:,.2f}'.format(float(tvl_graviaura))}"
    )
    await ctx.send(
        f"Current gauge relative weight(digg_pool): {'{0:.3%}'.format(digg_gauge_relative_weight)}. Pool TVL: {'${:,.2f}'.format(float(tvl_digg))}"
    )

    min_apr_badger = _min_apr(
        working_supply_badger_pool,
        badger_gauge_relative_weight,
        bal_price,
        tvl_badger,
        badger_pool_ts,
    )

    min_apr_graviaura = _min_apr(
        working_supply_graviaura_pool,
        graviaura_gauge_relative_weight,
        bal_price,
        tvl_graviaura,
        graviaura_pool_ts,
    )

    min_apr_digg = _min_apr(
        working_supply_digg_pool,
        digg_gauge_relative_weight,
        bal_price,
        tvl_digg,
        digg_pool_ts,
    )

    # display the min_apr and max_apr
    await ctx.send(
        f"80_BADGER_2O_WBTC -> (min_apr, max_apr) -> ({'{0:.2%}'.format(min_apr_badger)}, {'{0:.2%}'.format(min_apr_badger*2.5)})"
    )
    await ctx.send(
        f"33_GRAVIAURA_33_AURABAL_33_WETH -> (min_apr, max_apr) -> ({'{0:.2%}'.format(min_apr_graviaura)}, {'{0:.2%}'.format(min_apr_graviaura*2.5)})"
    )
    await ctx.send(
        f"40_WBTC_40_DIGG_20_GRAVIAURA -> (min_apr, max_apr) -> ({'{0:.2%}'.format(min_apr_digg)}, {'{0:.2%}'.format(min_apr_digg*2.5)})"
    )


def _min_apr(working_supply, relative_weight, bal_price, tvl, pool_supply):
    # calc ref: https://dev.balancer.fi/resources/vebal-and-gauges/estimating-gauge-incentive-aprs/apr-calculation
    # WITHOUT SWAP FEES APR CONSIDER
    return (
        (0.4 / (working_supply + 0.4))
        * relative_weight
        * BALANCER_WEEKLY_EMISSION
        * WEEKS_PER_YEAR
        * bal_price
    ) / (float(tvl) / pool_supply)
