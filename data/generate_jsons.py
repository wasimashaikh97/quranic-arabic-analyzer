import json

verbs = []

# helper to generate conjugations
def gen_conj(past, present, imperative, pass_past, pass_present, meaning_urdu, meaning_eng):
    # past, present, pass_past, pass_present are lists of 14 strings
    # imperative is list of 6 strings
    p_arab = ["هُوَ","هُمَا","هُمْ","هِيَ","هُمَا","هُنَّ","أَنْتَ","أَنْتُمَا","أَنْتُمْ","أَنْتِ","أَنْتُمَا","أَنْتُنَّ","أَنَا","نَحْنُ"]
    p_eng = ["He","They two (m)","They (m)","She","They two (f)","They (f)","You (m)","You two (m/f)","You all (m)","You (f)","You two (f)","You all (f)","I","We"]
    p_urd = ["اُس نے","اُن دونوں نے","اُن سب نے","اُس نے","اُن دونوں نے","اُن سب نے","تو نے","تم دونوں نے","تم سب نے","تو نے","تم دونوں نے","تم سب نے","میں نے","ہم نے"]
    prs = [3,3,3,3,3,3,2,2,2,2,2,2,1,1]
    gnd = ["masculine","masculine","masculine","feminine","feminine","feminine","masculine","masculine","masculine","feminine","feminine","feminine","common","common"]
    num = ["singular","dual","plural","singular","dual","plural","singular","dual","plural","singular","dual","plural","singular","plural"]
    
    past_act = []
    pres_act = []
    past_pas = []
    pres_pas = []
    
    for i in range(14):
        past_act.append({"pronoun_arabic": p_arab[i], "pronoun_english": p_eng[i], "pronoun_urdu": p_urd[i], "person": prs[i], "gender": gnd[i], "number": num[i], "arabic": past[i], "meaning_urdu": p_urd[i] + " " + meaning_urdu[0], "meaning_english": p_eng[i] + " " + meaning_eng[0]})
        pres_act.append({"pronoun_arabic": p_arab[i], "pronoun_english": p_eng[i], "pronoun_urdu": p_urd[i], "person": prs[i], "gender": gnd[i], "number": num[i], "arabic": present[i], "meaning_urdu": meaning_urdu[1], "meaning_english": p_eng[i] + " " + meaning_eng[1]})
        past_pas.append({"pronoun_arabic": p_arab[i], "pronoun_english": p_eng[i], "pronoun_urdu": p_urd[i], "person": prs[i], "gender": gnd[i], "number": num[i], "arabic": pass_past[i], "meaning_urdu": meaning_urdu[2], "meaning_english": p_eng[i] + " " + meaning_eng[2]})
        pres_pas.append({"pronoun_arabic": p_arab[i], "pronoun_english": p_eng[i], "pronoun_urdu": p_urd[i], "person": prs[i], "gender": gnd[i], "number": num[i], "arabic": pass_present[i], "meaning_urdu": meaning_urdu[3], "meaning_english": p_eng[i] + " " + meaning_eng[3]})

    # imperative
    imp = []
    pro = []
    imp_p_arab = p_arab[6:12]
    imp_p_eng = p_eng[6:12]
    imp_p_urd = p_urd[6:12]
    for i in range(6):
        imp.append({"pronoun_arabic": imp_p_arab[i], "pronoun_english": imp_p_eng[i], "pronoun_urdu": imp_p_urd[i], "person": 2, "gender": gnd[i+6], "number": num[i+6], "arabic": imperative[i], "meaning_urdu": meaning_urdu[4], "meaning_english": imp_p_eng[i] + " " + meaning_eng[4]})
        pro.append({"pronoun_arabic": imp_p_arab[i], "pronoun_english": imp_p_eng[i], "pronoun_urdu": imp_p_urd[i], "person": 2, "gender": gnd[i+6], "number": num[i+6], "arabic": "لَا " + present[i+6].replace("ُ","ْ").replace("ُونَ","ُوا").replace("َانِ","َا").replace("ِينَ","ِي"), "meaning_urdu": meaning_urdu[5], "meaning_english": "Do not " + meaning_eng[5]})

    return {"past_active": past_act, "present_active": pres_act, "past_passive": past_pas, "present_passive": pres_pas, "imperative": imp, "prohibition": pro}

