from pycoingecko import CoinGeckoAPI


async def _display_prices(ctx):
    prices = CoinGeckoAPI().get_price(["aura-finance", "balancer", "badger-dao"], "usd")
    bal_price = prices["balancer"]["usd"]
    aura_price = prices["aura-finance"]["usd"]
    badger_price = prices["badger-dao"]["usd"]

    await ctx.send("Price of ecosystem assets:")
    await ctx.send(f"BAL current price: {'${:.2f}'.format(bal_price)}")
    await ctx.send(f"AURA current price: {'${:.2f}'.format(aura_price)}")
    await ctx.send(f"BADGER current price: {'${:.2f}'.format(badger_price)}")
