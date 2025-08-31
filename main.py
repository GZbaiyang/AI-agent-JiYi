import streamlit as st
from openai import OpenAI
import random
import httpx

# 页面配置
st.set_page_config(
    page_title="吉伊",
    page_icon="🐾🐾",
    layout="wide"
)

# -------------------------- 全局变量定义 --------------------------
# 吉伊的周边商品数据
merchandise = [
    {"name": "吉伊毛绒公仔", "price": "89元", "image": "image/周边1.png", "desc": "超软萌的吉伊毛绒玩具，可抱可枕～"},
    {"name": "吉伊钥匙扣", "price": "39元", "image": "image/周边2.png", "desc": "挂在书包上超可爱的吉伊钥匙扣♡"},
    {"name": "吉伊手账本", "price": "45元", "image": "image/周边3.png", "desc": "记录日常的吉伊主题手账本～"},
    {"name": "吉伊T恤", "price": "79元", "image": "image/周边4.png", "desc": "穿上就是最萌的吉伊粉丝～"}
]

# 吉伊的角色信息
character_info = {
    "姓名": "吉伊",
    "物种": "神秘小动物",
    "性格": "可爱、纯真、有点小迷糊",
    "爱好": "玩耍、吃零食、晒太阳",
    "口头禅": "吉伊～、哇～、好开心呀♡",
    "好朋友": "哈奇、波奇、米露等"
}

# -------------------------- 会话状态初始化 --------------------------
if 'current_emotion' not in st.session_state:
    st.session_state['current_emotion'] = "happy"
if 'messages' not in st.session_state:
    st.session_state['messages'] = [('ai', '妈妈桑，我是你的吉伊宝宝！')]
if 'game_score' not in st.session_state:
    st.session_state['game_score'] = 0
if 'game_started' not in st.session_state:
    st.session_state['game_started'] = False
if 'game_clicks' not in st.session_state:
    st.session_state['game_clicks'] = 0
if 'start_time' not in st.session_state:
    st.session_state['start_time'] = 0

emotion_images = {
    "happy": "image/吉伊开心.png",
    "sad": "image/吉伊难过.png",
    "surprised": "image/吉伊惊讶.png",
    "angry": "image/吉伊生气.png",
    "sleepy": "image/吉伊困困.png",
    "excited": "image/吉伊兴奋.png"
}

# -------------------------- 函数定义 --------------------------
# LLM调用函数
def get_content_from_llm(client,
                         *,
                         system_prompt='',
                         few_shot_prompt=[],
                         user_prompt='',
                         model_name='deepseek-chat',
                         temperature=0.8,
                         top_p=0.9,
                         frequency_penalty=0.3,
                         presence_penalty=0.5,
                         max_tokens=200,
                         ):
    messages = []
    if system_prompt.strip():
        messages.append({'role': 'system', 'content': system_prompt})
    if few_shot_prompt:
        messages += few_shot_prompt
    if user_prompt.strip():
        messages.append({'role': 'user', 'content': user_prompt})
    try:
        response = client.chat.completions.create(
            model=model_name,
            temperature=temperature,
            top_p=top_p,
            stop='<Bye>',
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            max_tokens=max_tokens,
            messages=messages,
            stream=False
        )
        # 根据回复内容更新表情
        update_emotion_based_on_response(response.choices[0].message.content)
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"API调用失败：{str(e)}")
        return "吉伊正在除草啦～ 吉伊要赚钱给嘛嘛买下广州职业技术大学～♡"

# 根据回复内容更新表情
def update_emotion_based_on_response(response):
    happy_keywords = ["开心", "高兴", "喜欢", "好呀", "真棒", "可爱"]
    sad_keywords = ["难过", "伤心", "不好", "讨厌", "哭"]
    surprised_keywords = ["哇", "惊讶", "居然", "没想到"]
    angry_keywords = ["生气", "讨厌", "不要", "坏"]
    for kw in happy_keywords:
        if kw in response:
            st.session_state['current_emotion'] = "happy"
            return
    for kw in sad_keywords:
        if kw in response:
            st.session_state['current_emotion'] = "sad"
            return
    for kw in surprised_keywords:
        if kw in response:
            st.session_state['current_emotion'] = "surprised"
            return
    for kw in angry_keywords:
        if kw in response:
            st.session_state['current_emotion'] = "angry"
            return

# 获取AI回复
def get_ai_response(client):
    history_messages = []
    for role, content in st.session_state['messages']:
        model_role = 'assistant' if role == 'ai' else role
        history_messages.append({"role": model_role, "content": content})
    system_prompt = (
        "你是日本动漫《吉伊卡哇》中的吉伊，性格可爱、纯真、有点小迷糊，"
        "说话带有撒娇的语气，常用'～'、'♡'等语气词，喜欢用简单的词汇和短句。"
        "回复要充满元气，符合小动物的天真感，记得之前聊过的内容哦～"
    )
    return get_content_from_llm(
        client,
        model_name='deepseek-chat',
        system_prompt=system_prompt,
        few_shot_prompt=[
            {"role": "user", "content": "你好呀"},
            {"role": "assistant", "content": "吉伊来啦～ 你好呀♡"},
            {"role": "user", "content": "今天天气真好"},
            {"role": "assistant", "content": "是呀是呀～ 好想出去玩呢～"}
        ],
        user_prompt=history_messages[-1]['content'] if history_messages else ""
    )

