import asyncio
import random
from datetime import datetime, timedelta
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger

@register("sleepy_bot", "宵崎奏", "模拟真实人类睡觉行为的插件", "1.0.0")
class SleepyPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self.is_sleeping = False
        self.last_wake_up_time = datetime.now()

    async def initialize(self):
        """插件初始化时启动后台检查任务"""
        asyncio.create_task(self.auto_sleep_checker())

    async def auto_sleep_checker(self):
        """每分钟检查一次是否满足18小时未睡觉的条件"""
        while True:
            await asyncio.sleep(60)
            if not self.is_sleeping:
                elapsed = datetime.now() - self.last_wake_up_time
                if elapsed.total_seconds() >= 18 * 3600:
                    logger.info("Bot 已连续工作18小时，准备入睡...")
                    # 自动触发入睡不需要传入 event
                    asyncio.create_task(self.run_sleep_cycle())

    async def run_sleep_cycle(self, event: AstrMessageEvent = None):
        """执行完整的睡眠周期逻辑"""
        if self.is_sleeping:
            return
        
        self.is_sleeping = True
        sleep_duration_hours = random.uniform(2, 8)
        
        if event:
            yield event.plain_result(f"唔...熬不住了...先去睡了...预计 {sleep_duration_hours:.1f} 小时后见...")
        
        # 启动睡眠期间的小互动
        interaction_task = asyncio.create_task(self.sleep_interactions())
        
        # 等待睡觉时间结束
        await asyncio.sleep(sleep_duration_hours * 3600)
        
        # 醒来后的清理
        self.is_sleeping = False
        interaction_task.cancel()
        self.last_wake_up_time = datetime.now()
        logger.info("Bot 睡眠结束，已醒来")

    async def sleep_interactions(self):
        """睡觉期间的随机小互动（仅记录日志，若要发消息需额外适配）"""
        dreams = ["(砸吧砸吧嘴) 那个...谱面好像...", "Zzz...", "唔...这里的歌词...", "(小声嘀咕) 爱希..."]
        actions = ["(翻了个身，继续沉睡)", "(发出了轻微的呼吸声)", "(扯了扯运动服的领口)"]
        
        while self.is_sleeping:
            # 每 40~90 分钟触发一次
            await asyncio.sleep(random.randint(2400, 5400))
            if self.is_sleeping:
                content = random.choice(dreams + actions)
                logger.info(f"Bot 正在说梦话: {content}")

    @filter.command
