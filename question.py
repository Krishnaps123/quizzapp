import streamlit as st
import random
import time
import pandas as pd
import os

# ---------- QUIZ DATA ----------
questions = [
    {
        "question": "What is the capital of France?",
        "options": ["Berlin", "Madrid", "Paris", "Rome"],
        "answer": "Paris",
        "image": "assets/pariz.jpg",
        "audio": None,
    },
    {
        "question": "Which planet is known as the Red Planet?",
        "options": ["Earth", "Mars", "Jupiter", "Saturn"],
        "answer": "Mars",
        "image": None,
        "audio": None,
    },
    {
        "question": "Who wrote 'Hamlet'?",
        "options": ["Leo Tolstoy", "William Shakespeare", "Mark Twain", "Jane Austen"],
        "answer": "William Shakespeare",
        "image": None,
        "audio": None,
    
    },
    {
        "question": "Which is the largest mammal?",
        "options": ["Elephant", "Giraffe", "Blue Whale", "Hippopotamus"],
        "answer": "Blue Whale",
        "image": "assets/bluewhale.jpg",
        "audio": None,
    }
]

RESULTS_FILE = "results.csv"
TIME_LIMIT = 20 

# ---------- INITIAL STATE ----------
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'quiz_started' not in st.session_state:
    st.session_state.quiz_started = False
if 'quiz_order' not in st.session_state:
    st.session_state.quiz_order = random.sample(questions, len(questions))
    st.session_state.current_q = 0
    st.session_state.score = 0
    st.session_state.answered = False
    st.session_state.start_time = time.time()
    st.session_state.timeout = False
if 'quiz_finished' not in st.session_state:
    st.session_state.quiz_finished = False


# ---------- FUNCTIONS ----------
def check_answer(user_answer):
    correct = st.session_state.quiz_order[st.session_state.current_q]['answer']
    if user_answer == correct:
        st.success("✅ Correct!")
        st.session_state.score += 1
    else:
        st.error("❌ Wrong!")
        st.info(f"The correct answer is: **{correct}**")
    st.session_state.answered = True


def reset_timer():
    st.session_state.start_time = time.time()
    st.session_state.timeout = False


def save_result(name, score, total, percentage):
    time_taken = int(time.time() - st.session_state.quiz_start_time)
    data = {
        "Name": [name],
        "Score": [score],
        "Total": [total],
        "Percentage": [percentage],
        "Time (s)": [time_taken]
    }
    new_df = pd.DataFrame(data)
    if os.path.exists(RESULTS_FILE):
        existing_df = pd.read_csv(RESULTS_FILE)
        updated_df = pd.concat([existing_df, new_df], ignore_index=True)
    else:
        updated_df = new_df
    updated_df.to_csv(RESULTS_FILE, index=False)


def display_leaderboard():
    st.subheader("🏆 Leaderboard")
    if os.path.exists(RESULTS_FILE):
        df = pd.read_csv(RESULTS_FILE)
        df = df.sort_values(by=["Score", "Percentage", "Time (s)"], ascending=[False, False, True])
        df.index = range(1, len(df) + 1)
        st.dataframe(df.style.highlight_max(axis=0), use_container_width=True)
    else:
        st.info("No leaderboard data yet.")

def display_participants():
    st.subheader("👥 Participants")
    if os.path.exists(RESULTS_FILE):
        df = pd.read_csv(RESULTS_FILE)
        st.write(", ".join(df['Name'].unique()))
    else:
        st.info("No participants yet.")

# ---------- START PAGE ----------
if not st.session_state.quiz_started:
    st.title("🎯 Welcome to the Quiz!")

    st.session_state.username = st.text_input("Enter your name to begin:")

    if st.session_state.username:
        if st.button("Start Quiz"):
            st.session_state.quiz_started = True
            st.session_state.quiz_start_time = time.time()
            reset_timer()
else:
    # ---------- TIMER ----------
    elapsed = time.time() - st.session_state.start_time
    remaining_time = max(0, TIME_LIMIT - int(elapsed))

    if remaining_time == 0 and not st.session_state.answered:
        st.warning("⏰ Time's up!")
        st.session_state.timeout = True
        st.session_state.answered = True

    # ---------- QUIZ QUESTIONS ----------
    if st.session_state.current_q < len(st.session_state.quiz_order):
        q_data = st.session_state.quiz_order[st.session_state.current_q]

        st.title(" Advanced Quiz App")
        st.header(f"Hello, {st.session_state.username} ")

        st.progress(remaining_time / TIME_LIMIT)
        st.subheader(f"Question {st.session_state.current_q + 1}: {q_data['question']}")

        if q_data['image']:
            st.image(q_data['image'], width=400)
        if q_data['audio']:
            st.audio(q_data['audio'])

        user_choice = st.radio("Choose your answer:", q_data["options"], key=f"q_{st.session_state.current_q}")

        if not st.session_state.answered:
            if st.button("Submit Answer") or st.session_state.timeout:
                check_answer(user_choice)

        if st.session_state.answered and st.button("Next"):
            st.session_state.current_q += 1
            st.session_state.answered = False
            reset_timer()

    else:
        if not st.session_state.quiz_finished:
            st.session_state.quiz_finished = True
            score = st.session_state.score
            total_qs = len(st.session_state.quiz_order)
            percentage = (score / total_qs) * 100

            save_result(st.session_state.username, score, total_qs, percentage)

        # ---------- RESULTS ----------
        st.title("🎉 Quiz Completed!")
        st.write(f"✅ Final Score: **{st.session_state.score} / {len(st.session_state.quiz_order)}**")
        percentage = (st.session_state.score / len(st.session_state.quiz_order)) * 100
        st.write(f"📊 Percentage: **{percentage:.2f}%**")

        if percentage >= 50:
            st.success("🎯 You passed the quiz!")
        else:
            st.error("❌ You failed the quiz. Try again!")

        display_leaderboard()
        display_participants()

        if st.button("Restart Quiz"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