# 随机切换表情的函数
def random_emotion():
    emotions = list(emotion_images.keys())
    st.session_state['current_emotion'] = random.choice(emotions)
    st.success("吉伊的表情变啦～")

# -------------------------- 界面渲染 --------------------------
# 侧边栏配置
with st.sidebar:
    # 简化API配置（固定base_url，预设api_key）
    # st.subheader("")
    # base_url = 'https://api.deepseek.com/'  # 固定为你提供的地址
    # # 预设api_key（保持密码框隐藏，可手动修改）
    # api_key = st.text_input(
    #     label='API Key',
    #     type='password',
    #     value='sk-4207ee7113e445c5bfe64e388e99ef67'  # 预设你提供的密钥
    # )

    # 动态表情切换
    st.subheader("吉伊的心情")
    st.image(emotion_images[st.session_state['current_emotion']], width=100)
    if st.button("让吉伊变个表情～"):
        random_emotion()

    # 吉伊成长记录
    st.header("吉伊的成长记录（相机：dajiang pocket 3）")
    st.subheader("吉伊飞踢")
    st.video("image/吉伊飞踢.mp4")
    st.subheader("吉伊散步")
    st.video("image/吉伊散步.mp4")
    st.subheader("吉伊唱歌")
    st.video("image/吉伊唱歌.mp4")

# 主界面
st.write('# 吉伊(妈妈余涵版) 🐾')

# 顶部标签页
tab1, tab2, tab3, tab4 = st.tabs(["聊天", "吉伊介绍", "互动游戏", "周边商品"])

with tab1:
    # 显示当前表情
    st.image(emotion_images[st.session_state['current_emotion']], width=150)
    # 初始化OpenAI客户端（使用配置的base_url和api_key）
    client = OpenAI(base_url='https://api.deepseek.com/', api_key='sk-4207ee7113e445c5bfe64e388e99ef67')

    # 显示聊天记录
    for role, content in st.session_state['messages']:
        st.chat_message(role).write(content)

    # 处理用户输入
    user_input = st.chat_input()
    if user_input and client:
        st.chat_message('human').write(user_input)
        st.session_state['messages'].append(('human', user_input))
        with st.spinner('吉伊正在思考呢  (((φ(◎ロ◎;)φ))) ～'):
            resp_from_ai = get_ai_response(client)  # 传入client参数
            st.chat_message('assistant').write(resp_from_ai)
            st.session_state['messages'].append(('ai', resp_from_ai))

with tab2:
    st.header("吉伊的小档案 📖")
    col1, col2 = st.columns(2)
    with col1:
        st.image(emotion_images["happy"], width=300)
        st.markdown("""
        <div style="background-color: #FFF0F5; padding: 15px; border-radius: 10px; margin-top: 20px;">
            <h4>吉伊的小秘密</h4>
            <p>• 喜欢吃甜甜的东西～</p>
            <p>• 害怕打雷和黑暗</p>
            <p>• 每天都要睡午觉</p>
            <p>• 会藏小零食在肚子旁边</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        for key, value in character_info.items():
            st.subheader(f"{key}：")
            st.write(f"**{value}**")
        st.subheader("吉伊的日常：")
        st.write("吉伊每天都很开心，喜欢和朋友们一起玩耍。最喜欢在阳光下打滚，"
                 "或者找个舒服的地方睡午觉。遇到困难的时候会有点小慌张，"
                 "但很快就会恢复元气～")
        st.subheader("吉伊的名言：")
        st.info("'不管遇到什么事，只要笑一笑就好啦～♡'")

with tab3:
    st.header("和吉伊一起玩～ 🎈")
    st.divider()
    st.subheader("吉伊的问答小游戏")
    question = st.selectbox(
        "吉伊问你一个问题哦～",
        ["吉伊最喜欢的颜色是什么？", "吉伊害怕什么东西？", "吉伊的好朋友是谁？"]
    )
    answer = st.text_input("你的答案是？")
    if st.button("提交答案"):
        if (question == "吉伊最喜欢的颜色是什么？" and "粉" in answer) or \
           (question == "吉伊害怕什么东西？" and ("雷" in answer or "黑暗" in answer)) or \
           (question == "吉伊的好朋友是谁？" and ("哈奇" in answer or "波奇" in answer)):
            st.success("答对啦～ 吉伊好开心♡")
            st.session_state['current_emotion'] = "excited"
        else:
            st.error("答错了哦～ 再想想看～")
            st.session_state['current_emotion'] = "sad"

with tab4:
    st.header("吉伊的周边商品 🛍️")
    st.write("快来看看可爱的吉伊周边吧～ 每一件都超萌的哦！")
    cols = st.columns(2)
    for i, item in enumerate(merchandise):
        with cols[i % 2]:
            st.image(item["image"], width=200)
            st.subheader(item["name"])
            st.write(f"价格：{item['price']}")
            st.write(item["desc"])
            if st.button(f"想要 {item['name']}～", key=i):
                st.success(f"已加入购物车：{item['name']}")

# 页脚
st.divider()
st.markdown("""
<center>
    <p>吉伊 © 2025.9.1</p>
    <p>妈妈妈妈妈妈无畏契约～</p>
</center>
""", unsafe_allow_html=True)
