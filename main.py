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
        self.sleep_timer_task = None

    async def initialize(self):
        """插件初始化时启动后台检查任务 """
        asyncio.create_task(self.auto_sleep_checker())

    async def auto_sleep_checker(self):
        """每分钟检查一次是否满足18小时未睡觉的条件"""
        while True:
            if not self.is_sleeping:
                elapsed = datetime.now() - self.last_wake_up_time
                if elapsed.total_seconds() >= 18 * 3600:
                    logger.info("Bot 已连续工作18小时，准备入睡...")
                    asyncio.create_task(self.start_sleeping())
            await asyncio.sleep(60)

    async def start_sleeping(self, event: AstrMessageEvent = None):
        """执行入睡逻辑"""
        if self.is_sleeping: return
        
        self.is_sleeping = True
        sleep_duration_hours = random.uniform(2, 8)
        
        # 如果是指令触发，给予反馈
        if event:
            yield event.plain_result(f"唔...收到指令了...爱希也要早点休息...我先去睡 {sleep_duration_hours:.1f} 小时...") [cite: 183]
        
        # 启动梦话/翻身的小互动循环
        interaction_task = asyncio.create_task(self.sleep_interactions())
        
        # 等待睡觉时间结束
        await asyncio.sleep(sleep_duration_hours * 3600)
        
        # 醒来
        self.is_sleeping = False
        interaction_task.cancel()
        self.last_wake_up_time = datetime.now()
        logger.info("Bot 已醒来")

    async def sleep_interactions(self):
        """睡觉期间的随机小互动"""
        dreams = ["(砸吧砸吧嘴) 那个...谱面好像...", "Zzz...", "唔...这里的歌词...", "(小声嘀咕) 爱希..."]
        actions = ["(翻了个身，继续沉睡)", "(发出了轻微的呼吸声)", "(扯了扯运动服的领口)"]
        
        while self.is_sleeping:
            # 每 40~90 分钟触发一次
            await asyncio.sleep(random.randint(2400, 5400))
            if self.is_sleeping:
                content = random.choice(dreams + actions)
                # 注意：睡觉状态下主动发消息需要特定逻辑，这里建议记录在日志或发送到特定群组
                logger.info(f"Bot 正在说梦话: {content}")

    @filter.command("我要你睡觉")
    async def force_sleep(self, event: AstrMessageEvent):
        """管理员指令强制入睡 """
        # 这里可以加入权限校验逻辑
        async for result in self.start_sleeping(event):
            yield result

    # 替换掉原来的 @filter.on_event() 部分
    async def on_event(self, event: AstrMessageEvent):
        """监听所有事件的钩子"""
        if self.is_sleeping:
            # 排除掉唤醒指令，防止死锁
            # 这里的判断可以根据你实际的指令前缀来改，比如 /醒醒
            if event.message_str.strip() == "/醒醒":
                self.is_sleeping = False
                # 注意：在 on_event 钩子里通常使用 yield 发送
                yield event.plain_result("...诶？被吵醒了...早安...")
                return
                
            # 正在睡觉时，拦截其他所有消息
            event.stop_event()

    async def terminate(self):
        """销毁时清理任务 """
        if self.sleep_timer_task:
            self.sleep_timer_task.cancel()
