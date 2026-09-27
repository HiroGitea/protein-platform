# 贡献指南

## 开发环境

**后端**需要 [uv](https://docs.astral.sh/uv/) 和 Python 3.11+：

```bash
cd backend
uv sync --group dev
uv run uvicorn app.main:app --reload
```

**前端**需要 Node 18+：

```bash
cd frontend
npm install
npm run dev
```

## 提交前检查

CI 会跑这些，本地先过一遍能省时间：

```bash
# 后端
cd backend
uv run ruff check app tests
uv run ruff format --check app tests
uv run pytest

# 前端
cd frontend
npm run lint
npm run check
```

## 新增一个模型引擎

引擎都放在 `backend/app/engines/`，照着 `genmol.py` 写：

1. **写 provider**：继承 `Provider`，设 `kind = "local"` 或 `"remote"`，
   声明 `required_modules`、`checkpoint_name`、`needs_api_key`。
   接口先留着没实现的，设 `implemented = False` 并在 `note` 里写计划。
2. **重型依赖必须延迟导入**——写在方法内部，不要写在模块顶部。
   服务启动时不能 import torch，否则没装 GPU 依赖的用户连 API 都起不来。
3. **实现 `async def run(params, ctx)`**：
   - 阻塞的推理用 `loop.run_in_executor` 丢到线程池，别卡住事件循环
   - 用 `ctx.progress(0.5, "说明")` 报进度
   - 产出的文件用 `ctx.add_file(path)` 注册，前端才能下载
4. **组装引擎**：`Engine("name", local=..., remote=...)`，注册到 `app/engines/__init__.py`。
   在 `app/config.py` 加一个 `<name>_provider` 配置项。
5. 在 `app/schemas.py` 加请求模型，在 `app/routers/tools.py` 加路由。
6. 依赖加到 `pyproject.toml` 的 `[dependency-groups]`，**单独一组**，不要塞进核心依赖。

### 底线：不准返回假数据

这个项目是从一个全是 `setTimeout` + 硬编码结果的原型重写来的。
引擎没就绪就抛 `EngineNotReady` 并说清楚缺什么，
**永远不要为了让页面好看而编造结果**。

## 代码风格

- Python：ruff，行宽 110，类型注解尽量写全
- TypeScript：prettier + eslint，`npm run format`
- 注释和文档用中文，代码标识符用英文
- 提交信息说清楚"改了什么、为什么"，不要只写 `fix`

## 报 issue

请附上 `GET /api/health` 的完整输出，里面有显卡型号、驱动版本、
torch 版本和各引擎的就绪状态，能省掉大量来回。