# 1. kataba
v1 = {
    "id": "v001", "arabic": "كَتَبَ", "root": "ك ت ب", "root_letters": ["ك", "ت", "ب"], "form": 1, "form_name_arabic": "فَعَلَ", "pattern": "فَعَلَ", "masdar": "كِتَابَةً", "masdar_pattern": "فِعَالَة", "meaning_urdu": "لکھنا", "meaning_english": "to write", "verb_type": "sound", "transitivity": "transitive", "past_vowel": "a", "present_vowel": "u",
    "conjugations": gen_conj(
        ["كَتَبَ","كَتَبَا","كَتَبُوا","كَتَبَتْ","كَتَبَتَا","كَتَبْنَ","كَتَبْتَ","كَتَبْتُمَا","كَتَبْتُمْ","كَتَبْتِ","كَتَبْتُمَا","كَتَبْتُنَّ","كَتَبْتُ","كَتَبْنَا"],
        ["يَكْتُبُ","يَكْتُبَانِ","يَكْتُبُونَ","تَكْتُبُ","تَكْتُبَانِ","يَكْتُبْنَ","تَكْتُبُ","تَكْتُبَانِ","تَكْتُبُونَ","تَكْتُبِينَ","تَكْتُبَانِ","تَكْتُبْنَ","أَكْتُبُ","نَكْتُبُ"],
        ["اُكْتُبْ","اُكْتُبَا","اُكْتُبُوا","اُكْتُبِي","اُكْتُبَا","اُكْتُبْنَ"],
        ["كُتِبَ","كُتِبَا","كُتِبُوا","كُتِبَتْ","كُتِبَتَا","كُتِبْنَ","كُتِبْتَ","كُتِبْتُمَا","كُتِبْتُمْ","كُتِبْتِ","كُتِبْتُمَا","كُتِبْتُنَّ","كُتِبْتُ","كُتِبْنَا"],
        ["يُكْتَبُ","يُكْتَبَانِ","يُكْتَبُونَ","تُكْتَبُ","تُكْتَبَانِ","يُكْتَبْنَ","تُكْتَبُ","تُكْتَبَانِ","تُكْتَبُونَ","تُكْتَبِينَ","تُكْتَبَانِ","تُكْتَبْنَ","أُكْتَبُ","نُكْتَبُ"],
        ["لکھا","لکھتا ہے","لکھا گیا","لکھا جاتا ہے","لکھ","مت لکھ"],
        ["wrote","writes","was written","is written","write!","write!"]
    ),
    "derived_nouns": {"active_participle": {"arabic": "كَاتِب", "pattern": "فَاعِل", "meaning_urdu": "لکھنے والا", "meaning_english": "writer"}, "passive_participle": {"arabic": "مَكْتُوب", "pattern": "مَفْعُول", "meaning_urdu": "لکھا ہوا", "meaning_english": "written"}, "masdar": {"arabic": "كِتَابَةً", "pattern": "فِعَالَة", "meaning_urdu": "لکھنا", "meaning_english": "writing"}}
}
verbs.append(v1)

# 2. nasara
v2 = {
    "id": "v002", "arabic": "نَصَرَ", "root": "ن ص ر", "root_letters": ["ن", "ص", "ر"], "form": 1, "form_name_arabic": "فَعَلَ", "pattern": "فَعَلَ", "masdar": "نَصْرًا", "masdar_pattern": "فَعْل", "meaning_urdu": "مدد کرنا", "meaning_english": "to help", "verb_type": "sound", "transitivity": "transitive", "past_vowel": "a", "present_vowel": "u",
    "conjugations": gen_conj(
        ["نَصَرَ","نَصَرَا","نَصَرُوا","نَصَرَتْ","نَصَرَتَا","نَصَرْنَ","نَصَرْتَ","نَصَرْتُمَا","نَصَرْتُمْ","نَصَرْتِ","نَصَرْتُمَا","نَصَرْتُنَّ","نَصَرْتُ","نَصَرْنَا"],
        ["يَنْصُرُ","يَنْصُرَانِ","يَنْصُرُونَ","تَنْصُرُ","تَنْصُرَانِ","يَنْصُرْنَ","تَنْصُرُ","تَنْصُرَانِ","تَنْصُرُونَ","تَنْصُرِينَ","تَنْصُرَانِ","تَنْصُرْنَ","أَنْصُرُ","نَنْصُرُ"],
        ["اُنْصُرْ","اُنْصُرَا","اُنْصُرُوا","اُنْصُرِي","اُنْصُرَا","اُنْصُرْنَ"],
        ["نُصِرَ","نُصِرَا","نُصِرُوا","نُصِرَتْ","نُصِرَتَا","نُصِرْنَ","نُصِرْتَ","نُصِرْتُمَا","نُصِرْتُمْ","نُصِرْتِ","نُصِرْتُمَا","نُصِرْتُنَّ","نُصِرْتُ","نُصِرْنَا"],
        ["يُنْصَرُ","يُنْصَرَانِ","يُنْصَرُونَ","تُنْصَرُ","تُنْصَرَانِ","يُنْصَرْنَ","تُنْصَرُ","تُنْصَرَانِ","تُنْصَرُونَ","تُنْصَرِينَ","تُنْصَرَانِ","تُنْصَرْنَ","أُنْصَرُ","نُنْصَرُ"],
        ["مدد کی","مدد کرتا ہے","مدد کی گئی","مدد کی جاتی ہے","مدد کر","مدد مت کر"],
        ["helped","helps","was helped","is helped","help!","help!"]
    ),
    "derived_nouns": {"active_participle": {"arabic": "نَاصِر", "pattern": "فَاعِل", "meaning_urdu": "مدد کرنے والا", "meaning_english": "helper"}, "passive_participle": {"arabic": "مَنْصُور", "pattern": "مَفْعُول", "meaning_urdu": "جس کی مدد کی گئی", "meaning_english": "helped"}, "masdar": {"arabic": "نَصْرًا", "pattern": "فَعْل", "meaning_urdu": "مدد کرنا", "meaning_english": "helping"}}
}
verbs.append(v2)

