from brownie import Contract
from helpers.addresses import r

from utils.blame_ref import blame_timestamp


async def _aura_insight(ctx):
    # leverage .from_explorer pains with special erc20 here
    aura = Contract.from_explorer(r.aura.AURA)

    total_cliffs = aura.totalCliffs()
    cliff_reduction = aura.reductionPerCliff() / 1e18
    aura_total_supply = aura.totalSupply() / 1e18
    init_mint_amount = aura.INIT_MINT_AMOUNT() / 1e18
    # aura minted per bal
    aura_per_bal = (
        (total_cliffs - (aura_total_supply - init_mint_amount) / cliff_reduction) * 2.5
        + 700
    ) / total_cliffs
    current_cliff = (aura_total_supply - init_mint_amount) / cliff_reduction

    await ctx.send(blame_timestamp())
    await ctx.send(f"Aura mint per bal ratio: {aura_per_bal}")
    await ctx.send(
        f"Current cliff: {'{:.3f}'.format(current_cliff)}. Pct of total cliffs completed: {'{0:.3%}'.format(current_cliff/total_cliffs)}"
    )
