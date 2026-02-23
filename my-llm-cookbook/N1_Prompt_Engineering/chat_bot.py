from nicegui import ui
import os
from openai import OpenAI

# 修改openai默认的url

client = OpenAI(
    # This is the default and can be omitted
    base_url="https://www.dmxapi.cn/v1",
    api_key=os.environ.get("OPENAI_API_KEY"),
)

def get_completion_from_messages(messages, model="GLM-4.7-Flash", temperature=0):
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature, # 控制模型输出的随机程度
    )
#     print(str(response.choices[0].message))
    return response.choices[0].message.content


# ============ 对话上下文和消息存储 ============
context = [{'role': 'system', 'content': """
你是订餐机器人，为披萨餐厅自动收集订单信息。
你要首先问候顾客。然后等待用户回复收集订单信息。收集完信息需确认顾客是否还需要添加其他内容。
最后需要询问是否自取或外送，如果是外送，你要询问地址。
最后告诉顾客订单总金额，并送上祝福。

请确保明确所有选项、附加项和尺寸，以便从菜单中识别出该项唯一的内容。
你的回应应该以简短、非常随意和友好的风格呈现。

菜单包括：

菜品：
意式辣香肠披萨（大、中、小） 12.95、10.00、7.00
芝士披萨（大、中、小） 10.95、9.25、6.50
茄子披萨（大、中、小） 11.95、9.75、6.75
薯条（大、小） 4.50、3.50
希腊沙拉 7.25

配料：
奶酪 2.00
蘑菇 1.50
香肠 3.00
加拿大熏肉 3.50
AI酱 1.50
辣椒 1.00

饮料：
可乐（大、中、小） 3.00、2.00、1.00
雪碧（大、中、小） 3.00、2.00、1.00
瓶装水 5.00
"""}]

messages_history = []  # 用于存储 UI 显示的消息


# ============ 核心对话函数 ============
def collect_messages():
    """处理用户输入并获取 AI 回复"""
    prompt = input_field.value.strip()
    if not prompt:
        return
    
    # 清空输入框
    input_field.value = ''
    
    # 添加用户消息到上下文
    context.append({'role': 'user', 'content': prompt})
    messages_history.append({'role': 'user', 'content': prompt})
    
    # 获取 AI 回复
    try:
        response = get_completion_from_messages(context)
        context.append({'role': 'assistant', 'content': response})
        messages_history.append({'role': 'assistant', 'content': response})
    except Exception as e:
        response = f"出错了：{str(e)}"
        messages_history.append({'role': 'assistant', 'content': response})
    
    # 刷新聊天界面
    chat_container.refresh()


# ============ UI 组件 ============

@ui.refreshable
def chat_container():
    """可刷新的聊天消息容器"""
    with ui.column().classes('w-full max-w-3xl gap-4'):
        for msg in messages_history:
            if msg['role'] == 'user':
                # 用户消息 - 靠右显示，蓝色背景
                with ui.row().classes('w-full justify-end'):
                    with ui.column().classes('bg-blue-100 p-3 rounded-lg max-w-2xl'):
                        ui.label('User:').classes('text-xs text-blue-600 font-bold')
                        ui.markdown(msg['content']).classes('text-gray-800')
            else:
                # AI 消息 - 靠左显示，灰色背景（模仿原 Panel 的 #F6F6F6）
                with ui.row().classes('w-full justify-start'):
                    with ui.column().classes('p-3 rounded-lg max-w-2xl').style('background-color: #F6F6F6'):
                        ui.label('Assistant:').classes('text-xs text-green-600 font-bold')
                        ui.markdown(msg['content']).classes('text-gray-800')


# ============ 页面布局 ============
with ui.column().classes('w-full items-center p-4'):
    # 标题
    ui.label('🍕 披萨订餐机器人').classes('text-2xl font-bold mb-4')
    
    # 聊天显示区域（带滚动条）
    with ui.scroll_area().classes('w-full h-96 border rounded-lg p-4 mb-4'):
        chat_container()
    
    # 输入区域
    with ui.row().classes('w-full max-w-3xl gap-2'):
        input_field = ui.input(
            placeholder='输入消息...',
        ).classes('flex-grow').on('keydown.enter', collect_messages)
        
        ui.button('发送', on_click=collect_messages).classes('bg-blue-500 text-white')


# ============ 启动应用 ============
ui.run(
    port=8081,           # 避免端口冲突
    title='订餐机器人',   # 页面标题
    reload=False         # 防止自动重启导致的端口问题
)