# 3. daraba
v3 = {
    "id": "v003", "arabic": "ضَرَبَ", "root": "ض ر ب", "root_letters": ["ض", "ر", "ب"], "form": 1, "form_name_arabic": "فَعَلَ", "pattern": "فَعَلَ", "masdar": "ضَرْبًا", "masdar_pattern": "فَعْل", "meaning_urdu": "مارنا", "meaning_english": "to hit", "verb_type": "sound", "transitivity": "transitive", "past_vowel": "a", "present_vowel": "i",
    "conjugations": gen_conj(
        ["ضَرَبَ","ضَرَبَا","ضَرَبُوا","ضَرَبَتْ","ضَرَبَتَا","ضَرَبْنَ","ضَرَبْتَ","ضَرَبْتُمَا","ضَرَبْتُمْ","ضَرَبْتِ","ضَرَبْتُمَا","ضَرَبْتُنَّ","ضَرَبْتُ","ضَرَبْنَا"],
        ["يَضْرِبُ","يَضْرِبَانِ","يَضْرِبُونَ","تَضْرِبُ","تَضْرِبَانِ","يَضْرِبْنَ","تَضْرِبُ","تَضْرِبَانِ","تَضْرِبُونَ","تَضْرِبِينَ","تَضْرِبَانِ","تَضْرِبْنَ","أَضْرِبُ","نَضْرِبُ"],
        ["اِضْرِبْ","اِضْرِبَا","اِضْرِبُوا","اِضْرِبِي","اِضْرِبَا","اِضْرِبْنَ"],
        ["ضُرِبَ","ضُرِبَا","ضُرِبُوا","ضُرِبَتْ","ضُرِبَتَا","ضُرِبْنَ","ضُرِبْتَ","ضُرِبْتُمَا","ضُرِبْتُمْ","ضُرِبْتِ","ضُرِبْتُمَا","ضُرِبْتُنَّ","ضُرِبْتُ","ضُرِبْنَا"],
        ["يُضْرَبُ","يُضْرَبَانِ","يُضْرَبُونَ","تُضْرَبُ","تُضْرَبَانِ","يُضْرَبْنَ","تُضْرَبُ","تُضْرَبَانِ","تُضْرَبُونَ","تُضْرَبِينَ","تُضْرَبَانِ","تُضْرَبْنَ","أُضْرَبُ","نُضْرَبُ"],
        ["مارا","مارتا ہے","مارا گیا","مارا جاتا ہے","مار","مت مار"],
        ["hit","hits","was hit","is hit","hit!","hit!"]
    ),
    "derived_nouns": {"active_participle": {"arabic": "ضَارِب", "pattern": "فَاعِل", "meaning_urdu": "مارنے والا", "meaning_english": "striker"}, "passive_participle": {"arabic": "مَضْرُوب", "pattern": "مَفْعُول", "meaning_urdu": "مارا ہوا", "meaning_english": "struck"}, "masdar": {"arabic": "ضَرْبًا", "pattern": "فَعْل", "meaning_urdu": "مارنا", "meaning_english": "hitting"}}
}
verbs.append(v3)

# 4. fataha
v4 = {
    "id": "v004", "arabic": "فَتَحَ", "root": "ف ت ح", "root_letters": ["ف", "ت", "ح"], "form": 1, "form_name_arabic": "فَعَلَ", "pattern": "فَعَلَ", "masdar": "فَتْحًا", "masdar_pattern": "فَعْل", "meaning_urdu": "کھولنا", "meaning_english": "to open", "verb_type": "sound", "transitivity": "transitive", "past_vowel": "a", "present_vowel": "a",
    "conjugations": gen_conj(
        ["فَتَحَ","فَتَحَا","فَتَحُوا","فَتَحَتْ","فَتَحَتَا","فَتَحْنَ","فَتَحْتَ","فَتَحْتُمَا","فَتَحْتُمْ","فَتَحْتِ","فَتَحْتُمَا","فَتَحْتُنَّ","فَتَحْتُ","فَتَحْنَا"],
        ["يَفْتَحُ","يَفْتَحَانِ","يَفْتَحُونَ","تَفْتَحُ","تَفْتَحَانِ","يَفْتَحْنَ","تَفْتَحُ","تَفْتَحَانِ","تَفْتَحُونَ","تَفْتَحِينَ","تَفْتَحَانِ","تَفْتَحْنَ","أَفْتَحُ","نَفْتَحُ"],
        ["اِفْتَحْ","اِفْتَحَا","اِفْتَحُوا","اِفْتَحِي","اِفْتَحَا","اِفْتَحْنَ"],
        ["فُتِحَ","فُتِحَا","فُتِحُوا","فُتِحَتْ","فُتِحَتَا","فُتِحْنَ","فُتِحْتَ","فُتِحْتُمَا","فُتِحْتُمْ","فُتِحْتِ","فُتِحْتُمَا","فُتِحْتُنَّ","فُتِحْتُ","فُتِحْنَا"],
        ["يُفْتَحُ","يُفْتَحَانِ","يُفْتَحُونَ","تُفْتَحُ","تُفْتَحَانِ","يُفْتَحْنَ","تُفْتَحُ","تُفْتَحَانِ","تُفْتَحُونَ","تُفْتَحِينَ","تُفْتَحَانِ","تُفْتَحْنَ","أُفْتَحُ","نُفْتَحُ"],
        ["کھولا","کھولتا ہے","کھولا گیا","کھولا جاتا ہے","کھول","مت کھول"],
        ["opened","opens","was opened","is opened","open!","open!"]
    ),
    "derived_nouns": {"active_participle": {"arabic": "فَاتِح", "pattern": "فَاعِل", "meaning_urdu": "کھولنے والا", "meaning_english": "opener"}, "passive_participle": {"arabic": "مَفْتُوح", "pattern": "مَفْعُول", "meaning_urdu": "کھلا ہوا", "meaning_english": "opened"}, "masdar": {"arabic": "فَتْحًا", "pattern": "فَعْل", "meaning_urdu": "کھولنا", "meaning_english": "opening"}}
}
verbs.append(v4)

