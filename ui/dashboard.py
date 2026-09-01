import streamlit as st

def render_dashboard(analyzer, lang: str = 'en', translations: dict = None):
    """Render student progress dashboard with elderly-friendly Urdu/English display."""
    if not translations:
        translations = {}

    st.title("📊 میری پیشرفت (My Progress)")
    
    # Get stats from analyzer
    progress = analyzer.get_progress()
    study_stats = analyzer.get_study_stats()
    sm2_stats = analyzer.get_sm2_stats()
    
    total_attempts = progress.get('total_attempts', 0)
    correct_attempts = progress.get('correct_attempts', 0)
    accuracy = progress.get('accuracy', 0)
    unique_verbs = study_stats.get('unique_verbs_studied', 0)
    
    # Stat cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div style="background: #dcfce7; padding: 20px; border-radius: 12px; text-align: center; border: 2px solid #86efac;">
            <div style="font-size: 2.5em; font-weight: bold; color: #92400e;">📖 {unique_verbs}</div>
            <div style="color: #4b5563; font-size: 1.1em; direction: rtl;">پڑھے ہوئے افعال<br/>(Verbs Studied)</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div style="background: #dcfce7; padding: 20px; border-radius: 12px; text-align: center; border: 2px solid #86efac;">
            <div style="font-size: 2.5em; font-weight: bold; color: #92400e;">✍️ {total_attempts}</div>
            <div style="color: #4b5563; font-size: 1.1em; direction: rtl;">کل سوالات<br/>(Total Questions)</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div style="background: #dcfce7; padding: 20px; border-radius: 12px; text-align: center; border: 2px solid #86efac;">
            <div style="font-size: 2.5em; font-weight: bold; color: #166534;">{correct_attempts}</div>
            <div style="color: #4b5563; font-size: 1.1em; direction: rtl;">درست جوابات<br/>(Correct)</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        acc_color = "#166534" if accuracy >= 70 else "#92400e" if accuracy >= 40 else "#f87171"
        st.markdown(f"""
        <div style="background: #dcfce7; padding: 20px; border-radius: 12px; text-align: center; border: 2px solid #86efac;">
            <div style="font-size: 2.5em; font-weight: bold; color: {acc_color};">🎯 {accuracy:.0f}%</div>
            <div style="color: #4b5563; font-size: 1.1em; direction: rtl;">درستگی<br/>(Accuracy)</div>
        </div>
        """, unsafe_allow_html=True)

    # SM-2 Flashcard Stats
    if sm2_stats.get('total_cards', 0) > 0:
        st.markdown("---")
        st.markdown("<h3 style='direction: rtl; text-align: right;'>🗂️ فلیش کارڈز (SM-2 Flashcards)</h3>", unsafe_allow_html=True)
        
        fc1, fc2, fc3 = st.columns(3)
        with fc1:
            st.markdown(f"""
            <div style="background: #f6f6f2; padding: 15px; border-radius: 10px; text-align: center; border-right: 4px solid #3b82f6;">
                <div style="font-size: 2em; font-weight: bold; color: #4b5563;">{sm2_stats['total_cards']}</div>
                <div style="color: #6b7280; direction: rtl;">کل کارڈز (Total Cards)</div>
            </div>
            """, unsafe_allow_html=True)
        with fc2:
            st.markdown(f"""
            <div style="background: #f6f6f2; padding: 15px; border-radius: 10px; text-align: center; border-right: 4px solid #92400e;">
                <div style="font-size: 2em; font-weight: bold; color: #92400e;">{sm2_stats['due_today']}</div>
                <div style="color: #6b7280; direction: rtl;">آج باقی (Due Today)</div>
            </div>
            """, unsafe_allow_html=True)
        with fc3:
            st.markdown(f"""
            <div style="background: #f6f6f2; padding: 15px; border-radius: 10px; text-align: center; border-right: 4px solid #166534;">
                <div style="font-size: 2em; font-weight: bold; color: #166534;">{sm2_stats['average_ef']}</div>
                <div style="color: #6b7280; direction: rtl;">اوسط آسانی (Avg EF)</div>
            </div>
            """, unsafe_allow_html=True)

    # Recent Practice History
    st.markdown("---")
    st.markdown("<h3 style='direction: rtl; text-align: right;'>📝 حالیہ مشق (Recent Activity)</h3>", unsafe_allow_html=True)
    
    history = analyzer.get_practice_history()
    if history:
        # history returns tuples: (verb_id, correct, question_type, timestamp)
        for row in history[-10:][::-1]:  # Last 10, newest first
            verb_id = row[0]
            correct = row[1]
            q_type = row[2]
            timestamp = row[3] if len(row) > 3 else ''
            
            verb = analyzer.get_verb_by_id(verb_id)
            verb_name = verb.get('arabic', verb_id) if verb else verb_id
            
            icon = "✅" if correct else "❌"
            result_text = "درست (Correct)" if correct else "غلط (Incorrect)"
            
            st.markdown(f"""
            <div style="background: #f6f6f2; padding: 12px 18px; border-radius: 8px; margin: 5px 0; direction: rtl; text-align: right; display: flex; justify-content: space-between; align-items: center;">
                <span style="font-size: 1.3em;">{icon} <b style="color: #92400e;">{verb_name}</b> — {result_text}</span>
                <span style="color: #718096; font-size: 0.85em;">{timestamp}</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("ابھی تک کوئی مشق نہیں ہوئی۔ مشق شروع کریں! (No practice yet. Start practicing!)")

    # Saved Verbs
    st.markdown("---")
    st.markdown("<h3 style='direction: rtl; text-align: right;'>⭐ محفوظ افعال (Saved Verbs)</h3>", unsafe_allow_html=True)
    bookmarks = analyzer.get_bookmarks()
    if bookmarks:
        cols = st.columns(min(len(bookmarks), 4))
        for idx, b_id in enumerate(bookmarks):
            verb = analyzer.get_verb_by_id(b_id)
            if verb:
                with cols[idx % min(len(bookmarks), 4)]:
                    st.markdown(f"""
                    <div style="background: #f6f6f2; padding: 15px; border-radius: 10px; text-align: center; border-top: 3px solid #92400e;">
                        <div style="font-size: 1.8em; color: #92400e; font-weight: bold;">{verb.get('arabic', '')}</div>
                        <div style="color: #6b7280; direction: rtl;">{verb.get('meaning_urdu', '')}</div>
                    </div>
                    """, unsafe_allow_html=True)
    else:
        st.info("ابھی تک کوئی فعل محفوظ نہیں ہوا۔ (No verbs saved yet.)")
