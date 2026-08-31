import streamlit as st
import streamlit.components.v1 as components

def render_compare_view(analyzer, lang: str = 'en', translations: dict = None, font_scale: float = 1.0):
    st.markdown("<h2>⚖️ تقابل — Verb Comparison</h2>", unsafe_allow_html=True)
    
    if translations is None:
        translations = {}

    def t(key):
        return translations.get(key, key)

    verbs = getattr(analyzer, 'verbs', [])
    if not verbs:
        st.warning("No verbs available for comparison." if lang == 'en' else "تقابل کے لیے کوئی افعال دستیاب نہیں۔")
        return

    verb_options = {
        i: f"{v.get('arabic', '')} — {v.get('meaning_urdu', '')} ({v.get('meaning_english', '')})"
        for i, v in enumerate(verbs)
    }

    col1, col2 = st.columns([1, 1])
    
    with col1:
        v1_idx = st.selectbox("پہلا فعل (First Verb)", options=list(verb_options.keys()), format_func=lambda x: verb_options[x], key="v1_select")
    
    with col2:
        v2_idx = st.selectbox("دوسرا فعل (Second Verb)", options=list(verb_options.keys()), format_func=lambda x: verb_options[x], key="v2_select")

    if v1_idx is not None and v2_idx is not None:
        v1 = verbs[v1_idx]
        v2 = verbs[v2_idx]

        st.markdown("### بنیادی معلومات (Basic Info)")
        
        # Helper to highlight differences
        def hl(val1, val2, current_val, is_v1=True):
            color = "#f59e0b" if is_v1 else "#38bdf8"
            if val1 != val2:
                return f"<span style='color: #ef4444; font-weight: bold;'>{current_val}</span>"
            return f"<span style='color: {color};'>{current_val}</span>"

        info_html = f"""
        <div dir="rtl" style="display: flex; justify-content: space-between; background-color: #1a202c; padding: 20px; border-radius: 10px; color: white;">
            <div style="width: 48%; padding: 10px; border-left: 1px solid #4a5568;">
                <h4 style="color: #f59e0b; text-align: center;">{v1.get('arabic', '')}</h4>
                <p><b>مادہ (Root):</b> {hl(v1.get('root'), v2.get('root'), v1.get('root'), True)}</p>
                <p><b>باب (Form/Pattern):</b> {hl(v1.get('pattern', v1.get('form')), v2.get('pattern', v2.get('form')), v1.get('pattern', v1.get('form')), True)}</p>
                <p><b>مصدر (Masdar):</b> {hl(v1.get('masdar'), v2.get('masdar'), v1.get('masdar'), True)}</p>
                <p><b>قسم (Type):</b> {hl(v1.get('verb_type'), v2.get('verb_type'), v1.get('verb_type'), True)}</p>
                <p><b>لازم/متعدی (Transitivity):</b> {hl(v1.get('transitivity'), v2.get('transitivity'), v1.get('transitivity'), True)}</p>
                <p><b>معنی (Urdu):</b> {v1.get('meaning_urdu', '')}</p>
                <p><b>Meaning (English):</b> {v1.get('meaning_english', '')}</p>
            </div>
            <div style="width: 48%; padding: 10px;">
                <h4 style="color: #38bdf8; text-align: center;">{v2.get('arabic', '')}</h4>
                <p><b>مادہ (Root):</b> {hl(v1.get('root'), v2.get('root'), v2.get('root'), False)}</p>
                <p><b>باب (Form/Pattern):</b> {hl(v1.get('pattern', v1.get('form')), v2.get('pattern', v2.get('form')), v2.get('pattern', v2.get('form')), False)}</p>
                <p><b>مصدر (Masdar):</b> {hl(v1.get('masdar'), v2.get('masdar'), v2.get('masdar'), False)}</p>
                <p><b>قسم (Type):</b> {hl(v1.get('verb_type'), v2.get('verb_type'), v2.get('verb_type'), False)}</p>
                <p><b>لازم/متعدی (Transitivity):</b> {hl(v1.get('transitivity'), v2.get('transitivity'), v2.get('transitivity'), False)}</p>
                <p><b>معنی (Urdu):</b> {v2.get('meaning_urdu', '')}</p>
                <p><b>Meaning (English):</b> {v2.get('meaning_english', '')}</p>
            </div>
        </div>
        """
        st.markdown(info_html, unsafe_allow_html=True)

        conj1 = analyzer.conjugation_engine.conjugate_verb(v1) if hasattr(analyzer, 'conjugation_engine') else {}
        conj2 = analyzer.conjugation_engine.conjugate_verb(v2) if hasattr(analyzer, 'conjugation_engine') else {}

        def get_conj_list(conj, tense):
            return conj.get(tense, [])

        past1 = get_conj_list(conj1, 'past')
        past2 = get_conj_list(conj2, 'past')

        present1 = get_conj_list(conj1, 'present')
        present2 = get_conj_list(conj2, 'present')

        def build_table(title, data1, data2):
            rows = ""
            length = max(len(data1), len(data2), 14)
            for i in range(length):
                d1 = data1[i] if i < len(data1) else {}
                d2 = data2[i] if i < len(data2) else {}
                
                pronoun = d1.get('pronoun_arabic', d2.get('pronoun_arabic', ''))
                
                rows += f"""
                <tr>
                    <td style="text-align: center; border: 1px solid #4a5568; padding: 8px;">{pronoun}</td>
                    <td style="text-align: center; color: #f59e0b; font-family: 'Noto Naskh Arabic', serif; font-size: {1.2 * font_scale}em; border: 1px solid #4a5568; padding: 8px;">{d1.get('arabic', '')}</td>
                    <td style="text-align: center; border: 1px solid #4a5568; padding: 8px;">{d1.get('urdu', '')}</td>
                    <td style="text-align: center; color: #38bdf8; font-family: 'Noto Naskh Arabic', serif; font-size: {1.2 * font_scale}em; border: 1px solid #4a5568; padding: 8px;">{d2.get('arabic', '')}</td>
                    <td style="text-align: center; border: 1px solid #4a5568; padding: 8px;">{d2.get('urdu', '')}</td>
                </tr>
                """
            
            html = f"""
            <div dir="rtl" style="background-color: #1a202c; color: white; padding: 10px; border-radius: 5px;">
                <h3 style="color: #2b6cb0; text-align: center; margin-bottom: 10px;">{title}</h3>
                <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
                    <thead style="background-color: #2d3748;">
                        <tr>
                            <th style="border: 1px solid #4a5568; padding: 10px;">ضمیر</th>
                            <th style="border: 1px solid #4a5568; padding: 10px; color: #f59e0b;">عربی 1</th>
                            <th style="border: 1px solid #4a5568; padding: 10px; color: #f59e0b;">اردو 1</th>
                            <th style="border: 1px solid #4a5568; padding: 10px; color: #38bdf8;">عربی 2</th>
                            <th style="border: 1px solid #4a5568; padding: 10px; color: #38bdf8;">اردو 2</th>
                        </tr>
                    </thead>
                    <tbody>
                        {rows}
                    </tbody>
                </table>
            </div>
            """
            return html

        if past1 or past2:
            st.markdown("### ماضی (Past Tense)")
            past_html = build_table("ماضی (Past Tense)", past1, past2)
            components.html(past_html, height=60 + 14 * 50, scrolling=True)

        if present1 or present2:
            st.markdown("### مضارع (Present Tense)")
            present_html = build_table("مضارع (Present Tense)", present1, present2)
            components.html(present_html, height=60 + 14 * 50, scrolling=True)
            
        st.markdown("### مشتقات (Derived Forms)")
        d_html = f"""
        <div dir="rtl" style="display: flex; justify-content: space-between; background-color: #1a202c; padding: 20px; border-radius: 10px; color: white;">
            <div style="width: 48%; padding: 10px; border-left: 1px solid #4a5568;">
                <h4 style="color: #f59e0b; text-align: center;">{v1.get('arabic', '')}</h4>
                <p><b>اسم الفاعل:</b> <span style="font-family: 'Noto Naskh Arabic', serif; font-size: {1.2 * font_scale}em;">{v1.get('derived_nouns', {{}}).get('ism_faail', '')}</span></p>
                <p><b>اسم المفعول:</b> <span style="font-family: 'Noto Naskh Arabic', serif; font-size: {1.2 * font_scale}em;">{v1.get('derived_nouns', {{}}).get('ism_mafool', '')}</span></p>
                <p><b>اسم الظرف:</b> <span style="font-family: 'Noto Naskh Arabic', serif; font-size: {1.2 * font_scale}em;">{v1.get('derived_nouns', {{}}).get('ism_zarf', '')}</span></p>
                <p><b>اسم الآلة:</b> <span style="font-family: 'Noto Naskh Arabic', serif; font-size: {1.2 * font_scale}em;">{v1.get('derived_nouns', {{}}).get('ism_aala', '')}</span></p>
            </div>
            <div style="width: 48%; padding: 10px;">
                <h4 style="color: #38bdf8; text-align: center;">{v2.get('arabic', '')}</h4>
                <p><b>اسم الفاعل:</b> <span style="font-family: 'Noto Naskh Arabic', serif; font-size: {1.2 * font_scale}em;">{v2.get('derived_nouns', {{}}).get('ism_faail', '')}</span></p>
                <p><b>اسم المفعول:</b> <span style="font-family: 'Noto Naskh Arabic', serif; font-size: {1.2 * font_scale}em;">{v2.get('derived_nouns', {{}}).get('ism_mafool', '')}</span></p>
                <p><b>اسم الظرف:</b> <span style="font-family: 'Noto Naskh Arabic', serif; font-size: {1.2 * font_scale}em;">{v2.get('derived_nouns', {{}}).get('ism_zarf', '')}</span></p>
                <p><b>اسم الآلة:</b> <span style="font-family: 'Noto Naskh Arabic', serif; font-size: {1.2 * font_scale}em;">{v2.get('derived_nouns', {{}}).get('ism_aala', '')}</span></p>
            </div>
        </div>
        """
        st.markdown(d_html, unsafe_allow_html=True)
