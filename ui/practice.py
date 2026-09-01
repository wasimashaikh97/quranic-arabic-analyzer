import streamlit as st
import random

def render_practice_mode(analyzer, lang: str = 'en', translations: dict = None):
    """Render practice mode with MCQ exercises generated from real verb data."""
    st.title("✍️ عربی فعل کی مشق (Practice Drills)")
    
    if 'practice_score' not in st.session_state:
        st.session_state.practice_score = 0
    if 'practice_total' not in st.session_state:
        st.session_state.practice_total = 0
    if 'current_q' not in st.session_state:
        st.session_state.current_q = None
    if 'user_answered' not in st.session_state:
        st.session_state.user_answered = False

    st.markdown(f"<div class='score-display' style='direction: rtl;'>اسکور: <span class='correct'>{st.session_state.practice_score}</span> / {st.session_state.practice_total}</div>", unsafe_allow_html=True)

    verbs = analyzer.verbs
    if not verbs:
        st.warning("No verbs available for practice.")
        return

    if not st.session_state.current_q or st.button("🔄 اگلا سوال (Next Question)"):
        st.session_state.current_q = _generate_question(analyzer, verbs)
        st.session_state.user_answered = False
        st.rerun()

    q = st.session_state.current_q
    if q:
        st.markdown(f"""
        <div style="background: #f6f6f2; padding: 20px; border-radius: 12px; margin: 15px 0; direction: rtl; text-align: right;">
            <h3 style="color: #92400e;">سوال: {q['question']}</h3>
        </div>
        """, unsafe_allow_html=True)

        selected_option = st.radio("درست جواب منتخب کریں (Select correct answer):", q['options'], key=f"q_{q['id']}")

        if st.button("پڑتال کریں (Check Answer)") and not st.session_state.user_answered:
            st.session_state.user_answered = True
            st.session_state.practice_total += 1
            if selected_option == q['correct_answer']:
                st.session_state.practice_score += 1
                analyzer.record_practice(q['verb_id'], True, q['q_type'])
                st.success(f"✅ درست جواب! (Correct!) - {q['explanation']}")
            else:
                analyzer.record_practice(q['verb_id'], False, q['q_type'])
                st.error(f"❌ غلط جواب! (Incorrect) - درست جواب تھا: {q['correct_answer']}\n\n{q['explanation']}")


def _generate_question(analyzer, verbs: list) -> dict:
    verb = random.choice(verbs)
    conjugations = analyzer.conjugation_engine.conjugate_verb(verb)
    past_list = conjugations.get('past_active', [])
    if not past_list:
        return None
        
    entry = random.choice(past_list)
    correct_ar = entry.get('arabic')
    pronoun = entry.get('pronoun_arabic')
    meaning_ur = entry.get('meaning_urdu')

    # Create distractor options from other conjugations
    distractors = set()
    for e in past_list:
        if e.get('arabic') != correct_ar:
            distractors.add(e.get('arabic'))
    
    while len(distractors) < 3:
        other_v = random.choice(verbs)
        other_c = analyzer.conjugation_engine.conjugate_verb(other_v).get('past_active', [])
        if other_c:
            distractors.add(random.choice(other_c).get('arabic'))

    distractors = list(distractors)[:3]
    options = distractors + [correct_ar]
    random.shuffle(options)

    return {
        "id": random.randint(1000, 9999),
        "verb_id": verb.get("id"),
        "q_type": "past_active_mcq",
        "question": f"«{meaning_ur}» کا درست عربی صیغہ کون سا ہے؟",
        "correct_answer": correct_ar,
        "options": options,
        "explanation": f"«{correct_ar}» = {pronoun} (ماضی معروف)، مادہ: {verb.get('root')}"
    }


