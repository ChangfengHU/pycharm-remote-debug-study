# 跨主机容器触发本地 PyCharm Remote Debug

场景：Docker 容器运行在另一台主机 `192.168.10.108`，你的 PyCharm 运行在本机 `192.168.10.106`。访问容器的 5455 端口时，让应用回连到你本机 IDE 的 5454 端口进行远程调试。

## 拓扑
- IDE（PyCharm）：`192.168.10.106:5454`（监听）
- 容器宿主：`192.168.10.108`（对外暴露 `5455`）
- 浏览器/客户端：访问 `http://192.168.10.108:5455`

## 步骤 1：配置 PyCharm（在 192.168.10.106）
1. 创建并启动 "Python Debug Server"
   - Host: `0.0.0.0`（确保外部可达；若只在本机调试可以用 `127.0.0.1`）
   - Port: `5454`
   - 点击 Debug 开始监听（状态栏显示 Waiting for connection…）
2. 防火墙/安全策略：放行 5454 入站（至少允许来自 `192.168.10.108`）

## 步骤 2：启动容器（在 192.168.10.108）
只需要调整环境变量，无需修改代码。

### docker run 示例
```bash
docker run -d --name py-demo-web \
  -p 5455:5455 \
  -e AUTO_ATTACH_ON_REQUEST=1 \
  -e PYCHARM_REMOTE=1 \
  -e PYCHARM_REMOTE_HOST=192.168.10.106 \
  -e PYCHARM_REMOTE_PORT=5454 \
  py-demo-project:dev
```
说明：
- `PYCHARM_REMOTE_HOST` 必须写 IDE 机器的 IP（这里为 `192.168.10.106`），不要使用 `host.docker.internal`（那会指向容器宿主 `192.168.10.108`）。
- `AUTO_ATTACH_ON_REQUEST=1` 会在首次请求时自动回连 IDE。

### docker compose（推荐使用 .env 覆盖）
- 在 `192.168.10.108` 上新建 `.env`：
```dotenv
PYCHARM_REMOTE=1
PYCHARM_REMOTE_HOST=192.168.10.106
PYCHARM_REMOTE_PORT=5454
AUTO_ATTACH_ON_REQUEST=1
```
- 启动：
```bash
docker compose --env-file .env up -d web
```

## 步骤 3：触发调试
- 手动触发：
```bash
curl http://192.168.10.108:5455/debug
```
- 或在启用了 `AUTO_ATTACH_ON_REQUEST=1` 后，访问任意接口（例如）：
```bash
curl http://192.168.10.108:5455/fib/12
```

## 连通性自检
- 从容器宿主（192.168.10.108）检查到 IDE（192.168.10.106:5454）：
```bash
nc -vz 192.168.10.106 5454
```
- 从容器内部检查到 IDE（需要临时安装 nc）：
```bash
# 进入容器
docker exec -it py-demo-web bash || docker exec -it py-demo-web sh
# 安装并测试（Debian/Ubuntu 系）
apt-get update >/dev/null 2>&1 || true
apt-get install -y netcat-openbsd >/dev/null 2>&1 || true
nc -vz 192.168.10.106 5454
```

## 常见问题
- IDE 未监听或监听在 127.0.0.1：请在 PyCharm 将 Debug Server 监听地址设为 `0.0.0.0`。
- 防火墙拦截：确认 `192.168.10.106:5454` 对 `192.168.10.108` 可达。
- 写错目标 IP：务必将 `PYCHARM_REMOTE_HOST` 指向 IDE 所在机器（本例为 `192.168.10.106`），而非容器宿主。
- 安全：Debug Server 无认证，仅在可信内网使用；跨网请用 VPN 或安全隧道。

## 摘要
- IDE（106）监听 `0.0.0.0:5454` 并放行端口。
- 容器（108）将 `PYCHARM_REMOTE_HOST` 指向 `192.168.10.106`，应用监听 `5455`。
- 访问 `http://192.168.10.108:5455` 即可触发并回连到本机 PyCharm。