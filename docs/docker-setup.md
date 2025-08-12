# Docker 开发：在容器中触发本地 PyCharm Remote Debug

本说明帮助你使用 Docker 启动 Flask 应用（端口 5455），并在访问时让容器连接回宿主机上的 PyCharm Debug Server（端口 5454）。

## 前置准备
1. 在 PyCharm 中创建并启动 "Python Debug Server"：
   - Host: `0.0.0.0` 或本机 `127.0.0.1`
   - Port: `5454`
   - 点击 Debug 开始监听
2. 确保 Docker 可用（本机已安装 Docker Desktop）

## 构建镜像
```bash
docker build -t py-demo-project:dev .
```

## 运行容器（推荐命令）
容器会在第一次请求时自动附加到宿主机的 PyCharm：
```bash
docker run -d --name py-demo-web \
  -p 5455:5455 \
  -e AUTO_ATTACH_ON_REQUEST=1 \
  -e PYCHARM_REMOTE=1 \
  -e PYCHARM_REMOTE_HOST=host.docker.internal \
  -e PYCHARM_REMOTE_PORT=5454 \
  -e FLASK_ENV=development \
  --add-host host.docker.internal:host-gateway \
  py-demo-project:dev
```

说明：
- `host.docker.internal` 在 macOS/Windows 上默认可用；在 Linux 上通过 `--add-host host.docker.internal:host-gateway` 映射到宿主机。
- IDE 监听端口为 5454，Web 服务对外映射 5455。

## 触发调试
- 访问以触发连接（若未启用 AUTO_ATTACH_ON_REQUEST=1）：
```bash
curl http://127.0.0.1:5455/debug
```
- 或直接访问任意接口（如果启用了 `AUTO_ATTACH_ON_REQUEST=1`）：
```bash
curl http://127.0.0.1:5455/fib/12
```

## 常见问题
- 若容器无法连接 IDE：
  - 确认 IDE 正在 5454 监听
  - Linux 下确认 `--add-host host.docker.internal:host-gateway` 是否生效
  - 防火墙是否允许 5454 入站
- 若断点不命中：在 `app/web.py` 的视图或 `compute_fibonacci` 中放置断点，并重新发起请求。
