# astrbot_plugin_exclusive_master

**专属主人防打扰护盾** —— 除了主人以外，任何人的斜杠指令、`#sl` 指令或唤醒消息一律在消息管线最底层被掐灭，机器人彻底静默。

## 功能

- **最高优先级拦截**（priority=9999）：在其他任何插件处理之前完成审查，防穿透；
- **三层拦截**：
  1. `/`、`、` 开头的斜杠指令；
  2. `#sl` 系列强制回复指令（含句中出现的，正则全匹配）；
  3. 一切唤醒行为（@ 机器人、唤醒前缀等）；
- **主人无条件放行**：主人的所有消息与指令全链路畅通；
- **彻底静默**：被拦截的消息禁止调用 LLM、清空结果并终止事件传播，不会出现「拒绝了其他人」之类的回复——就是完全不理。

## 适用场景

- 机器人是私人助手，拉进了群但只服务自己；
- 不想让群友白嫖你的 API 额度；
- 讨厌群友用 `/help`、`#sl` 等指令骚扰机器人。

## 安装

```bash
cd /path/to/AstrBot/data/plugins
git clone https://github.com/snlyj/astrbot_plugin_exclusive_master.git
# 重启 AstrBot 或在 WebUI 面板热重载
```

## 配置

### MASTER_ID（必填）

```bash
# 方式一：环境变量
export ASTRBOT_MASTER_ID="你的QQ号"

# 方式二：编辑 main.py 第 6 行
MASTER_ID = "你的QQ号"
```

## 参数说明

| 参数 | 默认值 | 位置 | 说明 |
|------|--------|------|------|
| `MASTER_ID` | 无（必填） | 环境变量 `ASTRBOT_MASTER_ID` 或源码第 6 行 | 唯一被放行的用户 ID |
| `priority=9999` | `9999` | 装饰器参数 | 拦截优先级，保持最高以免被其他插件抢先处理 |

## 使用

无需任何指令，装上即生效：

```
群友A：/help            ← 被掐灭，无任何回复
群友A：@机器人 你好      ← 被掐灭，无任何回复
你：/help               ← 正常执行
你：随便聊天             ← 正常回复
```

## 常见问题

**Q：想放行多个管理员？**
把 `if sender_id == MASTER_ID:` 改成 `if sender_id in {MASTER_ID, "第二个QQ号"}:`。

**Q：日志在哪看？**
拦截行为会记录 INFO 日志：`[ExclusiveMasterGuard] 掐灭非主人 (...)`，在 AstrBot 日志文件或控制台可见。

**Q：和 wake_static 插件什么关系？**
黄金搭档——`exclusive_master` 负责「掐灭别人」，`wake_static` 负责「主人免 @ 唤醒」，两个一起装就是完整的私人专属方案。

## 依赖

- AstrBot v4.x+
- 无第三方 pip 依赖

## License

MIT
