## 插件说明：

[`国产模型kimi`](https://kimi.moonshot.cn/)插件

支持联网、文件解析、20万上下文、卡兹克大佬力荐。



【文件解析】支持的格式如下：

```
['.dot', '.doc', '.docx', '.xls', ".xlsx", ".ppt", ".ppa", ".pptx", ".md", ".pdf", ".txt", ".csv"]
```



【独立上下文】：通过user ID新建会话，测试可多个会话同时进行，请低调使用。



这插件应该不会更新了，就这样了，没有进行压测，估摸着用的人还不多，好用排队去申请API去，别薅国产之光。



## 插件使用：

将`config.json.template`复制为`config.json`，并修改其中`refresh_token`的值。



**`refresh_token`的值怎么获取？登录进去首页或对话页面先挂他个十几分钟，然后F12开发者模式，网络选项，发个信息，找到名称“refresh”的连接，打开响应选项卡，复制“refresh_token”：后面的值就行了**。



### 其他参数说明：

```json
{
    "refresh_token": "", # 看上面
    "file_parsing_prompts": "请帮我整理汇总文件的核心内容", # 文件解析的首次提示词，设置通用点，全局参数
    "keyword": "",  # 关键词触发，留空就全部文本对话都会走插件，插件没有剔除关键词再POST接口，所以弄个正常点的，比如“kimi”
    "reset_keyword": "kimi重置会话", # 相当于网页开个新的窗口对话，没有写会话过期逻辑，懒
    "file_upload": true # 文件解析开关，群聊私聊通通都是他，开就全开，关就全关
}
```

