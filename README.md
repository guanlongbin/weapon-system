# 武器装备情报查询系统

基于 Vue 3 的纯前端武器装备情报查询系统，支持模糊搜索、卡片式展示和详情弹窗。

**这是一个纯静态项目，没有后端。**

👉 **在线访问：[https://guanlongbin.github.io/weapon-system/](https://guanlongbin.github.io/weapon-system/)**

---

## 预览

![系统预览](图.jpg)

---

## 功能特性

- 模糊搜索
- 卡片式结果展示
- 点击卡片查看详情
- 支持按国家、类型、关键词快速筛选
- 完全静态部署，无需数据库、无需 Python、无需 Node.js
- Vue 3 本地化，无需依赖外部 CDN

---

## 项目结构

```text
weapon-system/
├── index.html              # 主页面（Vue 3 + 搜索逻辑）
├── missiles.json           # 武器数据
├── static/
│   └── vue.global.prod.js  # Vue 3 本地文件
└── images/                 # 武器图片
```

---

## 本地直接打开

如果只是自己看：

1. 下载项目
2. 直接双击 `index.html`
3. 浏览器打开即可

这个项目是静态页，所以**很多情况下甚至不需要服务器**。

---

## 最简单的部署方式

### 方式一：GitHub Pages

适合：想免费上线、最省事。

1. 把代码推到 GitHub 仓库
2. 打开仓库 `Settings`
3. 进入 `Pages`
4. `Source` 选择 `Deploy from a branch`
5. 分支选择 `main`，目录选择 `/(root)`
6. 保存后等待 1 分钟
7. 访问：

```text
https://你的用户名.github.io/weapon-system/
```

---

### 方式二：服务器直接上传

适合：你已经有一台服务器。

你只需要把这些文件上传到网站目录：

- `index.html`
- `missiles.json`
- `static/`
- `images/`

只要能被 Nginx 或其他静态文件服务器访问，就能运行。

---

## 空白服务器从 0 开始

假设你的服务器是全新的 Ubuntu，什么都没有。

### 第一步：安装 Nginx

```bash
sudo apt update
sudo apt install -y nginx
```

安装完成后先测试：

```bash
systemctl status nginx
```

如果看到 `active (running)`，说明成功。

---

### 第二步：准备网站目录

```bash
sudo mkdir -p /var/www/weapon-system
sudo chown -R $USER:$USER /var/www/weapon-system
```

---

### 第三步：上传项目文件

把以下内容上传到 `/var/www/weapon-system/`：

- `index.html`
- `missiles.json`
- `static/`
- `images/`

如果你本地有项目，可以这样传：

```bash
scp -r ./index.html ./missiles.json ./static ./images 用户名@服务器IP:/var/www/weapon-system/
```

---

### 第四步：配置 Nginx

创建配置文件：

```bash
sudo nano /etc/nginx/sites-available/weapon-system
```

写入：

```nginx
server {
    listen 80;
    server_name _;

    root /var/www/weapon-system;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

保存后执行：

```bash
sudo ln -s /etc/nginx/sites-available/weapon-system /etc/nginx/sites-enabled/weapon-system
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl reload nginx
```

---

### 第五步：浏览器访问

打开：

```text
http://你的服务器IP/
```

就可以访问了。

---

## 如果你有域名

把域名解析到服务器 IP 后，把 Nginx 配置中的：

```nginx
server_name _;
```

改成：

```nginx
server_name 你的域名;
```

然后重载：

```bash
sudo nginx -t
sudo systemctl reload nginx
```

---

## 如果要加 HTTPS

安装 certbot：

```bash
sudo apt install -y certbot python3-certbot-nginx
```

执行：

```bash
sudo certbot --nginx -d 你的域名
```

按提示完成即可。

---

## 更新方式

以后每次更新，只需要重新上传这几个静态文件：

- `index.html`
- `missiles.json`
- `static/`
- `images/`

如果只是改了页面，通常只传 `index.html` 就够了。

---

## 说明

这个项目本质上就是一个静态网站，所以部署原则很简单：

- 不需要 Python
- 不需要 Flask
- 不需要数据库
- 不需要安装 Node.js
- 只需要一个能提供静态文件访问的环境

最简单的两种方式就是：

1. GitHub Pages
2. Nginx 静态托管
