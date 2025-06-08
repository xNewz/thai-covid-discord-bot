# commands/check_lotto.py

import discord
import aiohttp
from discord.ext import commands


class CheckLotto(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def check_lotto(self, ctx, number: str):
        if not number.isdigit() or len(number) != 6:
            await ctx.send("❌ กรุณากรอกเลข 6 หลัก เช่น `!check_lotto 123456`")
            return

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("https://lotto.api.rayriffy.com/latest") as resp:
                    if resp.status != 200:
                        await ctx.send("❌ ไม่สามารถดึงข้อมูลหวยได้ในขณะนี้")
                        return
                    data = await resp.json()

            response = data.get("response", {})
            prizes = response.get("prizes", [])
            running = response.get("runningNumbers", [])
            matched = []

            # ตรวจรางวัลหลัก
            for prize in prizes:
                if number in prize.get("number", []):
                    reward = int(prize.get("reward", 0))
                    matched.append(f"{prize.get('name')} (฿{reward:,.0f})")

            # ตรวจรางวัลเลขหน้า 3 ตัว
            if len(running) > 0 and number[:3] in running[0].get("number", []):
                reward = int(running[0].get("reward", 0))
                matched.append(f"{running[0].get('name')} (฿{reward:,.0f})")

            # ตรวจรางวัลเลขท้าย 3 ตัว
            if len(running) > 1 and number[3:] in running[1].get("number", []):
                reward = int(running[1].get("reward", 0))
                matched.append(f"{running[1].get('name')} (฿{reward:,.0f})")

            # ตรวจรางวัลเลขท้าย 2 ตัว
            if len(running) > 2 and number[-2:] in running[2].get("number", []):
                reward = int(running[2].get("reward", 0))
                matched.append(f"{running[2].get('name')} (฿{reward:,.0f})")

            embed_color = 0x29AB87 if matched else 0xFF0000
            date_str = response.get("date", "ไม่พบข้อมูลวันที่")
            embed = discord.Embed(
                title="🎉 ผลการตรวจหวย!",
                description=(
                    f"🔢 เลขที่คุณกรอก: **`{number}`**\n"
                    f"🗓️ งวดวันที่: **{date_str}**\n"
                    "━━━━━━━━━━━━━━━━━━━━"
                ),
                color=embed_color,
            )

            if matched:
                embed.add_field(
                    name="🏆 ยินดีด้วย! คุณถูกรางวัล",
                    value="\n".join(f"🎊 **{m}**" for m in matched),
                    inline=False,
                )
            else:
                embed.add_field(
                    name="😢 ไม่ถูกรางวัล",
                    value="ขอให้โชคดีในงวดถัดไปนะครับ 🍀",
                    inline=False,
                )

            embed.set_footer(text="👨‍💻 พัฒนาโดย Pargorn Ruasijan")
            await ctx.send(embed=embed)

        except Exception as e:
            await ctx.send(f"❌ เกิดข้อผิดพลาด: {e}")

async def setup(bot):
    await bot.add_cog(CheckLotto(bot))