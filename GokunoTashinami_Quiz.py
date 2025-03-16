import streamlit as st
import pandas as pd
import random

# GoogleスプレッドシートのURL（CSV形式でエクスポートしたURLを使用）
DATA_URL = "https://docs.google.com/spreadsheets/d/1Ep1NKToR7nQVrKfAdIz3f8Z75TJ70_7j/gviz/tq?tqx=out:csv"

# データの読み込み
@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)
    return df

data = load_data()

# Streamlit UI
st.title("**語句のたしなみ**")

# サイドバーで出題範囲を選択
st.sidebar.header("出題内容の選択")
game_mode = st.sidebar.radio("ゲームを選択", ["意味を答える", "言葉を答える"])
category = st.sidebar.selectbox("カテゴリを選択", ["すべて"] + list(data["Category"].unique()))
test_num = st.sidebar.selectbox("Test#を選択", ["すべて"] + list(data["Test#"].unique()))
page_num = st.sidebar.selectbox("Page#を選択", ["すべて"] + list(data["Page#"].unique()))
importance = st.sidebar.selectbox("重要度を選択", ["すべて"] + sorted(data["Importance"].unique()))
question_count = st.sidebar.selectbox("出題数", ["すべて", 30, 20, 10, 5])

if "game_started" not in st.session_state:
    st.session_state.game_started = False

if st.sidebar.button("開始"):
    # 出題範囲のフィルタリング
    filtered_data = data.copy()
    if category != "すべて":
        filtered_data = filtered_data[filtered_data["Category"] == category]
    if test_num != "すべて":
        filtered_data = filtered_data[filtered_data["Test#"] == test_num]
    if page_num != "すべて":
        filtered_data = filtered_data[filtered_data["Page#"] == page_num]
    if importance != "すべて":
        filtered_data = filtered_data[filtered_data["Importance"] == importance]

    # 出題数の設定
    if question_count != "すべて":
        filtered_data = filtered_data.sample(min(len(filtered_data), int(question_count)))
    else:
        filtered_data = filtered_data.sample(frac=1)  # シャッフル

    st.session_state.questions = filtered_data.to_dict(orient="records")
    random.shuffle(st.session_state.questions)
    st.session_state.current_question = 0
    st.session_state.correct_count = 0
    st.session_state.mistakes = []
    st.session_state.show_answer = False
    st.session_state.game_started = True
    st.rerun()

if st.session_state.game_started:
    # 進行度バーの追加
    total_questions = len(st.session_state.questions)
    current_progress = st.session_state.current_question
    st.progress(current_progress / total_questions if total_questions > 0 else 0)
    st.markdown(f"**進行度: {current_progress}/{total_questions}**")

    if st.session_state.current_question < total_questions:
        row = st.session_state.questions[st.session_state.current_question]
        
        if game_mode == "意味を答える":
            st.write("**言葉:**", f":blue[{row['Word']}]")
            st.write("**例文:**", f":blue[{row['Example']}]")
        else:
            st.write("**意味:**", f":blue[{row['Definition']}]")
            st.write("**例文:**", f":blue[{row['Example']}]")
        
        if not st.session_state.show_answer:
            if st.button("🔍 答えを見る"):
                st.session_state.show_answer = True
                st.rerun()
        
        if st.session_state.show_answer:
            st.write("**答え:**", f":blue[**{row['Definition'] if game_mode == '意味を答える' else row['Word']}**]")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ 正解！"):
                    st.session_state.correct_count += 1
                    st.session_state.current_question += 1
                    st.session_state.show_answer = False
                    st.rerun()
            with col2:
                if st.button("❌ 不正解。。"):
                    st.session_state.mistakes.append(row)
                    st.session_state.current_question += 1
                    st.session_state.show_answer = False
                    st.rerun()

    else:
        # 結果表示
        correct = st.session_state.correct_count
        accuracy = (correct / total_questions) * 100 if total_questions > 0 else 0
        
        st.markdown(f"### 🎯 成績: {correct} / {total_questions} 正解 ({accuracy:.2f}%)")
        
        if st.session_state.mistakes:
            st.write("### ❌ 間違えた問題一覧")
            mistakes_df = pd.DataFrame(st.session_state.mistakes)
            st.table(mistakes_df[['Word', 'Definition', 'Example', 'Importance', 'Category', 'Test#', 'Page#']])
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 復習モード"):
                    st.session_state.questions = st.session_state.mistakes
                    st.session_state.current_question = 0
                    st.session_state.correct_count = 0
                    st.session_state.mistakes = []
                    st.session_state.show_answer = False
                    st.rerun()
            with col2:
                if st.button("🏠 Topページに戻る"):
                    st.session_state.questions = []
                    st.session_state.current_question = 0
                    st.session_state.correct_count = 0
                    st.session_state.mistakes = []
                    st.session_state.show_answer = False
                    st.session_state.game_started = False
                    st.rerun()
