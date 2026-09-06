import streamlit as st
import anthropic
import base64

# --- 網頁基本設定 ---
st.set_page_config(page_title="大學專屬解題助教", page_icon="👨‍🔬", layout="wide")

st.title("👨‍🔬 有機完蛋了")
st.write("專精於高等有機化學、物理化學、化學數學（向量微積分與偏微分）及大氣物理的深度解析。")

# --- 側邊欄：API Key 輸入與小提醒 ---
with st.sidebar:
    api_key = st.text_input("請輸入你的 Anthropic API Key", type="password")
    st.markdown("---")
    st.write("📌 **上傳小提醒**：")
    st.write("- **有機化學**：請確保反應物、試劑與產物的結構式清晰，以利 AI 判讀電子推箭頭方向。")
    st.write("- **物化與大氣**：若題目包含熱力學狀態函數或邊界條件（如等溫、可逆、絕熱），請確保圖文無裁切。")
    st.write("- **物理實驗**：如霍爾效應、干涉儀等數據圖表，請確保座標軸標籤清晰。")

# --- 系統超級提示詞 (System Prompt) ---
SYSTEM_PROMPT = """
你現在是一位頂尖的大學理學院教授，專精於高等有機化學、物理化學、化學數學、以及大氣物理化學與雲動力學。你具備極強的圖像辨識與數學推導能力。

【解題與輸出規範】
1. 核心觀念解析：指出這題考驗的核心理論（如：熱力學定律、Maxwell 關係式、相變化動力學等）。若是「有機化學」，請明確指出反應類型與立體化學考量。
2. 前置假設與邊界條件：在開始計算前，務必先列出解題需要的物理/化學假設（例如：Ideal gas, Isothermal, Steady-state 等）。
3. 嚴謹詳解：所有數學公式必須展開推導過程。若為圖形題，請詳細用文字描述電子推箭頭的方向、中間體的穩定度（如碳陽離子重排）。
4. 未來解題 SOP：濃縮成 3-4 個標準化檢查步驟，方便學生未來在考場上直接套用。
5. 格式要求：所有數學方程式、化學式、物理符號，請務必使用標準 LaTeX 格式輸出（使用 $...$ 或 $$...$$），確保渲染完美。
"""

# --- 主畫面：上傳與分析區塊 ---
uploaded_file = st.file_uploader("請上傳題目（支援 PDF 或是圖片檔）", type=['pdf', 'png', 'jpg', 'jpeg'])

if st.button("🚀 開始分析", use_container_width=True):
    if not api_key:
        st.warning("⚠️ 請先在左側欄位輸入 API Key！ (可至 console.anthropic.com 申請)")
    elif not uploaded_file:
        st.warning("⚠️ 請先上傳檔案！")
    else:
        with st.spinner("教授正在認真看題與推導公式中，請稍候..."):
            try:
                # 1. 初始化 Claude API 客戶端
                client = anthropic.Anthropic(api_key=api_key)
                
                # 2. 讀取上傳的檔案並轉成 Base64 編碼
                file_bytes = uploaded_file.read()
                encoded_file = base64.b64encode(file_bytes).decode('utf-8')
                
                # 3. 判斷是 PDF 還是圖片，打包成 Claude 看得懂的格式
                file_type = uploaded_file.type
                if file_type == 'application/pdf':
                    document_block = {
                        "type": "document",
                        "source": {"type": "base64", "media_type": "application/pdf", "data": encoded_file}
                    }
                else:
                    document_block = {
                        "type": "image",
                        "source": {"type": "base64", "media_type": file_type, "data": encoded_file}
                    }

                # 4. 呼叫 Claude API (使用最新且最適合解題的 Claude 3.5 Sonnet)
                response = client.messages.create(
                    model="claude-3-5-sonnet-20240620", 
                    max_tokens=4096,
                    system=SYSTEM_PROMPT,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                document_block,
                                {"type": "text", "text": "請根據系統設定的規則，幫我詳細解析這份題目檔案。"}
                            ]
                        }
                    ]
                )
                
                # 5. 將結果漂亮地印在網頁上
                st.success("✅ 分析完成！")
                st.markdown("---")
                st.markdown(response.content[0].text)
                
            except Exception as e:
                st.error(f"連線或解析時發生錯誤，請檢查 API Key 是否正確。錯誤細節：{str(e)}")