# 5. alima
v5 = {
    "id": "v005", "arabic": "عَلِمَ", "root": "ع ل م", "root_letters": ["ع", "ل", "م"], "form": 1, "form_name_arabic": "فَعِلَ", "pattern": "فَعِلَ", "masdar": "عِلْمًا", "masdar_pattern": "فِعْل", "meaning_urdu": "جاننا", "meaning_english": "to know", "verb_type": "sound", "transitivity": "transitive", "past_vowel": "i", "present_vowel": "a",
    "conjugations": gen_conj(
        ["عَلِمَ","عَلِمَا","عَلِمُوا","عَلِمَتْ","عَلِمَتَا","عَلِمْنَ","عَلِمْتَ","عَلِمْتُمَا","عَلِمْتُمْ","عَلِمْتِ","عَلِمْتُمَا","عَلِمْتُنَّ","عَلِمْتُ","عَلِمْنَا"],
        ["يَعْلَمُ","يَعْلَمَانِ","يَعْلَمُونَ","تَعْلَمُ","تَعْلَمَانِ","يَعْلَمْنَ","تَعْلَمُ","تَعْلَمَانِ","تَعْلَمُونَ","تَعْلَمِينَ","تَعْلَمَانِ","تَعْلَمْنَ","أَعْلَمُ","نَعْلَمُ"],
        ["اِعْلَمْ","اِعْلَمَا","اِعْلَمُوا","اِعْلَمِي","اِعْلَمَا","اِعْلَمْنَ"],
        ["عُلِمَ","عُلِمَا","عُلِمُوا","عُلِمَتْ","عُلِمَتَا","عُلِمْنَ","عُلِمْتَ","عُلِمْتُمَا","عُلِمْتُمْ","عُلِمْتِ","عُلِمْتُمَا","عُلِمْتُنَّ","عُلِمْتُ","عُلِمْنَا"],
        ["يُعْلَمُ","يُعْلَمَانِ","يُعْلَمُونَ","تُعْلَمُ","تُعْلَمَانِ","يُعْلَمْنَ","تُعْلَمُ","تُعْلَمَانِ","تُعْلَمُونَ","تُعْلَمِينَ","تُعْلَمَانِ","تُعْلَمْنَ","أُعْلَمُ","نُعْلَمُ"],
        ["جانا","جانتا ہے","جانا گیا","جانا جاتا ہے","جان لے","مت جان"],
        ["knew","knows","was known","is known","know!","know!"]
    ),
    "derived_nouns": {"active_participle": {"arabic": "عَالِم", "pattern": "فَاعِل", "meaning_urdu": "جاننے والا", "meaning_english": "knower"}, "passive_participle": {"arabic": "مَعْلُوم", "pattern": "مَفْعُول", "meaning_urdu": "معلوم شدہ", "meaning_english": "known"}, "masdar": {"arabic": "عِلْمًا", "pattern": "فِعْل", "meaning_urdu": "جاننا", "meaning_english": "knowing"}}
}
verbs.append(v5)

