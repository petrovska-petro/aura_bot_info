from discord.ext import commands

from dotenv import dotenv_values

from utils.network import connect_to_rpc

from cmds.general_info import _general_info
from cmds.display_prices import _display_prices
from cmds.gauges import _gauges_info
from cmds.graviaura_breakdown import _graviaura_breakdown
from cmds.aura_insight import _aura_insight
from cmds.bribe_roi import _bribe_roi_estimation

# make sure we connect rpc prior
connect_to_rpc()

# .env inf
config = dotenv_values(".env")
token = config["BOT_TOKEN"]
guild_id = int(config["GUILD_ID"])

# bot setup
help_command = commands.DefaultHelpCommand(no_category="Commands")
bot = commands.Bot(command_prefix="!", help_command=help_command)


@bot.command()
async def general_info(ctx):
    """
    Displays general metrics around AURA and Badger influence.
    """
    await _general_info(ctx)


@bot.command()
async def prices(ctx):
    """
    Displays prices of BAL, AURA and BADGER.
    """
    await _display_prices(ctx)


@bot.command()
async def gauges_info(ctx):
    """
    Display relevant relative gauge weights and its APR.
    """
    await _gauges_info(ctx)


@bot.command()
async def graviaura_locations(ctx):
    """
    Displays how much is owned by treasury, pooled and naked.
    """
    await _graviaura_breakdown(ctx)


@bot.command()
async def aura_mint_insight(ctx):
    """
    Displays current cliff and ratio of aura mint per bal
    """
    await _aura_insight(ctx)


@bot.command()
async def calc_bribe_roi(ctx, arg1, args2):
    """
    Displays rought estimate ROI of the treasury bribes
    """
    await _bribe_roi_estimation(ctx, arg1, args2)


@calc_bribe_roi.error
async def calc_bribe_roi_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(
            "Missing args bro...Example: <!calc_bribe_roi **proposal_id** **badger_amount_bribed**>"
        )


bot.run(token)
