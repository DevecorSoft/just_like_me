# Just Like Me

如果有一个人懂得你喜恶，陪伴你长久，理解你坚守，分担你忧愁，知道你习惯，跟随你做事，那么这个人何必是家人、朋友、同事，也可以是 “Just Like Me”。

这是一个以人为本的项目。每个人头上的碳基神经网络，拥有远超任何硅基神经网络的判断力。让工具去适应人、沉淀人的习惯，才能把这种判断力真正发挥出来。

---

## 技术定位：Powered by Hindsight

坦率地说，**Just Like Me 本质上是 Hindsight 的套壳**。

我们没有重复造轮子去发明另一套向量检索或记忆图谱。认知与记忆的全部能力——记忆存储 `retain`、多策略检索 `recall`、经验沉淀 `observations` 与心智模型 `mental models`——都来自底层的 **Hindsight**。

Just Like Me 只做最后一公里的工程化：
- **本地常驻与运维**：提供 macOS LaunchAgent 守护进程与本地 PostgreSQL 运行时管理，一键启动并常驻后台。
- **Agent 原生体验**：封装面向 GitHub Copilot CLI 的 `recall-memory` 技能与本地会话回填管线。
- **历史记忆载入**：`just_like_me.load_memory` 从只读的 Copilot 会话存储中批量回填历史对话，按块切分、断点续传，将过去的交互沉淀进记忆库，让"懂你"不必从零开始。
- **心智同步**：将 Hindsight 提炼出的个性化 Mental Model 同步为 Coding Agent 的全局 Instructions，并为后续的行为评测与版本回退建立栅栏。

认知属于 Hindsight，治理与习惯属于你。

项目地址：[DevecorSoft/just_like_me](https://github.com/DevecorSoft/just_like_me)

---

## 数据安全：纯本地运行

在数据安全上，Just Like Me 坚持纯本地化闭环：
- **本地数据存储**：元数据与记忆向量均存储于本地 PostgreSQL 实例（支持 Unix Socket 通信，不暴露公网端口）。
- **本地模型驱动**：支持本地 LLM 与 Embedding 引擎完成提取与检索，数据不离开你的开发机器。

---

## 记忆的边界：跨项目使用的思考

在实际使用中，`recall-memory` 会将过往提炼出的上下文与习惯记忆检索出来并提供给大模型。

这引出一个实际问题：**当开发者切换项目时，过去的记忆是否应当继续存在？**

从一个角度看，AI 就像一个真实的人，换了新项目自然会带着上一段经历中沉淀下的工程习惯和编程直觉；但从团队隔离与数据安全的角度，这确实存在灰色地带。

我们的建议很明确：如果项目涉及严格的隔离要求，切换项目时请清理对应的 Memory Bank，从零开始记录新记忆。掌控权在用户手中。

---

## 结语

让硅基的算力记住细节，让碳基的智慧引领方向。这就是 Just Like Me。

