# coding=utf-8
"""
Author: chazzjimel
Email: chazzjimel@gmail.com
wechat：cheung-z-x

Description:

"""
import time

import plugins
from bridge.context import ContextType
from bridge.reply import Reply, ReplyType
from channel.chat_message import ChatMessage
from plugins import *
from .module.token_manager import tokens, refresh_access_token
from .module.api_models import create_new_chat_session, stream_chat_responses
from .module.file_uploader import FileUploader


@plugins.register(
    name="KimiChat",
    desire_priority=1,
    hidden=True,
    desc="kimi模型对话",
    version="0.1",
    author="chazzjimel",
)
class KimiChat(Plugin):
    def __init__(self):
        super().__init__()
        self.chat_data = {}
        try:
            curdir = os.path.dirname(__file__)
            config_path = os.path.join(curdir, "config.json")
            logger.debug(f"[KimiChat] 加载配置文件{config_path}")
            with open(config_path, "r", encoding="utf-8") as f:
                conf = json.load(f)
            tokens['refresh_token'] = conf.get("refresh_token")
            if not tokens['access_token']:  # 初始化全局access_token
                refresh_access_token()
            self.keyword = conf.get("keyword", "")
            self.reset_keyword = conf.get("reset_keyword", "kimi重置会话")
            self.file_upload = conf.get("file_upload", False)
            self.file_parsing_prompts = conf.get("file_parsing_prompts", "请帮我整理汇总文件的核心内容")
            self.handlers[Event.ON_HANDLE_CONTEXT] = self.on_handle_context
            logger.info("[KimiChat] inited.")
        except Exception as e:
            if isinstance(e, FileNotFoundError):  # 如果是 FileNotFoundError 异常
                logger.warn(f"[KimiChat] init failed, config.json not found.")  # 则输出日志信息，表示配置文件未找到
            else:  # 如果是其他类型的异常
                logger.warn("[KimiChat] init failed." + str(e))  # 则输出日志信息，表示初始化失败，并附加异常信息
            raise e  # 抛出异常，结束程序

    def on_handle_context(self, e_context: EventContext):

        if e_context["context"].type != ContextType.TEXT and e_context["context"].type != ContextType.FILE:
            return
        msg: ChatMessage = e_context["context"]["msg"]
        content = e_context["context"].content.strip()
        user_id = msg.from_user_id
        logger.info(f"[KimiChat] content:{content}, user_id:{user_id}")

        if e_context["context"].type == ContextType.TEXT:
            if self.reset_keyword in content:
                if user_id in self.chat_data:
                    # 如果存在用户信息，删除对应的内容
                    del self.chat_data[user_id]
                    rely_content = "[Kimi] 会话已重置"
                    logger.info(f"[KimiChat] 用户 {user_id} 的聊天数据已重置")
                else:
                    # 如果用户信息不存在，输出提示信息
                    rely_content = "[Kimi] 会话不存在"
                    logger.info(f"[KimiChat] 用户 {user_id} 的聊天数据不存在")
            elif self.keyword == "" or self.keyword in content:
                logger.info(f"[KimiChat] 开始处理文本对话！")
                if user_id in self.chat_data:
                    chat_info = self.chat_data[user_id]
                    chat_id = chat_info['chatid']
                    use_search = chat_info['use_search']
                    rely_content = stream_chat_responses(chat_id, content, use_search=use_search)
                else:
                    chat_id = create_new_chat_session()
                    rely_content = stream_chat_responses(chat_id, content, new_chat=True)
                    self.chat_data[user_id] = {'chatid': chat_id, 'use_search': True}
            else:
                return
        else:
            if self.file_upload:
                if not check_file_format(content):
                    logger.info(f"[KimiChat] 文件格式不支持，PASS！")
                    return
                msg.prepare()
                time.sleep(3)
                if os.path.isfile(content):
                    logger.info(f"[KimiChat] 开始处理文件！")
                    uploader = FileUploader()
                    filename = os.path.basename(content)
                    file_id = uploader.upload(filename, content)
                    refs_list = [file_id]

                    if user_id in self.chat_data:
                        chat_info = self.chat_data[user_id]
                        chat_id = chat_info['chatid']
                        logger.info(f"[KimiChat] 正在获取文件解析回复！")
                        rely_content = stream_chat_responses(chat_id, self.file_parsing_prompts, refs_list, False)
                    else:
                        chat_id = create_new_chat_session()
                        logger.info(f"[KimiChat] 正在获取文件解析回复！")
                        rely_content = stream_chat_responses(chat_id, self.file_parsing_prompts, refs_list, False, True)
                        self.chat_data[user_id] = {'chatid': chat_id, 'use_search': False}
                else:
                    return
            else:
                return

        if not rely_content or rely_content == "":
            rely_content = "Kimi 现在有点累了，晚一点再来问问我吧！您也可以重置会话试试噢！"
            logger.warn(f"[KimiChat] 没有获取到回复内容，请检查！")

        reply = Reply()
        reply.type = ReplyType.TEXT
        reply.content = rely_content
        e_context["reply"] = reply
        e_context.action = EventAction.BREAK_PASS  # 事件结束，并跳过处理context的默认逻辑

    def get_help_text(self, **kwargs):
        help_text = "kimi模型体验插件，支持联网、文件解析、超长上下文"
        return help_text


def check_file_format(file_path):
    _, file_extension = os.path.splitext(file_path)

    # 检查是否为指定的格式
    if file_extension.lower() in ['.dot', '.doc', '.docx', '.xls', ".xlsx", ".ppt", ".ppa", ".pptx", ".md", ".pdf",
                                  ".txt", ".csv"]:
        return True
    else:
        return False
