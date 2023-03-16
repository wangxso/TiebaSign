# TiebaSign
TiebaSign is a tool that allows users to automatically sign into their Baidu Tieba accounts and perform daily forum sign-ins. It is written in Go and can be easily built and run on any platform that supports the Go programming language.

## Usage
To use TiebaSign, follow these steps:

1. Clone the TiebaSign repository:
```bash
git clone https://github.com/wangxso/TiebaSign
```

2. Build the TiebaSign binary by running:
```bash
go build .
```
3. Modify the configuration file by making a copy of the template file:
```bash
cp config.yaml.template config.yaml
nano config.yaml
```
Add your BDUSS (Baidu User Session Security) token to the configuration file.
4. Add a cron job to run the TiebaSign binary at a scheduled time:

```bash
crontab -e
0 8 * * * cd ${your_dir} && ./tiebasign > /dev/null 2>&1
```
This example cron job will run TiebaSign every day at 8:00 AM.

## Features
 Automatic Baidu Tieba sign-ins
- Feishu message notifications (coming soon)
- Enterprise WeChat robot notifications (coming soon)
Thank you for using TiebaSign! If you have any questions or issues, please feel free to open an issue on the GitHub repository.
