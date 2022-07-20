from brownie import Contract
from helpers.addresses import r

from utils.blame_ref import blame_timestamp

BALANCER_WEEKLY_EMISSION = 145000


async def _general_info(ctx):
    vebal = Contract(r.balancer.veBAL)
    vebal_ts = vebal.totalSupply()

    # how much vebal under AURA control
    vebal_aura_balance = vebal.balanceOf(r.aura.voter_proxy)
    pct_controlled = vebal_aura_balance / vebal_ts

    # lock aura
    vlAURA = Contract(r.aura.vlAURA)
    locked_aura = vlAURA.totalSupply()

    # badger lock aura controlled
    badger_lock_control = vlAURA.getVotes(r.badger_wallets.delegate)

    pct_badger_controls = badger_lock_control / locked_aura
    # emission controlled via aura
    emissions_weekly_control = (
        BALANCER_WEEKLY_EMISSION * pct_controlled * pct_badger_controls
    )

    await ctx.send(blame_timestamp())
    await ctx.send(f"veBAL controlled by Aura: {'{0:.2%}'.format(pct_controlled)}")
    await ctx.send(
        f"Aura lock controlled by BADGER: {'{0:.2%}'.format(pct_badger_controls)}"
    )
    await ctx.send(
        f"BAL emissions controlled by BADGER: {emissions_weekly_control}. In pct of the weekly BAL emitted: {'{0:.2%}'.format(emissions_weekly_control/BALANCER_WEEKLY_EMISSION)}"
    )
