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
        <div style="background: linear-gradient(135deg, #1e3a5f, #2b6cb0); padding: 20px; border-radius: 12px; text-align: center;">
            <div style="font-size: 2.5em; font-weight: bold; color: #fbbf24;">📖 {unique_verbs}</div>
            <div style="color: #93c5fd; font-size: 1.1em; direction: rtl;">پڑھے ہوئے افعال<br/>(Verbs Studied)</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #1e3a5f, #2b6cb0); padding: 20px; border-radius: 12px; text-align: center;">
            <div style="font-size: 2.5em; font-weight: bold; color: #fbbf24;">✍️ {total_attempts}</div>
            <div style="color: #93c5fd; font-size: 1.1em; direction: rtl;">کل سوالات<br/>(Total Questions)</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #1e3a5f, #2b6cb0); padding: 20px; border-radius: 12px; text-align: center;">
            <div style="font-size: 2.5em; font-weight: bold; color: #4ade80;">{correct_attempts}</div>
            <div style="color: #93c5fd; font-size: 1.1em; direction: rtl;">درست جوابات<br/>(Correct)</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        acc_color = "#4ade80" if accuracy >= 70 else "#fbbf24" if accuracy >= 40 else "#f87171"
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #1e3a5f, #2b6cb0); padding: 20px; border-radius: 12px; text-align: center;">
            <div style="font-size: 2.5em; font-weight: bold; color: {acc_color};">🎯 {accuracy:.0f}%</div>
            <div style="color: #93c5fd; font-size: 1.1em; direction: rtl;">درستگی<br/>(Accuracy)</div>
        </div>
        """, unsafe_allow_html=True)

    # SM-2 Flashcard Stats
    if sm2_stats.get('total_cards', 0) > 0:
        st.markdown("---")
        st.markdown("<h3 style='direction: rtl; text-align: right;'>🗂️ فلیش کارڈز (SM-2 Flashcards)</h3>", unsafe_allow_html=True)
        
        fc1, fc2, fc3 = st.columns(3)
        with fc1:
            st.markdown(f"""
            <div style="background: #2d3748; padding: 15px; border-radius: 10px; text-align: center; border-right: 4px solid #3b82f6;">
                <div style="font-size: 2em; font-weight: bold; color: #93c5fd;">{sm2_stats['total_cards']}</div>
                <div style="color: #a0aec0; direction: rtl;">کل کارڈز (Total Cards)</div>
            </div>
            """, unsafe_allow_html=True)
        with fc2:
            st.markdown(f"""
            <div style="background: #2d3748; padding: 15px; border-radius: 10px; text-align: center; border-right: 4px solid #f59e0b;">
                <div style="font-size: 2em; font-weight: bold; color: #fbbf24;">{sm2_stats['due_today']}</div>
                <div style="color: #a0aec0; direction: rtl;">آج باقی (Due Today)</div>
            </div>
            """, unsafe_allow_html=True)
        with fc3:
            st.markdown(f"""
            <div style="background: #2d3748; padding: 15px; border-radius: 10px; text-align: center; border-right: 4px solid #4ade80;">
                <div style="font-size: 2em; font-weight: bold; color: #4ade80;">{sm2_stats['average_ef']}</div>
                <div style="color: #a0aec0; direction: rtl;">اوسط آسانی (Avg EF)</div>
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
            <div style="background: #2d3748; padding: 12px 18px; border-radius: 8px; margin: 5px 0; direction: rtl; text-align: right; display: flex; justify-content: space-between; align-items: center;">
                <span style="font-size: 1.3em;">{icon} <b style="color: #f39c12;">{verb_name}</b> — {result_text}</span>
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
                    <div style="background: #2d3748; padding: 15px; border-radius: 10px; text-align: center; border-top: 3px solid #f59e0b;">
                        <div style="font-size: 1.8em; color: #f39c12; font-weight: bold;">{verb.get('arabic', '')}</div>
                        <div style="color: #a0aec0; direction: rtl;">{verb.get('meaning_urdu', '')}</div>
                    </div>
                    """, unsafe_allow_html=True)
    else:
        st.info("ابھی تک کوئی فعل محفوظ نہیں ہوا۔ (No verbs saved yet.)")