# 6. khalaqa
v6 = {
    "id": "v006", "arabic": "خَلَقَ", "root": "خ ل ق", "root_letters": ["خ", "ل", "ق"], "form": 1, "form_name_arabic": "فَعَلَ", "pattern": "فَعَلَ", "masdar": "خَلْقًا", "masdar_pattern": "فَعْل", "meaning_urdu": "پیدا کرنا", "meaning_english": "to create", "verb_type": "sound", "transitivity": "transitive", "past_vowel": "a", "present_vowel": "u",
    "conjugations": gen_conj(
        ["خَلَقَ","خَلَقَا","خَلَقُوا","خَلَقَتْ","خَلَقَتَا","خَلَقْنَ","خَلَقْتَ","خَلَقْتُمَا","خَلَقْتُمْ","خَلَقْتِ","خَلَقْتُمَا","خَلَقْتُنَّ","خَلَقْتُ","خَلَقْنَا"],
        ["يَخْلُقُ","يَخْلُقَانِ","يَخْلُقُونَ","تَخْلُقُ","تَخْلُقَانِ","يَخْلُقْنَ","تَخْلُقُ","تَخْلُقَانِ","تَخْلُقُونَ","تَخْلُقِينَ","تَخْلُقَانِ","تَخْلُقْنَ","أَخْلُقُ","نَخْلُقُ"],
        ["اُخْلُقْ","اُخْلُقَا","اُخْلُقُوا","اُخْلُقِي","اُخْلُقَا","اُخْلُقْنَ"],
        ["خُلِقَ","خُلِقَا","خُلِقُوا","خُلِقَتْ","خُلِقَتَا","خُلِقْنَ","خُلِقْتَ","خُلِقْتُمَا","خُلِقْتُمْ","خُلِقْتِ","خُلِقْتُمَا","خُلِقْتُنَّ","خُلِقْتُ","خُلِقْنَا"],
        ["يُخْلَقُ","يُخْلَقَانِ","يُخْلَقُونَ","تُخْلَقُ","تُخْلَقَانِ","يُخْلَقْنَ","تُخْلَقُ","تُخْلَقَانِ","تُخْلَقُونَ","تُخْلَقِينَ","تُخْلَقَانِ","تُخْلَقْنَ","أُخْلَقُ","نُخْلَقُ"],
        ["پیدا کیا","پیدا کرتا ہے","پیدا کیا گیا","پیدا کیا جاتا ہے","پیدا کر","مت پیدا کر"],
        ["created","creates","was created","is created","create!","create!"]
    ),
    "derived_nouns": {"active_participle": {"arabic": "خَالِق", "pattern": "فَاعِل", "meaning_urdu": "پیدا کرنے والا", "meaning_english": "creator"}, "passive_participle": {"arabic": "مَخْلُوق", "pattern": "مَفْعُول", "meaning_urdu": "مخلوق", "meaning_english": "created"}, "masdar": {"arabic": "خَلْقًا", "pattern": "فَعْل", "meaning_urdu": "پیدا کرنا", "meaning_english": "creating"}}
}
verbs.append(v6)

# 7. ja'ala
v7 = {
    "id": "v007", "arabic": "جَعَلَ", "root": "ج ع ل", "root_letters": ["ج", "ع", "ل"], "form": 1, "form_name_arabic": "فَعَلَ", "pattern": "فَعَلَ", "masdar": "جَعْلًا", "masdar_pattern": "فَعْل", "meaning_urdu": "بنانا / رکھنا", "meaning_english": "to make / place", "verb_type": "sound", "transitivity": "transitive", "past_vowel": "a", "present_vowel": "a",
    "conjugations": gen_conj(
        ["جَعَلَ","جَعَلَا","جَعَلُوا","جَعَلَتْ","جَعَلَتَا","جَعَلْنَ","جَعَلْتَ","جَعَلْتُمَا","جَعَلْتُمْ","جَعَلْتِ","جَعَلْتُمَا","جَعَلْتُنَّ","جَعَلْتُ","جَعَلْنَا"],
        ["يَجْعَلُ","يَجْعَلَانِ","يَجْعَلُونَ","تَجْعَلُ","تَجْعَلَانِ","يَجْعَلْنَ","تَجْعَلُ","تَجْعَلَانِ","تَجْعَلُونَ","تَجْعَلِينَ","تَجْعَلَانِ","تَجْعَلْنَ","أَجْعَلُ","نَجْعَلُ"],
        ["اِجْعَلْ","اِجْعَلَا","اِجْعَلُوا","اِجْعَلِي","اِجْعَلَا","اِجْعَلْنَ"],
        ["جُعِلَ","جُعِلَا","جُعِلُوا","جُعِلَتْ","جُعِلَتَا","جُعِلْنَ","جُعِلْتَ","جُعِلْتُمَا","جُعِلْتُمْ","جُعِلْتِ","جُعِلْتُمَا","جُعِلْتُنَّ","جُعِلْتُ","جُعِلْنَا"],
        ["يُجْعَلُ","يُجْعَلَانِ","يُجْعَلُونَ","تُجْعَلُ","تُجْعَلَانِ","يُجْعَلْنَ","تُجْعَلُ","تُجْعَلَانِ","تُجْعَلُونَ","تُجْعَلِينَ","تُجْعَلَانِ","تُجْعَلْنَ","أُجْعَلُ","نُجْعَلُ"],
        ["بنایا","بناتا ہے","بنایا گیا","بنایا جاتا ہے","بنا","مت بنا"],
        ["made","makes","was made","is made","make!","make!"]
    ),
    "derived_nouns": {"active_participle": {"arabic": "جَاعِل", "pattern": "فَاعِل", "meaning_urdu": "بنانے والا", "meaning_english": "maker"}, "passive_participle": {"arabic": "مَجْعُول", "pattern": "مَفْعُول", "meaning_urdu": "بنایا ہوا", "meaning_english": "made"}, "masdar": {"arabic": "جَعْلًا", "pattern": "فَعْل", "meaning_urdu": "بنانا", "meaning_english": "making"}}
}
verbs.append(v7)

