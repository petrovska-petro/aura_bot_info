import requests
from pycoingecko import CoinGeckoAPI

from brownie import Contract, network, chain
from helpers.addresses import r

from utils.subgraph import (
    SNAPSHOT_SUBGRAPH,
    PROPOSAL_INFO_QUERY,
    BRIBE_TARGET,
    VOTES_FROM_DELEGATE,
)
from utils.ecosystem_values import BALANCER_WEEKLY_EMISSION

# arg1: it is the proposal_id
# arg2: it is the bribe amount
async def _bribe_roi_estimation(ctx, arg1, args2):
    # two key elements imo
    proposal_id = str(arg1)
    badger_amout = int(args2)

    """
    # This approach takes too long for a bot to be friendly
    # check if treasury already had bribe, otherwise no point in continuing calcs
    aura_bribe = Contract(r.hidden_hands.aura_bribe)
    aura_bribes_events = network.contract.ContractEvents(aura_bribe)
    events = aura_bribes_events.get_sequence(proposal_block_height, chain.height, event_type='DepositBribe')
    """

    # from proposl deduct block height, aura actively voting & votes into our gauge
    response_proposal = requests.post(
        SNAPSHOT_SUBGRAPH,
        json={"query": PROPOSAL_INFO_QUERY, "variables": {"proposal_id": proposal_id}},
    ).json()["data"]["proposal"]
    proposal_block_height = int(response_proposal["snapshot"])
    aura_voting_actively = response_proposal["scores_total"]
    choices = response_proposal["choices"]
    scores = response_proposal["scores"]

    # choices in snap starts on "1"
    target_index = choices.index(BRIBE_TARGET)
    voting_for_badger_pool = scores[target_index]

    await ctx.send(f"Calculations are based on block height: {proposal_block_height}")
    await ctx.send(
        f"From all the active aura voting: {'{0:.3%}'.format(voting_for_badger_pool / aura_voting_actively)} is voting to 80BADGER_20WBTC gauge currently"
    )

    # will seem logical to subtract whatever amount is coming from our delegate voting to this gauge
    # to only consider the real amount of aura lock, which had being attracted by the bribe
    response_delegate_voter = requests.post(
        SNAPSHOT_SUBGRAPH,
        json={
            "query": VOTES_FROM_DELEGATE,
            "variables": {
                "proposal_id": proposal_id,
                "voter_addr": r.badger_wallets.delegate,
            },
        },
    ).json()["data"]["votes"][0]

    print(response_delegate_voter)
    print(str(target_index))
    pct_from_delegate = (
        response_delegate_voter["choice"].get(str(target_index + 1), 0) / 100
    )
    print("pct_from_delegate", pct_from_delegate)
    delegate_voting_for_badger_gauge = response_delegate_voter["vp"] * pct_from_delegate
    print(delegate_voting_for_badger_gauge)
    aura_voting_for_our_bribe = (
        voting_for_badger_pool - delegate_voting_for_badger_gauge
    ) * 1e18

    # badger price from coingecko
    prices = CoinGeckoAPI().get_price(["aura-finance", "balancer", "badger-dao"], "usd")
    bal_price = prices["balancer"]["usd"]
    aura_price = prices["aura-finance"]["usd"]
    badger_price = prices["badger-dao"]["usd"]

    bribe_in_dollar = badger_amout * badger_price

    # Contracts for lock tokens
    vebal = Contract(r.balancer.veBAL)
    vlAURA = Contract(r.aura.vlAURA)
    # leverage from_explorer issues with erc20 interface
    aura = Contract.from_explorer(r.aura.AURA)

    # balancer amount controlled by the weight attracted in the bribe
    total_aura_lock = vlAURA.totalSupply(block_identifier=proposal_block_height)
    pct_active_voting = (aura_voting_actively * 1e18) / total_aura_lock

    aura_vp_control = aura_voting_for_our_bribe / (total_aura_lock * pct_active_voting)

    vebal_aura_controlled = vebal.balanceOfAt(r.aura.voter_proxy, proposal_block_height)
    vebal_total_supply = vebal.totalSupplyAt(proposal_block_height)

    vebal_weight_bribe_attracted = aura_vp_control * vebal_aura_controlled

    vote_captured = vebal_weight_bribe_attracted / vebal_total_supply

    # reward aura contract and gauge
    gauge_badger = Contract(r.balancer.B_20_BTC_80_BADGER_GAUGE)
    reward_badger_aura = Contract(r.aura.B_20_BTC_80_BADGER_REWARD)

    tcl_reward_capture = reward_badger_aura.balanceOf(
        r.badger_wallets.treasury_vault_multisig, block_identifier=proposal_block_height
    ) / reward_badger_aura.totalSupply(block_identifier=proposal_block_height)
    aura_gauge_capture = gauge_badger.balanceOf(
        r.aura.voter_proxy, block_identifier=proposal_block_height
    ) / gauge_badger.totalSupply(block_identifier=proposal_block_height)

    # emissions captured by tcl on this week
    bal_emissions_captured = (
        BALANCER_WEEKLY_EMISSION
        * vote_captured
        * aura_gauge_capture
        * tcl_reward_capture
    )

    # calc ratio of aura minted per bal
    total_cliffs = aura.totalCliffs()
    cliff_reduction = aura.reductionPerCliff() / 1e18
    aura_total_supply = aura.totalSupply() / 1e18
    init_mint_amount = aura.INIT_MINT_AMOUNT() / 1e18
    aura_mint_ratio = (
        (total_cliffs - (aura_total_supply - init_mint_amount) / cliff_reduction) * 2.5
        + 700
    ) / total_cliffs

    # ROI = emissions we get into our tcl / bribe in dollar value
    roi_estimation = (
        bal_emissions_captured * bal_price
        + bal_emissions_captured * aura_mint_ratio * aura_price
    ) / bribe_in_dollar

    await ctx.send(
        f"ROI estimation on bribing {'${:.2f}'.format(bribe_in_dollar)} is {'{0:.3%}'.format(roi_estimation)} for treasury"
    )
