import discord
from discord import app_commands
from discord.ext import commands

class Core(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="unector", description="Show Unector bot status and enabled modules.")
    async def status(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message(
            embed=discord.Embed(
                title="Unector",
                description="The community bot is online.",
                color=discord.Color.blurple(),
            ).add_field(name="Status", value="Operational", inline=True)
             .add_field(name="Media module", value="Enabled", inline=True)
             .set_footer(text="Unector • Community tools"),
            ephemeral=True,
        )

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Core(bot))
