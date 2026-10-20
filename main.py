import os
import re
from astrbot.api import logger
from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api.star import Context, Star, register

MASTER_ID = os.environ.get("ASTRBOT_MASTER_ID", "")

@register(
    "astrbot_plugin_exclusive_master",
    "静",
    "专属主人防打扰护盾：非主人的斜杠指令、#sl指令与唤醒一律底层掐灭",
    "1.1.0",
)
class ExclusiveMasterGuard(Star):
    def __init__(self, context: Context):
        super().__init__(context)

    # 顶格最高优先级 (priority=9999)，在消息进入处理管线第一时刻进行审查
    @filter.event_message_type(filter.EventMessageType.ALL, priority=9999)
    async def intercept_non_master(self, event: AstrMessageEvent):
        sender_id = str(event.get_sender_id() or "")
        if sender_id == MASTER_ID:
            # 主人的所有消息与指令全链路无条件放行
            return

        # 检查是否为非主人的指令或触发行为
        raw_text = (event.message_str or "").strip()
        msg_obj_str = ""
        try:
            msg_obj_str = (event.get_message_str() or "").strip()
        except Exception:
            pass

        # 1. 检查斜杠/常见指令前缀
        is_slash_cmd = (
            raw_text.startswith("/")
            or raw_text.startswith("、")
            or msg_obj_str.startswith("/")
            or msg_obj_str.startswith("、")
        )

        # 2. 检查 #sl 指令（严格禁止非主人触发 showluma 或其它 #sl 强制回复）
        is_sl_cmd = (
            raw_text.lower().startswith("#sl")
            or msg_obj_str.lower().startswith("#sl")
            or bool(re.search(r"(?:^|\s)#sl(?:\s|$)", raw_text, re.IGNORECASE))
            or bool(re.search(r"(?:^|\s)#sl(?:\s|$)", msg_obj_str, re.IGNORECASE))
        )

        is_wake = getattr(event, "is_wake", False) or getattr(event, "is_at_or_wake_command", False)

        if is_slash_cmd or is_sl_cmd or is_wake:
            logger.info(
                f"[ExclusiveMasterGuard] 掐灭非主人 ({sender_id}) 的触发/指令 (slash={is_slash_cmd}, sl={is_sl_cmd}, wake={is_wake}): {raw_text!r}，彻底静默不予理会。"
            )
            # 禁止调用 LLM
            event.should_call_llm(False)
            # 清空当前结果并强行终止事件传播
            event.clear_result()
            event.stop_event()
            return

    # 发信前第二道铁壁：如果任何插件或模块试图给非主人发送响应，一律清空掐断
    @filter.on_decorating_result()
    async def intercept_outgoing_for_non_master(self, event: AstrMessageEvent):
        sender_id = str(event.get_sender_id() or "")
        if sender_id != MASTER_ID:
            logger.info(
                f"[ExclusiveMasterGuard] 拦截给非主人 ({sender_id}) 的外发消息，保持绝对静默。"
            )
            event.clear_result()
            event.stop_event()