def render_flashcard_mode(analyzer, lang: str = 'en', translations: dict = None):
    """Render flashcard study mode using SM-2."""
    st.title("🗂️ فلیش کارڈز (SM-2 Flashcards)")
    
    # Add New Cards button
    if st.button("➕ نئے کارڈز شامل کریں (Add New Cards)"):
        count = 0
        for verb in analyzer.verbs:
            card_id = f"{verb['id']}_meaning"
            card = analyzer.get_sm2_card(card_id)
            if not card:
                analyzer.update_sm2_card(card_id, verb['id'], 'meaning', 0) # Initialize
                count += 1
        if count > 0:
            st.success(f"{count} نئے کارڈز شامل کیے گئے! (Added {count} new cards)")
            st.rerun()
        else:
            st.info("تمام وربز کے کارڈز پہلے ہی موجود ہیں۔ (All cards already exist)")

    # Stats banner
    stats = analyzer.get_sm2_stats()
    st.markdown(f"""
    <div style='display: flex; justify-content: space-around; background: #1f2937; padding: 15px; border-radius: 10px; margin-bottom: 20px; direction: rtl; color: #ffffff;'>
        <div><b>کل کارڈز:</b> {stats['total_cards']}</div>
        <div><b>آج کے لیے باقی:</b> {stats['due_today']}</div>
        <div><b>اوسط آسانی (EF):</b> {stats['average_ef']}</div>
    </div>
    """, unsafe_allow_html=True)

    due_cards = analyzer.get_due_cards(limit=1)
    
    if not due_cards:
        if stats['total_cards'] > 0:
            st.success("🎉 زبردست! آج کے لیے کوئی کارڈ باقی نہیں۔ (Great! No cards due today.)")
        else:
            st.info("کارڈز شامل کرنے کے لیے اوپر دیا گیا بٹن دبائیں۔ (Click 'Add New Cards' to start.)")
        return

    current_card = due_cards[0]
    verb = current_card['verb']
    
    if not verb:
        st.error("Error: Verb data not found.")
        return

    if 'flashcard_flipped' not in st.session_state:
        st.session_state.flashcard_flipped = False

    front_text = verb.get('arabic', '')
    back_text = f"<b>مادہ:</b> {verb.get('root', '')}<br/><b>معنی:</b> {verb.get('meaning_urdu', '')}<br/><b>English:</b> {verb.get('meaning_english', '')}"
    
    card_content = front_text if not st.session_state.flashcard_flipped else back_text

    st.markdown(f"""
        <div class="flashcard" style="background: linear-gradient(135deg, #1a365d 0%, #14532d 100%); border-radius: 15px; padding: 40px; text-align: center; min-height: 200px; display: flex; align-items: center; justify-content: center; margin: 20px 0;">
            <div class="flashcard-text" style="font-size: 2.5em; color: #1f2937; direction: rtl;">
                {card_content}
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state.flashcard_flipped:
        if st.button("🔄 کارڈ الٹیں (Flip Card)", use_container_width=True):
            st.session_state.flashcard_flipped = True
            st.rerun()
    else:
        st.markdown("<p style='text-align: center; direction: rtl;'>آپ کو یہ کارڈ کیسا لگا؟ (How was this card?)</p>", unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns(4)
        
        def handle_rating(quality):
            card_id = current_card['card_id']
            verb_id = current_card['verb_id']
            card_type = current_card['card_type']
            updated = analyzer.update_sm2_card(card_id, verb_id, card_type, quality)
            # Truncate time for toast
            next_date = updated['next_review'][:10]
            st.session_state.flashcard_flipped = False
            # Streamlit doesn't support toast with return values easily here without extra session state, but we can just rerun
            st.toast(f"اگلا ریویو: {next_date}")
            
        with col1:
            if st.button("🔴 بالکل نہیں یاد (Again)", use_container_width=True):
                handle_rating(1)
                st.rerun()
        with col2:
            if st.button("🟠 مشکل (Hard)", use_container_width=True):
                handle_rating(2)
                st.rerun()
        with col3:
            if st.button("🟡 ٹھیک ہے (Good)", use_container_width=True):
                handle_rating(3)
                st.rerun()
        with col4:
            if st.button("🟢 بہت آسان (Easy)", use_container_width=True):
                handle_rating(5)
                st.rerun()