# 8. dakhala
v8 = {
    "id": "v008", "arabic": "دَخَلَ", "root": "د خ ل", "root_letters": ["د", "خ", "ل"], "form": 1, "form_name_arabic": "فَعَلَ", "pattern": "فَعَلَ", "masdar": "دُخُولًا", "masdar_pattern": "فُعُول", "meaning_urdu": "داخل ہونا", "meaning_english": "to enter", "verb_type": "sound", "transitivity": "intransitive", "past_vowel": "a", "present_vowel": "u",
    "conjugations": gen_conj(
        ["دَخَلَ","دَخَلَا","دَخَلُوا","دَخَلَتْ","دَخَلَتَا","دَخَلْنَ","دَخَلْتَ","دَخَلْتُمَا","دَخَلْتُمْ","دَخَلْتِ","دَخَلْتُمَا","دَخَلْتُنَّ","دَخَلْتُ","دَخَلْنَا"],
        ["يَدْخُلُ","يَدْخُلَانِ","يَدْخُلُونَ","تَدْخُلُ","تَدْخُلَانِ","يَدْخُلْنَ","تَدْخُلُ","تَدْخُلَانِ","تَدْخُلُونَ","تَدْخُلِينَ","تَدْخُلَانِ","تَدْخُلْنَ","أَدْخُلُ","نَدْخُلُ"],
        ["اُدْخُلْ","اُدْخُلَا","اُدْخُلُوا","اُدْخُلِي","اُدْخُلَا","اُدْخُلْنَ"],
        ["دُخِلَ","دُخِلَا","دُخِلُوا","دُخِلَتْ","دُخِلَتَا","دُخِلْنَ","دُخِلْتَ","دُخِلْتُمَا","دُخِلْتُمْ","دُخِلْتِ","دُخِلْتُمَا","دُخِلْتُنَّ","دُخِلْتُ","دُخِلْنَا"],
        ["يُدْخَلُ","يُدْخَلَانِ","يُدْخَلُونَ","تُدْخَلُ","تُدْخَلَانِ","يُدْخَلْنَ","تُدْخَلُ","تُدْخَلَانِ","تُدْخَلُونَ","تُدْخَلِينَ","تُدْخَلَانِ","تُدْخَلْنَ","أُدْخَلُ","نُدْخَلُ"],
        ["داخل ہوا","داخل ہوتا ہے","داخل کیا گیا","داخل کیا جاتا ہے","داخل ہو","داخل مت ہو"],
        ["entered","enters","was entered","is entered","enter!","enter!"]
    ),
    "derived_nouns": {"active_participle": {"arabic": "دَاخِل", "pattern": "فَاعِل", "meaning_urdu": "داخل ہونے والا", "meaning_english": "enterer"}, "passive_participle": {"arabic": "مَدْخُول", "pattern": "مَفْعُول", "meaning_urdu": "جس میں داخل ہوا گیا", "meaning_english": "entered"}, "masdar": {"arabic": "دُخُولًا", "pattern": "فُعُول", "meaning_urdu": "داخل ہونا", "meaning_english": "entering"}}
}
verbs.append(v8)

# 9. kharaja
v9 = {
    "id": "v009", "arabic": "خَرَجَ", "root": "خ ر ج", "root_letters": ["خ", "ر", "ج"], "form": 1, "form_name_arabic": "فَعَلَ", "pattern": "فَعَلَ", "masdar": "خُرُوجًا", "masdar_pattern": "فُعُول", "meaning_urdu": "نکلنا", "meaning_english": "to exit", "verb_type": "sound", "transitivity": "intransitive", "past_vowel": "a", "present_vowel": "u",
    "conjugations": gen_conj(
        ["خَرَجَ","خَرَجَا","خَرَجُوا","خَرَجَتْ","خَرَجَتَا","خَرَجْنَ","خَرَجْتَ","خَرَجْتُمَا","خَرَجْتُمْ","خَرَجْتِ","خَرَجْتُمَا","خَرَجْتُنَّ","خَرَجْتُ","خَرَجْنَا"],
        ["يَخْرُجُ","يَخْرُجَانِ","يَخْرُجُونَ","تَخْرُجُ","تَخْرُجَانِ","يَخْرُجْنَ","تَخْرُجُ","تَخْرُجَانِ","تَخْرُجُونَ","تَخْرُجِينَ","تَخْرُجَانِ","تَخْرُجْنَ","أَخْرُجُ","نَخْرُجُ"],
        ["اُخْرُجْ","اُخْرُجَا","اُخْرُجُوا","اُخْرُجِي","اُخْرُجَا","اُخْرُجْنَ"],
        ["خُرِجَ","خُرِجَا","خُرِجُوا","خُرِجَتْ","خُرِجَتَا","خُرِجْنَ","خُرِجْتَ","خُرِجْتُمَا","خُرِجْتُمْ","خُرِجْتِ","خُرِجْتُمَا","خُرِجْتُنَّ","خُرِجْتُ","خُرِجْنَا"],
        ["يُخْرَجُ","يُخْرَجَانِ","يُخْرَجُونَ","تُخْرَجُ","تُخْرَجَانِ","يُخْرَجْنَ","تُخْرَجُ","تُخْرَجَانِ","تُخْرَجُونَ","تُخْرَجِينَ","تُخْرَجَانِ","تُخْرَجْنَ","أُخْرَجُ","نُخْرَجُ"],
        ["نکلا","نکلتا ہے","نکالا گیا","نکالا جاتا ہے","نکل","مت نکل"],
        ["exited","exits","was taken out","is taken out","exit!","exit!"]
    ),
    "derived_nouns": {"active_participle": {"arabic": "خَارِج", "pattern": "فَاعِل", "meaning_urdu": "نکلنے والا", "meaning_english": "exiter"}, "passive_participle": {"arabic": "مَخْرُوج", "pattern": "مَفْعُول", "meaning_urdu": "نکالا ہوا", "meaning_english": "exited"}, "masdar": {"arabic": "خُرُوجًا", "pattern": "فُعُول", "meaning_urdu": "نکلنا", "meaning_english": "exiting"}}
}
verbs.append(v9)

