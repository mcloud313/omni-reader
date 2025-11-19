import streamlit as st
import pandas as pd
from datetime import date
import os
import json

# --- CONFIGURATION & SETUP ---
DATA_FILE = 'reading_data.json'

# Initialize data structure if file doesn't exist
def load_data():
    if not os.path.exists(DATA_FILE):
        return {
            "books": [],  # List of dicts: {title, current, max, status}
            "logs": [],   # List of dicts: {date, pages_read}
            "user_stats": {"total_xp": 0, "level": 1}
        }
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)

data = load_data()

# --- SIDEBAR: ACTION CENTER ---
st.sidebar.header("📚 Library Actions")

# 1. Add a New Book
with st.sidebar.expander("Add New Book"):
    new_title = st.text_input("Book Title")
    new_max_pages = st.number_input("Total Pages", min_value=1, value=300)
    if st.button("Add to Library"):
        if new_title:
            data["books"].append({
                "title": new_title,
                "current": 0,
                "max": new_max_pages,
                "status": "Active"
            })
            save_data(data)
            st.rerun()

# 2. Log Reading Session (The Gamification Engine)
with st.sidebar.expander("Log Reading Session", expanded=True):
    active_books = [b['title'] for b in data['books'] if b['status'] == 'Active']
    if active_books:
        selected_book = st.selectbox("Which book did you read?", active_books)
        pages_read = st.number_input("Pages read just now", min_value=1, value=10)
        
        if st.button("Submit Log"):
            # Update Book Progress
            for book in data["books"]:
                if book["title"] == selected_book:
                    book["current"] = min(book["current"] + pages_read, book["max"])
                    
                    # Check if finished
                    if book["current"] == book["max"]:
                        st.balloons()
                        st.sidebar.success(f"Finished {book['title']}!")
            
            # Update Stats
            data["logs"].append({"date": str(date.today()), "pages": pages_read})
            data["user_stats"]["total_xp"] += pages_read
            # Simple leveling logic: Level up every 500 pages
            data["user_stats"]["level"] = 1 + (data["user_stats"]["total_xp"] // 500)
            
            save_data(data)
            st.rerun()
    else:
        st.sidebar.info("Add a book to start tracking!")

# --- MAIN DASHBOARD ---
st.title("📖 Omni-Reader Dashboard")

# 1. Gamification Header
xp = data["user_stats"]["total_xp"]
lvl = data["user_stats"]["level"]
next_lvl = (lvl * 500)
progress_to_next = (xp - ((lvl-1)*500)) / 500

col1, col2, col3 = st.columns(3)
col1.metric("Current Level", f"Lvl {lvl}")
col1.progress(progress_to_next)
col2.metric("Total Pages Read (XP)", f"{xp} XP")

# Daily Progress Calculation
today_str = str(date.today())
today_pages = sum(log['pages'] for log in data['logs'] if log['date'] == today_str)
col3.metric("Pages Read Today", today_pages, delta=None)

st.markdown("---")

# 2. The Active Book Stack
st.subheader("Currently Reading")

if not data['books']:
    st.info("No books currently being tracked.")
else:
    # Sort by 'Active' first
    for i, book in enumerate(data['books']):
        if book['status'] == 'Active':
            with st.container():
                c1, c2 = st.columns([3, 1])
                
                # Calculate Percentage
                percent = book['current'] / book['max']
                display_percent = int(percent * 100)
                
                with c1:
                    st.markdown(f"**{book['title']}**")
                    st.progress(percent)
                    st.caption(f"Page {book['current']} of {book['max']} ({display_percent}%)")
                
                with c2:
                    # Delete button (small hack to keep it clean)
                    if st.button("🗑️", key=f"del_{i}"):
                        data["books"].pop(i)
                        save_data(data)
                        st.rerun()
                
                st.markdown("") # Spacer