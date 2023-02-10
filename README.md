<h1 align="center">TiebaSign-贴吧签到助手</h1>


# 使用

## 1.clone 本项目
```bash
git clone https://github.com/wangxso/TiebaSign
go build .
```

## 2.修改配置文件
```bash
cp config.yaml.template config.yaml
nano config.yaml
```
- 添加你的BDUSS
## 3.添加定时任务
```bash
crontab -e
0 8 * * * cd ${your_dir}/TiebaSign/ && ./TiebaSign > /dev/null 2>&1
```

# Feature
[] 添加飞书消息通知
