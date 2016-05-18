# 饭否小鲸鱼应用

包括：
  - 小鲸鱼
  - 诗词君
  - 短信发饭
  - Kindle 饭

依赖
  - web.py
  - redis

需要在应用中的 store.py 或 view.py 中填入 Consumer，kindle 中的 mail.py 需要填写邮箱信息

因为机器人需要定时抓取数据，task 模仿了 *nux 下的 Crontab，编辑 cron.tab 可添加定时任务，这样运行它

    python code.py 4096

tasks.py 中的 add_task 可添加队列任务，其中的端口对应上面的端口

主文件夹的 code.py 为应用入口，这样运行它
    
    python code.py 8080

其中的端口对应 cron.tab 中的端口

fanfou.py 是饭否 OAuth (XAuth) 模块，可以复用到其他饭否应用中

@home2 http://fanfou.com/home2