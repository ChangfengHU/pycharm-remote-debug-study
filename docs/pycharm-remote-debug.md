# PyCharm Remote Debug（Flask + uv）

本文档说明如何使用 uv 管理运行环境，并通过 Flask Web 应用（端口 5455）触发 PyCharm 的 Remote Debug（IDE 监听 5454）。

## 前置条件
- PyCharm 中创建并启动 "Python Debug Server"：
  - Host: `127.0.0.1`
  - Port: `5454`
  - 点击 Debug 开始监听（状态栏显示 Waiting for connection…）

## 方式 A（推荐，显式传参）
- 启动 IDE 监听：PyCharm Debug Server 端口 5454
- 启动 Web 应用（端口 5455）：

```bash
PYCHARM_REMOTE=1 PYCHARM_REMOTE_HOST=127.0.0.1 PYCHARM_REMOTE_PORT=5454 AUTO_ATTACH_ON_REQUEST=1 \
uv run python -m flask --app app.web run --host 0.0.0.0 --port 5455
```

- 访问以触发连接：

```bash
curl http://127.0.0.1:5455/debug
```

- 或直接访问任意接口（因为设置了 `AUTO_ATTACH_ON_REQUEST=1`）：

```bash
curl http://127.0.0.1:5455/fib/12
```

## 方式 B（不用自动附加，手动触发）
- 启动 Web 应用：

```bash
uv run python -m flask --app app.web run --host 0.0.0.0 --port 5455
```

- 访问以触发附加：

```bash
curl http://127.0.0.1:5455/debug
```

## API 列表
- `GET /`：健康检查
- `GET /debug`：触发远程调试连接（按环境变量连接 IDE 的 5454）
- `GET /fib/<n>`：示例计算接口（可在函数内打断点调试）

## 说明与提示
- Web 应用监听 5455；IDE 监听 5454。数据流为：浏览器 → 5455 → 程序 → 连接 IDE:5454。
- 本机调试请使用 `PYCHARM_REMOTE_HOST=127.0.0.1`。
- 跨机器调试：将 `PYCHARM_REMOTE_HOST` 设置为 PyCharm 所在机器的可达 IP，并开放 5454 入站。
- 若未安装 uv，可使用虚拟环境直接运行（等效于方式 A）：

```bash
PYCHARM_REMOTE=1 PYCHARM_REMOTE_HOST=127.0.0.1 PYCHARM_REMOTE_PORT=5454 AUTO_ATTACH_ON_REQUEST=1 \
./.venv/bin/python -m flask --app app.web run --host 0.0.0.0 --port 5455
```

## 常见问题
- `pydevd_pycharm not found`：请确保环境中已安装（项目已在 `pyproject.toml` 声明，`uv sync` 后使用 `uv run` 启动即可）。
- 连接不上：
  - IDE 是否在 5454 端口监听？
  - 环境变量是否正确（HOST/PORT）？
  - 跨机器是否有防火墙限制？
- 断点未命中：在 `app/web.py` 的 `compute_fibonacci` 或视图函数处设置断点，并重新发起请求。