# 10. qala (hollow)
v10 = {
    "id": "v010", "arabic": "قَالَ", "root": "ق و ل", "root_letters": ["ق", "و", "ل"], "form": 1, "form_name_arabic": "فَعَلَ", "pattern": "فَعَلَ", "masdar": "قَوْلًا", "masdar_pattern": "فَعْل", "meaning_urdu": "کہنا", "meaning_english": "to say", "verb_type": "hollow", "transitivity": "transitive", "past_vowel": "a", "present_vowel": "u",
    "conjugations": gen_conj(
        ["قَالَ","قَالَا","قَالُوا","قَالَتْ","قَالَتَا","قُلْنَ","قُلْتَ","قُلْتُمَا","قُلْتُمْ","قُلْتِ","قُلْتُمَا","قُلْتُنَّ","قُلْتُ","قُلْنَا"],
        ["يَقُولُ","يَقُولَانِ","يَقُولُونَ","تَقُولُ","تَقُولَانِ","يَقُلْنَ","تَقُولُ","تَقُولَانِ","تَقُولُونَ","تَقُولِينَ","تَقُولَانِ","تَقُلْنَ","أَقُولُ","نَقُولُ"],
        ["قُلْ","قُولَا","قُولُوا","قُولِي","قُولَا","قُلْنَ"],
        ["قِيلَ","قِيلَا","قِيلُوا","قِيلَتْ","قِيلَتَا","قِلْنَ","قِلْتَ","قِلْتُمَا","قِلْتُمْ","قِلْتِ","قِلْتُمَا","قِلْتُنَّ","قِلْتُ","قِلْنَا"],
        ["يُقَالُ","يُقَالَانِ","يُقَالُونَ","تُقَالُ","تُقَالَانِ","يُقَلْنَ","تُقَالُ","تُقَالَانِ","تُقَالُونَ","تُقَالِينَ","تُقَالَانِ","تُقَلْنَ","أُقَالُ","نُقَالُ"],
        ["کہا","کہتا ہے","کہا گیا","کہا جاتا ہے","کہہ","مت کہہ"],
        ["said","says","was said","is said","say!","say!"]
    ),
    "derived_nouns": {"active_participle": {"arabic": "قَائِل", "pattern": "فَاعِل", "meaning_urdu": "کہنے والا", "meaning_english": "speaker"}, "passive_participle": {"arabic": "مَقُول", "pattern": "مَفْعُول", "meaning_urdu": "کہا گیا", "meaning_english": "said"}, "masdar": {"arabic": "قَوْلًا", "pattern": "فَعْل", "meaning_urdu": "کہنا", "meaning_english": "saying"}}
}
verbs.append(v10)

# 11. da'aa (defective waw)
v11 = {
    "id": "v011", "arabic": "دَعَا", "root": "د ع و", "root_letters": ["د", "ع", "و"], "form": 1, "form_name_arabic": "فَعَلَ", "pattern": "فَعَلَ", "masdar": "دُعَاءً", "masdar_pattern": "فُعَال", "meaning_urdu": "پکارنا / دعا کرنا", "meaning_english": "to call / pray", "verb_type": "defective", "transitivity": "transitive", "past_vowel": "a", "present_vowel": "u",
    "derived_nouns": {"active_participle": {"arabic": "دَاعٍ", "pattern": "فَاعٍ", "meaning_urdu": "پکارنے والا", "meaning_english": "caller"}, "passive_participle": {"arabic": "مَدْعُوّ", "pattern": "مَفْعُول", "meaning_urdu": "جس کو پکارا گیا", "meaning_english": "called"}, "masdar": {"arabic": "دُعَاءً", "pattern": "فُعَال", "meaning_urdu": "دعا", "meaning_english": "supplication"}}
}
verbs.append(v11)

