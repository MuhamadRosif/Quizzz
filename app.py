import streamlit as st
import time
import random
from supabase_client import supabase
from PIL import Image

st.set_page_config(page_title="Quiz App", layout="centered")

# ==========================================
# LOADING SCREEN (LOGO UNIVERSITAS)
# ==========================================
if "loaded" not in st.session_state:
    st.session_state.loaded = False

if not st.session_state.loaded:
    st.markdown("""
    <style>
        .center {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 90vh;
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<div class='center'>", unsafe_allow_html=True)

    try:
        logo = Image.open("assets/logo.png")
        st.image(logo, width=250)
    except:
        st.write("Logo tidak ditemukan di folder assets/logo.png")

    st.markdown("</div>", unsafe_allow_html=True)

    time.sleep(2.5)
    st.session_state.loaded = True
    st.rerun()

# =========================================================
# Detect admin mode
# =========================================================
params = st.query_params
is_admin = "page" in params and params["page"] == "admin"

# =========================================================
# LOAD QUESTIONS
# =========================================================
def load_questions():
    res = supabase.table("questions").select("*").execute()
    data = res.data
    random.shuffle(data)  # acak urutan soal
    return data

# =========================================================
# ADMIN PAGE
# =========================================================
if is_admin:
    st.title("Admin Panel - Manage Questions")

    st.write("### Tambah Soal Baru")
    q_text = st.text_area("Pertanyaan")
    opt1 = st.text_input("Opsi 1")
    opt2 = st.text_input("Opsi 2")
    opt3 = st.text_input("Opsi 3")
    opt4 = st.text_input("Opsi 4")
    correct = st.selectbox("Jawaban Benar (pilih index)", [0,1,2,3])

    if st.button("Tambah Soal"):
        supabase.table("questions").insert({
            "question": q_text,
            "options": [opt1,opt2,opt3,opt4],
            "answer": correct
        }).execute()
        st.success("Soal berhasil ditambahkan!")
        time.sleep(1)
        st.rerun()

    st.divider()
    st.write("### Semua Soal")
    all_q = load_questions()
    for q in all_q:
        st.write(f"**ID {q['id']}**: {q['question']}")
        st.write(q["options"])
        st.write(f"Jawaban benar: {q['answer']}")
        col1, col2 = st.columns(2)
        with col1:
            if st.button(f"Edit {q['id']}"):
                st.query_params["edit"] = q["id"]
                st.rerun()
        with col2:
            if st.button(f"Hapus {q['id']}"):
                supabase.table("questions").delete().eq("id", q["id"]).execute()
                st.rerun()

    # Edit Mode
    if "edit" in st.query_params:
        edit_id = int(st.query_params["edit"])
        st.divider()
        st.write(f"### Edit Soal ID {edit_id}")
        q = supabase.table("questions").select("*").eq("id", edit_id).single().execute().data
        e_q = st.text_area("Pertanyaan", q["question"])
        e_opt = []
        for i in range(4):
            e_opt.append(st.text_input(f"Opsi {i+1}", q["options"][i]))
        e_ans = st.selectbox("Jawaban Benar", [0,1,2,3], index=q["answer"])
        if st.button("Simpan Perubahan"):
            supabase.table("questions").update({
                "question": e_q,
                "options": e_opt,
                "answer": e_ans
            }).eq("id", edit_id).execute()
            st.success("Soal berhasil diupdate!")
            del st.query_params["edit"]
            time.sleep(1)
            st.rerun()

    st.stop()

# =========================================================
# SESSION STATE
# =========================================================
if "page" not in st.session_state:
    st.session_state.page = "home"
if "name" not in st.session_state:
    st.session_state.name = ""
if "score" not in st.session_state:
    st.session_state.score = 0
if "q_index" not in st.session_state:
    st.session_state.q_index = 0
if "questions" not in st.session_state:
    st.session_state.questions = []

# ---------------- HOME ----------------
if st.session_state.page == "home":
    st.title("Quiz Phishing")
    st.write("Masukkan nama untuk mulai")
    name = st.text_input("Nama")
    if st.button("Mulai"):
        if name.strip() == "":
            st.error("Nama tidak boleh kosong")
        else:
            st.session_state.name = name
            st.session_state.q_index = 0
            st.session_state.score = 0
            st.session_state.questions = load_questions()
            st.session_state.page = "quiz"
            st.rerun()

# ---------------- QUIZ ----------------
elif st.session_state.page == "quiz":
    questions = st.session_state.questions
    q_i = st.session_state.q_index

    if q_i >= len(questions):
        st.session_state.page = "result"
        st.rerun()

    q = questions[q_i]

    st.header(f"Soal {q_i+1}/{len(questions)}")
    st.write("### " + q["question"])

    # Timer 30 detik
    if "timer" not in st.session_state or st.session_state.timer_reset:
        st.session_state.start_time = time.time()
        st.session_state.timer_reset = False

    elapsed = int(time.time() - st.session_state.start_time)
    remaining = max(30 - elapsed, 0)
    st.progress(remaining/30)

    st.write(f"⏱ Sisa waktu: {remaining} detik")

    picked = st.radio("Pilih jawaban:", q["options"])

    # Auto next jika timer habis
    if remaining <= 0:
        if picked == q["options"][q["answer"]]:
            st.session_state.score += 1
        st.session_state.q_index += 1
        st.session_state.timer_reset = True
        st.rerun()

    if st.button("Lanjut"):
        if picked == q["options"][q["answer"]]:
            st.session_state.score += 1
        st.session_state.q_index += 1
        st.session_state.timer_reset = True
        st.rerun()

# ---------------- RESULT ----------------
elif st.session_state.page == "result":
    st.success(f"Skor Anda: {st.session_state.score}/{len(st.session_state.questions)}")

    supabase.table("leaderboard").insert({
        "name": st.session_state.name,
        "score": st.session_state.score,
        "total": len(st.session_state.questions)
    }).execute()

    if st.button("Lihat leaderboard"):
        st.session_state.page = "leaderboard"
        st.rerun()

# ---------------- LEADERBOARD ----------------
elif st.session_state.page == "leaderboard":
    st.title("Leaderboard")
    rows = supabase.table("leaderboard").select("*").order("score", desc=True).execute().data
    for r in rows:
        st.write(f"**{r['name']}** — {r['score']} / {r['total']}")
    if st.button("Kembali"):
        st.session_state.page = "home"
        st.rerun()
