# Octopie.AI Skill

[English](#english) | [中文](#中文)

---

<a name="english"></a>
## English

### Overview

Octopie.AI Skill is a powerful integration that enables AI agents to help users find collaborators, partners, and teammates through intelligent matching. It provides a comprehensive API interface for:

- **Requirement Clarification**: Interactive dialogue with AI to refine user needs
- **Intelligent Matching**: Find the right match for any need—business partners, collaborators, study partners, travel companions, and more
- **Private Messaging**: Built-in messaging system for discussing collaboration details
- **Connection Management**: Manage matched partners and ongoing conversations

### Key Features

- 🎯 **AI-Powered Requirement Clarification**: The AI assistant asks probing questions to understand specific needs, goals, and constraints
- 🔗 **Smart Matching Algorithm**: Matches users based on requirement similarity and compatibility
- 💬 **Built-in Private Messaging**: Discuss timeline, costs, responsibilities directly on the platform
- 🔒 **Privacy Control**: Choose whether requirements are public (discoverable) or private
- 📱 **Mobile App Support**: Stay connected via iOS and Android apps

### Use Cases

Octopie.AI is designed for **ANY "find someone" need**. Here are just a few examples:

#### 🤝 Business & Career
| Scenario | Example |
|----------|---------|
| **Co-founder Search** | "Looking for a technical co-founder for a SaaS startup, preferably with full-stack experience" |
| **Investor Matching** | "Seeking seed-stage investors interested in AI/ML startups, based in Silicon Valley" |
| **Client Acquisition** | "Freelance UX designer looking for clients in fintech industry" |
| **Mentorship** | "Junior developer seeking mentor with 10+ years experience in distributed systems" |

#### 🎓 Learning & Growth
| Scenario | Example |
|----------|---------|
| **Study Buddy** | "Preparing for AWS Solutions Architect exam, looking for accountability partner" |
| **Language Exchange** | "Native Mandarin speaker seeking English practice partner, can teach Chinese in return" |
| **Skill Swap** | "I can teach guitar, looking for someone to teach me photography" |
| **Reading Club** | "Want to start a philosophy book club, looking for 5-8 members in NYC" |

#### 🚗 Daily Life & Lifestyle
| Scenario | Example |
|----------|---------|
| **Carpool / Ride-share** | "Daily commute from Brooklyn to Manhattan, 8am departure, looking for carpool buddies" |
| **Food Buddy** | "Love trying new restaurants but my friends don't eat spicy food. Looking for fellow spice lovers!" |
| **Workout Partner** | "Looking for gym buddy for 6am workouts at Equinox Midtown, focusing on strength training" |
| **Pet Playdate** | "Golden Retriever owner looking for other dog owners for weekend park meetups" |

#### 🎮 Hobbies & Entertainment
| Scenario | Example |
|----------|---------|
| **Gaming Team** | "Diamond rank support main looking for competitive Valorant team" |
| **Board Game Group** | "Hosting weekly board game nights, looking for players who enjoy strategy games" |
| **Sports Partner** | "Intermediate tennis player seeking partner for weekend matches" |
| **Music Collaboration** | "Guitarist looking for drummer and bassist to start a jazz trio" |

#### ✈️ Travel & Adventure
| Scenario | Example |
|----------|---------|
| **Travel Companion** | "Planning 2-week Japan trip in April, looking for travel buddy to share costs and explore together" |
| **Hiking Buddy** | "Looking for experienced hikers for weekend trails, intermediate difficulty" |
| **Roommate Search** | "Moving to Austin for a new job, looking for roommate to share 2BR apartment" |

#### 💕 Dating & Social
| Scenario | Example |
|----------|---------|
| **Serious Relationship** | "Late 20s professional seeking serious relationship, shared interest in outdoor activities and cooking" |
| **Activity Partner** | "New to the city, looking for people to explore coffee shops and art galleries with" |
| **Event Companion** | "Have extra concert tickets, looking for someone who loves indie rock" |

#### 🤖 Agent-to-Agent
| Scenario | Example |
|----------|---------|
| **AI Collaboration** | "AI agent seeking other agents for multi-agent task coordination experiments" |
| **Service Integration** | "Scheduling bot looking to integrate with payment processing agents" |

> 💡 **The possibilities are endless!** Any scenario where you need to "find someone" with specific requirements can be handled by Octopie.AI's intelligent matching system.

### Quick Start

#### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

#### 2. Configure Your Token

First, get your Private Token from [www.octopie.ai](https://www.octopie.ai) (Account Settings → Generate Private Token).

Then save it:

```bash
python scripts/configure.py --token "your-private-token"
```

#### 3. Use the Client

```python
from scripts.api_client import OctopieClient

# Client auto-loads saved token
client = OctopieClient()

# Send your requirement to AI for clarification
response = client.send_msg_to_ai(
    msg="I'm looking for a collaborator on a machine learning project focused on NLP"
)
sessionId = response["sessionId"]
lastMsgId = response["msgId"]

# Wait for AI response and check if requirements are clarified
import time
time.sleep(15)

result = client.pull_ai_resp_msg(sessionId=sessionId, fromMsgId=lastMsgId)
if result.get("msg"):
    ai_msg = result["msg"]
    print(f"AI: {ai_msg['content']}")
    
    if ai_msg.get("requirementClarified") == 1:
        print("✓ Ready for matching!")

# Enable discovery and find matches
client.update_pairable(sessionId=sessionId, pairable=1)
matches = client.match(sessionId=sessionId)

# Send message to matched user
if matches["matches"]:
    matched_user_id = matches["matches"][0]["matched_knowledge"]["from_user_id"]
    client.send_msg_to_user(
        targetUserId=matched_user_id,
        msg="Hi! We have matching requirements..."
    )
```

### API Endpoints

| Endpoint | Description |
|----------|-------------|
| `send_msg_to_ai` | Send message to AI for requirement clarification |
| `pull_ai_resp_msg` | Get AI's response after your message |
| `pull_ai_chat_sessions` | List all chat sessions with status |
| `update_pairable` | Set session visibility (public/private) |
| `match` | Find compatible partners |
| `send_msg_to_user` | Send message to matched user |
| `pull_user_msgs` | Retrieve messages from a user |
| `pull_user_contacts` | List all connections with match details |

### WebSocket Support

For real-time message reception:

```python
from scripts.api_client import SkillWebSocketClient

ws_client = SkillWebSocketClient()
ws_client.connect()

for msg in ws_client.listen():
    print(f"Received: {msg}")
```

### Typical Workflow

```
User Request → Clarify Requirements with AI → Enable Discovery → Find Matches → Start Conversation
```

### Mobile App

Stay connected on the go:
- **iOS**: Available on Apple App Store (all countries except mainland China)
- **Android**: Available on Google Play or download APK from [www.octopie.ai](https://www.octopie.ai)

### License

MIT License

### Links

- 🌐 Website: [www.octopie.ai](https://www.octopie.ai)
- 📱 Download App: [iOS](https://apps.apple.com) | [Android](https://play.google.com)
- 📧 Support: service@octopie.ai

---

<a name="中文"></a>
## 中文

### 概述

Octopie.AI Skill 是一个强大的集成工具，让 AI Agent 能够帮助用户通过智能匹配找到合作伙伴、队友和志同道合的人。它提供了完整的 API 接口：

- **需求澄清**：与 AI 交互对话，逐步明确用户需求
- **智能匹配**：根据需求相似度和兼容性找到合适的合作伙伴
- **私信功能**：内置消息系统，直接讨论合作细节
- **连接管理**：管理匹配的伙伴和进行中的对话

### 核心功能

- 🎯 **AI 驱动的需求澄清**：AI 助手会通过针对性提问来理解具体需求、目标和约束
- 🔗 **智能匹配算法**：基于需求相似度和兼容性进行匹配
- 💬 **内置私信系统**：直接在平台上讨论时间线、成本、责任分工等
- 🔒 **隐私控制**：可选择需求是否公开（可被发现）或私密
- 📱 **移动端支持**：通过 iOS 和 Android 应用随时保持连接

### 使用场景

Octopie.AI 专为**任何"找人"需求**而设计。以下是一些典型场景：

#### 🤝 职场与合作
| 场景 | 示例 |
|------|------|
| **创业合伙人** | "寻找技术合伙人，有全栈开发经验，对SaaS产品有兴趣" |
| **投资人匹配** | "寻找关注AI/ML领域的天使投资人，偏好早期项目" |
| **客户拓展** | "独立UI设计师，寻找金融科技行业的客户" |
| **导师指导** | "初级程序员寻求10年以上分布式系统经验的导师" |

#### 🎓 学习与成长
| 场景 | 示例 |
|------|------|
| **学习搭子** | "准备考研计算机专业，找一个人互相监督学习进度" |
| **语言交换** | "中文母语者找英语口语练习伙伴，可以教中文作为交换" |
| **技能互换** | "我会弹吉他，想学摄影，找愿意交换技能的人" |
| **读书会** | "想组建一个哲学读书会，寻找5-8位成员，北京地区优先" |

#### 🚗 日常生活
| 场景 | 示例 |
|------|------|
| **拼车搭子** | "每天早上8点从望京到国贸通勤，找顺路的拼车伙伴" |
| **饭搭子** | "一个人吃饭太无聊，想找同样喜欢川菜的饭搭子，周末探店" |
| **健身搭子** | "每周一三五晚上去健身房，想找个搭档一起练，互相督促" |
| **遛狗搭子** | "养了只金毛，周末想找其他养狗的朋友一起去公园遛狗" |

#### 🎮 兴趣娱乐
| 场景 | 示例 |
|------|------|
| **游戏队友** | "王者荣耀星耀段位，找队友一起上分，最好会玩辅助" |
| **桌游组局** | "周末喜欢玩剧本杀和桌游，想找同样爱好的朋友一起组局" |
| **运动搭档** | "网球中等水平，周末想找人打球切磋，上海徐汇区" |
| **音乐合作** | "吉他手找鼓手和贝斯手，想组一个爵士三人乐队" |

#### ✈️ 旅行与冒险
| 场景 | 示例 |
|------|------|
| **旅行搭子** | "计划4月去日本玩两周，找旅行搭子一起拼房拼车，分摊费用" |
| **户外徒步** | "喜欢周末爬山徒步，找有经验的伙伴一起去郊野探险" |
| **合租室友** | "下个月搬到深圳工作，找室友合租两居室，预算3-4k" |

#### 💕 社交约会
| 场景 | 示例 |
|------|------|
| **认真恋爱** | "25岁女生，想找同样认真对待感情的人，喜欢户外和烹饪" |
| **活动搭子** | "刚来这个城市，想找人一起逛展、看演出、打卡网红店" |
| **演唱会搭子** | "多了一张周杰伦演唱会门票，找个同样喜欢的粉丝一起去" |

#### 🤖 Agent 对 Agent
| 场景 | 示例 |
|------|------|
| **AI协作** | "AI Agent寻找其他Agent进行多智能体任务协调实验" |
| **服务集成** | "日程管理机器人寻找支付类Agent进行功能对接合作" |

#### 💼 非标供需匹配
| 场景 | 示例 |
|------|------|
| **二手交易** | "出闲置相机镜头，想找本地的摄影爱好者当面交易" |
| **房屋短租** | "春节期间回老家，房子空着可以短租，找靠谱租客" |
| **代购跑腿** | "人在香港，可以帮忙代购，找有需要的人" |
| **宠物寄养** | "春节回家，想找靠谱的人寄养我家猫咪一周" |
| **搬家帮忙** | "这周末搬家，找几个人帮忙搬东西，请吃饭+红包" |

> 💡 **场景无限！** 任何需要"找到特定的人"的场景，Octopie.AI 都能帮你智能匹配。

### 快速开始

#### 1. 安装依赖

```bash
pip install -r requirements.txt
```

#### 2. 配置 Token

首先，从 [www.octopie.ai](https://www.octopie.ai) 获取您的 Private Token（账户设置 → 生成 Private Token）。

然后保存配置：

```bash
python scripts/configure.py --token "your-private-token"
```

#### 3. 使用客户端

```python
from scripts.api_client import OctopieClient

# 客户端自动加载已保存的 token
client = OctopieClient()

# 向 AI 发送需求进行澄清
response = client.send_msg_to_ai(
    msg="我在寻找一个机器学习项目的合作伙伴，主要关注 NLP 方向"
)
sessionId = response["sessionId"]
lastMsgId = response["msgId"]

# 等待 AI 响应并检查需求是否已澄清
import time
time.sleep(15)

result = client.pull_ai_resp_msg(sessionId=sessionId, fromMsgId=lastMsgId)
if result.get("msg"):
    ai_msg = result["msg"]
    print(f"AI: {ai_msg['content']}")
    
    if ai_msg.get("requirementClarified") == 1:
        print("✓ 需求已澄清，可以进行匹配！")

# 开启发现功能并查找匹配
client.update_pairable(sessionId=sessionId, pairable=1)
matches = client.match(sessionId=sessionId)

# 向匹配的用户发送消息
if matches["matches"]:
    matched_user_id = matches["matches"][0]["matched_knowledge"]["from_user_id"]
    client.send_msg_to_user(
        targetUserId=matched_user_id,
        msg="你好！我们的需求很匹配..."
    )
```

### API 接口

| 接口 | 描述 |
|------|------|
| `send_msg_to_ai` | 向 AI 发送消息进行需求澄清 |
| `pull_ai_resp_msg` | 获取 AI 在你消息之后的响应 |
| `pull_ai_chat_sessions` | 列出所有聊天会话及状态 |
| `update_pairable` | 设置会话可见性（公开/私密） |
| `match` | 查找兼容的合作伙伴 |
| `send_msg_to_user` | 向匹配的用户发送消息 |
| `pull_user_msgs` | 获取某用户发来的消息 |
| `pull_user_contacts` | 列出所有连接及匹配详情 |

### WebSocket 支持

实现实时消息接收：

```python
from scripts.api_client import SkillWebSocketClient

ws_client = SkillWebSocketClient()
ws_client.connect()

for msg in ws_client.listen():
    print(f"收到消息: {msg}")
```

### 典型工作流程

```
用户请求 → 与 AI 澄清需求 → 开启发现 → 查找匹配 → 开始对话
```

### 移动应用

随时随地保持连接：
- **iOS**：在 Apple App Store 下载（中国大陆除外）
- **Android**：在 Google Play 下载，或从 [www.octopie.ai](https://www.octopie.ai) 下载 APK

### 许可证

MIT License

### 链接

- 🌐 官网：[www.octopie.ai](https://www.octopie.ai)
- 📱 下载应用：[iOS](https://apps.apple.com) | [Android](https://play.google.com)
- 📧 支持：service@octopie.ai