# 12. ramaa (defective ya)
v12 = {
    "id": "v012", "arabic": "رَمَى", "root": "ر م ي", "root_letters": ["ر", "م", "ي"], "form": 1, "form_name_arabic": "فَعَلَ", "pattern": "فَعَلَ", "masdar": "رَمْيًا", "masdar_pattern": "فَعْل", "meaning_urdu": "پھینکنا / تیر چلانا", "meaning_english": "to throw", "verb_type": "defective", "transitivity": "transitive", "past_vowel": "a", "present_vowel": "i",
    "derived_nouns": {"active_participle": {"arabic": "رَامٍ", "pattern": "فَاعٍ", "meaning_urdu": "پھینکنے والا", "meaning_english": "thrower"}, "passive_participle": {"arabic": "مَرْمِيّ", "pattern": "مَفْعُول", "meaning_urdu": "پھینکا ہوا", "meaning_english": "thrown"}, "masdar": {"arabic": "رَمْيًا", "pattern": "فَعْل", "meaning_urdu": "پھینکنا", "meaning_english": "throwing"}}
}
verbs.append(v12)

# 13. wa'ada (assimilated)
v13 = {
    "id": "v013", "arabic": "وَعَدَ", "root": "و ع د", "root_letters": ["و", "ع", "د"], "form": 1, "form_name_arabic": "فَعَلَ", "pattern": "فَعَلَ", "masdar": "وَعْدًا", "masdar_pattern": "فَعْل", "meaning_urdu": "وعدہ کرنا", "meaning_english": "to promise", "verb_type": "assimilated", "transitivity": "transitive", "past_vowel": "a", "present_vowel": "i",
    "derived_nouns": {"active_participle": {"arabic": "وَاعِد", "pattern": "فَاعِل", "meaning_urdu": "وعدہ کرنے والا", "meaning_english": "promiser"}, "passive_participle": {"arabic": "مَوْعُود", "pattern": "مَفْعُول", "meaning_urdu": "جس کا وعدہ کیا گیا", "meaning_english": "promised"}, "masdar": {"arabic": "وَعْدًا", "pattern": "فَعْل", "meaning_urdu": "وعدہ", "meaning_english": "promise"}}
}
verbs.append(v13)

# 14. radda (doubled)
v14 = {
    "id": "v014", "arabic": "رَدَّ", "root": "ر د د", "root_letters": ["ر", "د", "د"], "form": 1, "form_name_arabic": "فَعَلَ", "pattern": "فَعَلَ", "masdar": "رَدًّا", "masdar_pattern": "فَعْل", "meaning_urdu": "لوٹانا / جواب دینا", "meaning_english": "to return / reject", "verb_type": "doubled", "transitivity": "transitive", "past_vowel": "a", "present_vowel": "u",
    "derived_nouns": {"active_participle": {"arabic": "رَادّ", "pattern": "فَاعِل", "meaning_urdu": "لوٹانے والا", "meaning_english": "rejecter"}, "passive_participle": {"arabic": "مَرْدُود", "pattern": "مَفْعُول", "meaning_urdu": "لوٹایا ہوا", "meaning_english": "rejected"}, "masdar": {"arabic": "رَدًّا", "pattern": "فَعْل", "meaning_urdu": "لوٹانا", "meaning_english": "returning"}}
}
verbs.append(v14)

# 15. akala (hamzated)
v15 = {
    "id": "v015", "arabic": "أَكَلَ", "root": "أ ك ل", "root_letters": ["أ", "ك", "ل"], "form": 1, "form_name_arabic": "فَعَلَ", "pattern": "فَعَلَ", "masdar": "أَكْلًا", "masdar_pattern": "فَعْل", "meaning_urdu": "کھانا", "meaning_english": "to eat", "verb_type": "hamzated", "transitivity": "transitive", "past_vowel": "a", "present_vowel": "u",
    "derived_nouns": {"active_participle": {"arabic": "آكِل", "pattern": "فَاعِل", "meaning_urdu": "کھانے والا", "meaning_english": "eater"}, "passive_participle": {"arabic": "مَأْكُول", "pattern": "مَفْعُول", "meaning_urdu": "کھایا ہوا", "meaning_english": "eaten"}, "masdar": {"arabic": "أَكْلًا", "pattern": "فَعْل", "meaning_urdu": "کھانا", "meaning_english": "eating"}}
}
verbs.append(v15)

# 16. arsala (Form IV)
v16 = {
    "id": "v016", "arabic": "أَرْسَلَ", "root": "ر س ل", "root_letters": ["ر", "س", "ل"], "form": 4, "form_name_arabic": "أَفْعَلَ", "pattern": "أَفْعَلَ", "masdar": "إِرْسَالًا", "masdar_pattern": "إِفْعَال", "meaning_urdu": "بھیجنا", "meaning_english": "to send", "verb_type": "sound", "transitivity": "transitive",
    "derived_nouns": {"active_participle": {"arabic": "مُرْسِل", "pattern": "مُفْعِل", "meaning_urdu": "بھیجنے والا", "meaning_english": "sender"}, "passive_participle": {"arabic": "مُرْسَل", "pattern": "مُفْعَل", "meaning_urdu": "بھیجا ہوا (رسول)", "meaning_english": "sent one / messenger"}, "masdar": {"arabic": "إِرْسَالًا", "pattern": "إِفْعَال", "meaning_urdu": "بھیجنا", "meaning_english": "sending"}}
}
verbs.append(v16)

from pathlib import Path
out_path = Path(__file__).parent / "verbs.json"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump({"verbs": verbs}, f, ensure_ascii=False, indent=2)

print(f"Generated {len(verbs)} verbs in verbs.json")

