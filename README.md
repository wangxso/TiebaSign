<h1 align="center">TiebaSign-贴吧签到助手</h1>


# 使用

## 1.clone 本项目
```bash
git clone https://github.com/wangxso/TiebaSign
chmod 755 start.sh
```
## 2.修改配置文件
```bash
mv config.yaml.template config.yaml
nano config.yaml
```
- 添加你的BDUSS
- 如果你需要通知，我这里仅支持了飞书的
## 3.添加定时任务
```bash
corntab -e
0 8 * * * cd ${your_dir}/TiebaSign/ && bash start.sh > /dev/null 2>&1
```
