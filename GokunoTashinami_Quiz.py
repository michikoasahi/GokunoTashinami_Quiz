import streamlit as st
import pandas as pd
import random

# GoogleスプレッドシートのCSV形式のURL
SHEET_URL = "https://docs.google.com/spreadsheets/d/1Ep1NKToR7nQVrKfAdIz3f8Z75TJ70_7j/export?format=csv"

# データの読み込み
def load_data():
    return pd.read_csv(SHEET_URL)

# セッションの初期化
def initialize_session():
    if "index" not in st.session_state:
        st.session_state.index = 0
        st.session_state.correct = 0
        st.session_state.wrong_questions = []
        st.session_state.show_answer = False
        st.session_state.filtered_df = None

def filter_questions(df, category, test_num, page_num, importance, question_count):
    if category != "すべて":
        df = df[df["Category"] == category]
    if test_num != "すべて":
        df = df[df["Test#"] == test_num]
    if page_num != "すべて":
        df = df[df["Page#"] == page_num]
    if importance != "すべて":
        df = df[df["Importance"] == importance]
    
    if question_count != "すべて":
        df = df.sample(min(len(df), int(question_count)))
    else:
        df = df.sample(frac=1).reset_index(drop=True)
    
    return df

def display_question(question, game_mode):
    if game_mode == "意味を答える":
        st.write("**言葉:**", f":blue[{question['Word']}]")
        st.write("**例文:**", f":blue[{question['Example']}]")
    else:
        st.write("**意味:**", f":blue[{question['Definition']}]")
        st.write("**例文:**", f":blue[{question['Example']}]")

def main():
    st.title("**語句のたしなみ**")
    df = load_data()
    initialize_session()

    st.sidebar.header("出題内容の選択")
    game_mode = st.sidebar.radio("【ゲームを選択】", ["意味を答える", "言葉を答える"])
    category = st.sidebar.selectbox("【カテゴリを選択】", ["すべて"] + list(df["Category"].unique()))
    test_num = st.sidebar.selectbox("【Test#を選択】", ["すべて"] + list(df["Test#"].unique()))
    page_num = st.sidebar.selectbox("【Page#を選択】", ["すべて"] + list(df["Page#"].unique()))
    importance = st.sidebar.selectbox("【重要度を選択】", ["すべて"] + list(df["Importance"].unique()))
    question_count = st.sidebar.radio("【出題数】", ["すべて", 30, 20, 10, 5])

    # サイドバーの変更を検知し、データを更新
    st.session_state.filtered_df = filter_questions(df, category, test_num, page_num, importance, question_count)
    
    total_questions = len(st.session_state.filtered_df)

    if st.session_state.index < total_questions:
        question = st.session_state.filtered_df.iloc[st.session_state.index]
        display_question(question, game_mode)

        if st.button("答えを見る"):
            st.session_state.show_answer = True
        
        if st.session_state.show_answer:
            answer = question['Definition'] if game_mode == "意味を答える" else question['Word']
            st.write("**答え:**", f":blue[**{answer}**]")

            col1, col2 = st.columns(2)
            if col1.button("正解！"):
                st.session_state.correct += 1
                st.session_state.index += 1
                st.session_state.show_answer = False
                st.rerun()
            if col2.button("不正解。。"):
                st.session_state.wrong_questions.append(question)
                st.session_state.index += 1
                st.session_state.show_answer = False
                st.rerun()
        
        st.progress(st.session_state.index / total_questions)
        st.write(f"進行度: {st.session_state.index} / {total_questions} 問")
    else:
        correct_answers = st.session_state.correct
        accuracy = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
        st.write(f"### :green[成績: {correct_answers} / {total_questions} 正解 ({accuracy:.2f}%)]")
        
        if st.session_state.wrong_questions:
            st.write("### 間違えた問題一覧")
            wrong_df = pd.DataFrame(st.session_state.wrong_questions)
            st.dataframe(wrong_df[["Word", "Definition", "Example", "Importance", "Category", "Test#", "Page#"]])
            
            col1, col2 = st.columns(2)
            if col1.button("Topページに戻る"):
                st.session_state.index = 0
                st.session_state.correct = 0
                st.session_state.wrong_questions = []
                st.session_state.show_answer = False
                st.session_state.filtered_df = None
                st.rerun()
            if col2.button("復習モード"):
                st.session_state.index = 0
                st.session_state.correct = 0
                st.session_state.filtered_df = pd.DataFrame(st.session_state.wrong_questions)
                st.session_state.wrong_questions = []
                st.session_state.show_answer = False
                st.rerun()

if __name__ == "__main__":
    main()
