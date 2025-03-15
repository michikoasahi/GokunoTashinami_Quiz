import streamlit as st
import pandas as pd
import random

def load_data():
    url = "https://docs.google.com/spreadsheets/d/1Ep1NKToR7nQVrKfAdIz3f8Z75TJ70_7j/export?format=csv"
    df = pd.read_csv(url)
    return df

def filter_data(df, category, test_num, page_num, importance):
    if category != "すべて":
        df = df[df["Category"] == category]
    if test_num != "すべて":
        df = df[df["Test#"] == test_num]
    if page_num != "すべて":
        df = df[df["Page#"] == page_num]
    if importance != "すべて":
        df = df[df["Importance"] == importance]
    return df

def main():
    st.title("**語句のたしなみ**")
    df = load_data()
    
    categories = ["すべて"] + df["Category"].unique().tolist()
    test_nums = ["すべて"] + df["Test#"].unique().tolist()
    page_nums = ["すべて"] + df["Page#"].unique().tolist()
    importance_levels = ["すべて", "A", "B"]
    
    category = st.sidebar.selectbox("**カテゴリを選択**", categories)
    test_num = st.sidebar.selectbox("**Test＃を選択**", test_nums)
    page_num = st.sidebar.selectbox("**Page＃を選択**", page_nums)
    importance = st.sidebar.selectbox("**重要度を選択**", importance_levels)
    num_questions = st.sidebar.selectbox("**出題数**", ["すべて", 50, 40, 30, 20, 10])
    
    if st.sidebar.button("開始"):
        filtered_df = filter_data(df, category, test_num, page_num, importance)
        if num_questions != "すべて":
            filtered_df = filtered_df.sample(min(len(filtered_df), int(num_questions)))
        
        st.session_state["questions"] = filtered_df.to_dict(orient="records")
        st.session_state["current_index"] = 0
        st.session_state["score"] = 0
        st.session_state["incorrect"] = []
    
    if "questions" in st.session_state:
        questions = st.session_state["questions"]
        index = st.session_state["current_index"]
        
        if index < len(questions):
            q = questions[index]
            st.write(f"**問題 {index + 1} / {len(questions)}**")
            st.progress((index + 1) / len(questions))
            
            st.write(f"**Definition:** <span style='color:blue; font-weight:bold;'>{q['Definition']}</span>", unsafe_allow_html=True)
            st.write(f"**Example:** <span style='color:blue; font-weight:bold;'>{q['Example']}</span>", unsafe_allow_html=True)
            
            if st.button("答えを見る", key=f"show_answer_{index}"):
                st.session_state["show_answer"] = True
            
            if "show_answer" in st.session_state:
                st.write(f"**Answer:** <span style='color:blue; font-weight:bold; font-size:24px;'>{q['Answer']}</span>", unsafe_allow_html=True)
                
                if st.button("正解！", key=f"correct_{index}"):
                    st.session_state["score"] += 1
                    st.session_state["current_index"] += 1
                    del st.session_state["show_answer"]
                    st.rerun()
                
                if st.button("不正解。。", key=f"incorrect_{index}"):
                    st.session_state["incorrect"].append(q)
                    st.session_state["current_index"] += 1
                    del st.session_state["show_answer"]
                    st.rerun()
        else:
            st.write(f"**成績: {st.session_state['score']} / {len(questions)} ({(st.session_state['score']/len(questions))*100:.1f}%)**")
            if st.session_state["incorrect"]:
                st.write("**間違えた問題**")
                incorrect_df = pd.DataFrame(st.session_state["incorrect"])
                st.dataframe(incorrect_df.style.set_properties(**{"border": "1px solid black"}))
                
                if st.button("復習モード"):
                    st.session_state["questions"] = st.session_state["incorrect"]
                    st.session_state["current_index"] = 0
                    st.session_state["score"] = 0
                    st.session_state["incorrect"] = []
                    st.rerun()
            
            if st.button("Topページに戻る"):
                del st.session_state["questions"]
                del st.session_state["current_index"]
                del st.session_state["score"]
                del st.session_state["incorrect"]
                st.rerun()
    
if __name__ == "__main__":
    main()
