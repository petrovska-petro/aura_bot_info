import requests
from pycoingecko import CoinGeckoAPI

from brownie import Contract
from helpers.addresses import r

from utils.blame_ref import blame_timestamp
from utils.subgraph import (
    TVL_QUERY,
    BALANCER_SUBGRAPH,
    POOL_ID_DIGG,
    POOL_ID_AURABAL_GRAVIAURA,
)


async def _graviaura_breakdown(ctx):
    aura_price = CoinGeckoAPI().get_price(["aura-finance"], "usd")["aura-finance"][
        "usd"
    ]
    graviaura = Contract(r.sett_vaults.graviAURA)
    ppfs = graviaura.getPricePerFullShare() / 1e18
    total_supply_graviaura = graviaura.totalSupply()

    graviaura_badger_controlled_naked = (
        graviaura.balanceOf(r.badger_wallets.treasury_ops_multisig)
        + graviaura.balanceOf(r.badger_wallets.treasury_vault_multisig)
        + graviaura.balanceOf(r.badger_wallets.treasury_voter_multisig)
    )

    response_tvl_digg = requests.post(
        BALANCER_SUBGRAPH,
        json={"query": TVL_QUERY, "variables": {"pool_id": POOL_ID_DIGG}},
    ).json()
    tvl_digg = float(response_tvl_digg["data"]["pool"]["totalLiquidity"])
    digg_pool = Contract(r.balancer.bpt_40wbtc_40digg_20graviaura)
    rewards_digg_pool = Contract("0x10Ca519614b0F3463890387c24819001AFfC5152")
    graviaura_badger_controlled_in_pool = (
        tvl_digg
        * (
            rewards_digg_pool.balanceOf(r.badger_wallets.treasury_vault_multisig)
            / digg_pool.totalSupply()
        )
        * 0.2
        / (aura_price * ppfs)
    )

    graviaura_treasury_dollar_exp = "${:.2f}".format(
        (graviaura_badger_controlled_naked / 1e18 + graviaura_badger_controlled_in_pool)
        * ppfs
        * aura_price
    )

    await ctx.send(blame_timestamp())
    await ctx.send(
        f"graviAURA Badger treasury controlled naked: {graviaura_badger_controlled_naked / 1e18}"
    )
    await ctx.send(
        f"graviAURA Badger treasury controlled in digg pool: {graviaura_badger_controlled_in_pool}"
    )
    await ctx.send(
        f"graviaAURA pct owned by BADGER treasury:  {'{0:.2%}'.format(((graviaura_badger_controlled_naked+ graviaura_badger_controlled_in_pool * 1e18)/ total_supply_graviaura))}"
    )
    await ctx.send(
        f"Treasury graviAURA expressed in dollar denomination: {graviaura_treasury_dollar_exp}"
    )

    total_graviaura_in_digg_pool = tvl_digg * 0.2 / (aura_price * ppfs)
    response_tvl_aurabal_graviaura = requests.post(
        BALANCER_SUBGRAPH,
        json={"query": TVL_QUERY, "variables": {"pool_id": POOL_ID_AURABAL_GRAVIAURA}},
    ).json()
    tvl_aurabal_graviaura = float(
        response_tvl_aurabal_graviaura["data"]["pool"]["totalLiquidity"]
    )
    total_graviaura_in_aurabal_pool = (
        tvl_aurabal_graviaura * 0.3334 / (aura_price * ppfs)
    )

    await ctx.send(f"graviAURA in digg pool: {total_graviaura_in_digg_pool}")
    await ctx.send(f"graviAURA in auraBAL pool: {total_graviaura_in_aurabal_pool}")
    await ctx.send(
        f"Pooled graviaura pct of total supply: {'{0:.2%}'.format(((total_graviaura_in_digg_pool * 1e18+ total_graviaura_in_aurabal_pool * 1e18)/ total_supply_graviaura))}"
    )
    await ctx.send(
        f"Fees from pool graviaura(10%): {total_graviaura_in_digg_pool*.1+total_graviaura_in_aurabal_pool*.1}"
    )

    naked_graviaura = (
        total_supply_graviaura
        - total_graviaura_in_digg_pool * 1e18
        - total_graviaura_in_aurabal_pool * 1e18
        - graviaura_badger_controlled_naked
    )

    fees_from_naked = (naked_graviaura / 1e18) * 0.1

    await ctx.send(f"Naked graviAURA:: {naked_graviaura / 1e18}")
    await ctx.send(
        f"Naked graviaura pct of total supply: {'{0:.2%}'.format((naked_graviaura / total_supply_graviaura))}"
    )
    await ctx.send(f"Fees from naked graviAURA(10%): {fees_from_naked}")
