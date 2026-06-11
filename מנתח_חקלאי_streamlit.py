"""
מנת"ח חקלאי v9 — Streamlit Edition
מערכת ניתוח תכנוני לחוות דעת חקלאית — משרד החקלאות וביטחון המזון
"""
import streamlit as st
from google import genai as google_genai
from google.genai import types as genai_types
import json
import os
from io import BytesIO
from datetime import date
import pandas as pd

# ─────────────────────────────────────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title='מנת"ח חקלאי',
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Heebo:wght@300;400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Heebo', sans-serif !important; direction: rtl; }
.stMarkdown p, .stMarkdown li, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 { text-align: right; }
.stAlert > div { text-align: right; }
div[data-testid="stMetricLabel"] > div { text-align: right; }
div[data-testid="stMetricValue"] { text-align: right; }
</style>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
#  CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────
YISHUVIM = [
    "אבו גוש","אבו סנאן","אבו קרינאת","אבטין","אביאל","אביגדור","אביחיל",
    "אביטל","אבירים","אבן מנחם","אבן ספיר","אבן שמואל","אבנת","אודים",
    "אודם","אוחד","אופקים","אור הגנוז","אור הנר","אור יהודה","אור עקיבא",
    "אורה","אורות","אורים","אורנים","אורנית","אושה","אזור","אחווה",
    "אחוזם","אחוזת ברק","אחיהוד","אחיטוב","אחיסמך","אחיעזר","איבים",
    "איילון","איילת השחר","אילון","אילות","אילניה","אכסאל","אל-בטוף",
    "אלומה","אלומות","אלון הגליל","אלון מורה","אלון שבות","אלוני אבא",
    "אלוני הבשן","אלוני יצחק","אלונים","אלי-עד","אליאב","אליכין",
    "אלישיב","אלישמע","אלמגור","אלמוג","אלעד","אלעזר","אלפי מנשה",
    "אלקוש","אלקנה","אמירים","אמציה","אניעם","אספר","אעבלין","אפיק",
    "אפיקים","אפק","אפרת","ארבל","ארגמן","ארז","אשבול","אשדוד",
    "אשדות יעקב איחוד","אשדות יעקב מאוחד","אשוח","אשחר","אשכולות",
    "אשל הנשיא","אשלים","אשקלון","אשרת","אשתאול",
    "באקה אל-גרביה","באר גנים","באר טוביה","באר יעקב","באר מילכה",
    "באר שבע","בארות יצחק","בארותיים","בארי","בוסתן הגליל",
    "בועיינה נוגידאת","בוקעתא","בור שחורה","ביצרון","ביר אל-מכסור",
    "בירייה","בית אורן","בית אל","בית אלעזרי","בית אלפא","בית אריה",
    "בית ברל","בית גוברין","בית גן","בית דגן","בית הגדי","בית הלוי",
    "בית הלל","בית העמק","בית הערבה","בית זיד","בית זית","בית זרע",
    "בית חגי","בית חורון","בית חירות","בית חלקיה","בית חנן","בית חנניה",
    "בית חשמונאי","בית יהושע","בית יוסף","בית ינאי","בית יצחק-שער חפר",
    "בית כנף","בית לחם הגלילית","בית מאיר","בית נחמיה","בית ניר",
    "בית נקופה","בית עובד","בית עוזיאל","בית עזרא","בית עין","בית עריף",
    "בית קמה","בית קשת","בית רבן","בית רימון","בית שאן","בית שמש",
    "בית שערים","בית שקמה","ביתן אהרן","ביתר עילית","בן זכאי","בן עמי",
    "בן שמן","בני ברק","בני דרום","בני דרר","בני יהודה","בני עטרות",
    "בני עיש","בנימינה-גבעת עדה","בסמה","בסמת טבעון","בענה","בצרה",
    "בצת","בקוע","בקעות","בר גיורא","בר יוחאי","ברוכין","ברור חיל",
    "ברכה","ברכיה","ברעם","ברקאי","ברקן","ברקת","בת הדר","בת חן",
    "בת חפר","בת ים","בת עין","בת שלמה",
    "גאולה","גאולי תימן","גאליה","גבולות","גבים","גבע","גבע בנימין",
    "גבע כרמל","גבעון החדשה","גבעות בר","גבעת אבני","גבעת ברנר",
    "גבעת השלושה","גבעת יואב","גבעת יערים","גבעת נילי","גבעת עוז",
    "גבעת שמואל","גבעת שפירא","גבעתי","גבעתיים","גברעם","גדות","גדיש",
    "גדעונה","גולן","גונן","גורן","גורנות הגליל","גזית","גזר","גיאה",
    "גיבתון","גיזו","גיל עם","גילון","גילת","גינוסר","גיניגר","גינתון",
    "גלאון","גלגל","גליל ים","גמזו","גן הדרום","גן השומרון","גן חיים",
    "גן יאשיה","גן יבנה","גן נר","גן שורק","גן שלמה","גן שמואל",
    "גנות","גנות הדר","גני טל","גני יוחנן","גני מודיעין","גני תקווה",
    "גנר","געש","גפן","גרופית","גשר","גשר הזיו","גשרון","גת","גת רימון",
    "דבורה","דבוריה","דברת","דגניה א","דגניה ב","דובב","דור","דורות",
    "דחי","דייר חנא","דימונה","דיר אל-אסד","דיר חנא","דישון","דלייה",
    "דלתון","דן","דפנה","דקל",
    "האון","הבונים","הגושרים","הוד השרון","הושעיה","הזורע","הזורעים",
    "החותרים","הילה","הכפר הירוק","המעפיל","הסוללים","העוגן","הר אדר",
    "הר גילה","הר עמשא","הראל","הרדוף","הרצליה","הררית",
    "זוהר","זיקים","זיתן","זכרון יעקב","זמר","זנוח","זרועה","זרזיר",
    "חבצלת השרון","חגור","חגי","חגלה","חד-נס","חדיד","חדרה","חולדה",
    "חולון","חולית","חולתה","חוסן","חוסנייה","חופית","חוקוק","חורה",
    "חורפיש","חורשים","חיבת ציון","חיפה","חירות","חכליל","חלוץ",
    "חלמיש","חמד","חמדיה","חמדת","חמרה","חמת גדר","חניאל","חניתה",
    "חנתון","חספין","חפץ חיים","חצב","חצבה","חצור הגלילית","חצור-אשדוד",
    "חצרים","חרב לאת","חרוצים","חריש","חרמש","חרשים","חשמונאים",
    "טבריה","טובא-זנגריה","טורעאן","טייבה","טייבה בעמק","טירה",
    "טירת יהודה","טירת כרמל","טירת צבי","טל מנשה","טל שחר","טללים",
    "טלמון","טמרה","טמרה יזרעאל",
    "יבול","יבנאל","יבנה","יגור","יגל","יד בנימין","יד חנה","יד מרדכי",
    "יד נתן","יד רמבם","ידידה","יהוד-מונוסון","יהל","יובל","יובלים",
    "יודפת","יונתן","יושיביה","יזרעאל","יחיעם","יכיני","ינוח-גת","ינון",
    "יסוד המעלה","יסודות","יספיף","יעד","יעל","יערה","יפיע","יפית",
    "יפעת","יפרח","יצהר","יציץ","יקום","יקיר","יקנעם עילית","ירדנה",
    "ירוחם","ירושלים","ירחיב","ירכא","ירקונה","ישע","ישרש","יתד",
    "כאבול","כאוכב אבו אל-היג","כברי","כדורי","כוכב השחר","כוכב יאיר",
    "כוכב מיכאל","כורזים","כחל","כינרות","כיסופים","כישור","כלנית",
    "כמאנה","כנות","כנף","כנרת מושבה","כנרת קבוצה","כסיפה","כסלון",
    "כסרא-סמיע","כעביה-טבאש","כפר אדומים","כפר אוריה","כפר אחים",
    "כפר ביאליק","כפר בילו","כפר בלום","כפר בן נון","כפר ברא","כפר ברוך",
    "כפר גלים","כפר גלעדי","כפר דניאל","כפר האורנים","כפר החורש",
    "כפר המכבי","כפר הנגיד","כפר הנשיא","כפר הס","כפר הראה","כפר הריף",
    "כפר וורבורג","כפר ויתקין","כפר זיתים","כפר חבד","כפר חוש","כפר חיטים",
    "כפר חנניה","כפר חרוב","כפר טרומן","כפר יאסיף","כפר יהושע","כפר יובל",
    "כפר יונה","כפר יחזקאל","כפר יעבץ","כפר כמא","כפר כנא","כפר מונש",
    "כפר מימון","כפר מלל","כפר מנדא","כפר מנחם","כפר מסריק","כפר מצר",
    "כפר נטר","כפר סאלד","כפר סבא","כפר סילבר","כפר סירקין","כפר עבודה",
    "כפר עזה","כפר עציון","כפר פינס","כפר קאסם","כפר קיש","כפר קרע",
    "כפר ראש הנקרה","כפר רופין","כפר רות","כפר שמאי","כפר שמריהו",
    "כפר תבור","כפר תפוח","כרכום","כרם בן זמרה","כרם בן שמן","כרם מהרל",
    "כרם שלום","כרמי יוסף","כרמי צור","כרמי קטיף","כרמיאל","כרמים","כרמל",
    "לבון","לביא","לבנים","להב","להבות הבשן","להבות חביבה","לוד","לוזית",
    "לוחמי הגטאות","לוטם","לוטן","לימן","לכיש","לפיד","לפידות","לקיה",
    "מבוא ביתר","מבוא דותן","מבוא חורון","מבוא חמה","מבוא מודיעים",
    "מבואות ים","מבטחים","מבקיעים","מגאר","מגדים","מגדל","מגדל העמק",
    "מגדל עוז","מגדל תפן","מגידו","מגל","מגן","מגן שאול","מגשימים",
    "מדרך עוז","מזור","מזכרת בתיה","מזרע","מחולה","מחניים","מטולה","מיטב",
    "מיכמן","מיכמנת","מירב","מירון","מישר","מיתר","מכורה","מכמורת","מכמש",
    "מלכיה","מנחמיה","מנרה","מסד","מסילות","מסלול","מסעדה","מעגלים",
    "מעגן","מעגן מיכאל","מעון","מעונה","מעיין ברוך","מעיין צבי","מעלה אדומים",
    "מעלה אפרים","מעלה גלבוע","מעלה גמלא","מעלה החמישה","מעלה לבונה",
    "מעלה מכמש","מעלה עירון","מעלה עמוס","מעלה שומרון","מעלות-תרשיחא",
    "מעמר","מענית","מפלסים","מצדות יהודה","מצובה","מצליח","מצפה","מצפה אביב",
    "מצפה אילן","מצפה רמון","מצפה שלם","מקווה ישראל","מרגליות","מרום גולן",
    "מרחביה מושב","מרחביה קיבוץ","מרכז שפירא","משגב עם","משהד","משואה",
    "משואות יצחק","משכיות","משמר איילון","משמר דוד","משמר הירדן","משמר הנגב",
    "משמר העמק","משמר השרון","משמרות","משמרת","משען","מתן","מתת","מתתיהו",
    "נאות גולן","נאות הכיכר","נאות מרדכי","נאות סמדר","נבטים","נגבה","נהורה",
    "נהלל","נהריה","נוב","נוגה","נווה אור","נווה אטיב","נווה אילן","נווה אמיאל",
    "נווה דניאל","נווה זוהר","נווה זיו","נווה חריף","נווה ים","נווה ירק",
    "נווה מבטח","נווה מיכאל","נווה מנחם","נווה שלום","נועם","נוף הגליל",
    "נופים","נופית","נוקדים","נורדיה","נורית","נחושה","נחל עוז","נחלה",
    "נחליאל","נחם","נחף","נחשון","נחשונים","ניין","ניר אליהו","ניר בנים",
    "ניר גלים","ניר דוד","ניר חן","ניר יפה","ניר יצחק","ניר ישראל","ניר משה",
    "ניר עוז","ניר עם","ניר עקיבא","ניר צבי","נירים","נירית","נס הרים",
    "נס ציונה","נצר חזני","נצר סרני","נצרת","נצרת עילית","נשר","נתיב הגדוד",
    "נתיב הלה","נתיב העשרה","נתיבות","נתניה",
    "סאסא","סביון","סגולה","סומיל","סחנין","סלעית","סנסנה","סעד","ספיר","סתריה",
    "עגור","עדי","עדנה","עוזה","עולש","עומר","עופר","עופרה","עוצם","עזריאל",
    "עזריה","עזריקם","עטרת","עיילבון","עיינות","עכו","עלומות","עלי","עלי זהב",
    "עליזה","עלמה","עלמון","עמינדב","עמיעד","עמיעוז","עמיר","עמנואל","עמקה",
    "עמר","עמרם","ענב","עספיא","עפולה","עפרה","עצמון שגב","עראבה","עראמשה",
    "ערד","ערוגות","ערערה","ערערה בנגב","עשרת","עתלית","עתניאל",
    "פארן","פדואל","פדויים","פדיה","פוריה עילית","פטיש","פלך","פלמחים",
    "פני חבר","פסגות","פסוטה","פצאל","פקיעין","פקיעין חדשה","פרדס חנה-כרכור",
    "פרדסיה","פרוד","פרזון","פריאל","פתח תקווה","פתחיה",
    "צאלים","צביה","צבעון","צובה","צוחר","צופים","צופית","צופר","צוקי ים",
    "צוקים","צוריאל","צורית","ציפורי","צלפון","צנדלה","צפריר","צפרירים",
    "צפת","צרופה","צרעה",
    "קבוצת יבנה","קדומים","קדים","קדמת צבי","קדרון","קדרים","קוממיות",
    "קורנית","קטורה","קיסריה","קלחים","קליה","קלנסווה","קלע","קציר",
    "קצרין","קרית אונו","קרית ארבע","קרית אתא","קרית ביאליק","קרית גת",
    "קרית טבעון","קרית ים","קרית מוצקין","קרית מלאכי","קרית ענבים",
    "קרית שמונה","קשת",
    "ראמה","ראש העין","ראש פינה","ראש צורים","ראשון לציון","רבדים","רביבים",
    "רגבה","רהט","רווחה","רוחמה","רועי","רותם","רחובות","רחלים","ריחאניה",
    "ריחן","רימונים","רינתיה","רכסים","רמות","רמות השבים","רמות מאיר",
    "רמות מנשה","רמות נפתלי","רמלה","רמת גן","רמת דוד","רמת הכובש",
    "רמת השרון","רמת יוחנן","רמת ישי","רמת מגשימים","רמת צבי","רמת רזיאל",
    "רמת רחל","רמת שפר","רנן","רעים","רעננה","רקפת","רשפון","רשפים",
    "שאר ישוב","שבי ציון","שבי שומרון","שגב-שלום","שדה אילן","שדה אליהו",
    "שדה אליעזר","שדה בוקר","שדה דוד","שדה יואב","שדה יעקב","שדה יצחק",
    "שדה משה","שדה נחום","שדה נחמיה","שדה עוזיהו","שדה צבי","שדות ים",
    "שדות מיכה","שדי חמד","שדמה","שדמות דבורה","שדמות מחולה","שהם","שובה",
    "שובל","שוהם","שומרה","שורש","שורשים","שזור","שחר","שיבולים","שיזף",
    "שילה","שילת","שימשית","שיתים","שכניה","שלווה","שלומי","שלומית","שמיר",
    "שמעה","שמרת","שני","שניר","שעב","שעל","שעלבים","שפיר","שפרעם","שקד",
    "שקף","שרונה","שריד","שרשרת","שתולה","שתולים",
    "תאשור","תדהר","תובל","תומר","תושיה","תימורים","תירוש","תל אביב - יפו",
    "תל יוסף","תל יצחק","תל מונד","תל עדשים","תל קציר","תל שבע","תלמי אלעזר",
    "תלמי בילו","תלמי יוסף","תלמי יחיאל","תלמי יפה","תלמים","תמרת","תנובות",
    "תפרח","תקומה","תקוע","תרום",
]

BLDG_OPTIONS = [
    "לול מטילות","לול פטם","לול הודים","בית אימון (עופות)","לול רביה",
    "לול הסגר / יבוא","מדגירה",
    "מבנה / סככה לרפת","מבנה / סככה למפטמה","מבנה לצאן",
    "אורווה","כלבייה",
    "מרכז מזון מורכב","מרכז מזון פשוט","מחסן חקלאי","מחסן ציוד",
    "בית צמיחה (חממה)","בית אריזה",
    "מכון רדית דבש",
    "מגורים חקלאי","מתקן השקיה / מים","מבנה שירות","אחר",
]

REQ_TYPES = [
    "היתר בנייה — מבנה חדש",
    "היתר בנייה — תוספת/שינוי",
    "שינוי ייעוד / שימוש חורג",
    "אישור עקרוני",
    "תכנית מפורטת",
    "אחר",
]

SYSTEM_PROMPT = (
    "אתה מנתח תכנוני בכיר במשרד החקלאות וביטחון המזון. "
    "מטרתך להפיק ניתוח מקצועי, מנומק ומבוסס-מקורות בלבד. "
    "החזר JSON בלבד — ללא backticks, ללא תגי markdown, ללא שום טקסט נוסף."
)

GEMINI_MODEL = "gemini-3.1-pro-preview"

_SECTION_LABELS = [
    ('"summary"',         '📋 סיכום'),
    ('"checklist"',       '☑️  בדיקת סף'),
    ('"documents"',       '📄 מסמכים'),
    ('"normativeMap"',    '🗺  מפה נורמטיבית'),
    ('"comparisonTable"', '⚖️  השוואה'),
    ('"determinations"',  '📌 קביעות'),
    ('"blockers"',        '🚫 חסמים'),
    ('"opinion"',         '📝 חוות דעת'),
    ('"appendix"',        '🗃  נספח'),
]

JSON_SCHEMA = """{
  "summary": {
    "caseId": "מספר תיק",
    "yishuv": "ישוב",
    "gush": "גוש",
    "helka": "חלקה",
    "bldgType": "סוג מבנה",
    "reqType": "סוג בקשה",
    "overallStatus": "להמליץ|להמליץ בתנאים|נדרש בירור|לא להמליץ",
    "certainty": "גבוהה|בינונית|נמוכה|לא מספקת",
    "analysisDate": "תאריך",
    "keyFindings": ["ממצא 1","ממצא 2"],
    "criticalGaps": ["פער 1","פער 2"]
  },
  "checklist": [
    {"num":1,"label":"זיהוי חד-משמעי של התיק","status":"נבדק|לא ישים|לא נבדק","finding":"","certainty":""},
    {"num":2,"label":"שלמות מסמכי ליבה","status":"נבדק|לא ישים|לא נבדק","finding":"","certainty":""},
    {"num":3,"label":"עמידה בתנאי יסוד","status":"נבדק|לא ישים|לא נבדק","finding":"","certainty":""},
    {"num":4,"label":"מיפוי מצב קיים מול מוצע","status":"נבדק|לא ישים|לא נבדק","finding":"","certainty":""},
    {"num":5,"label":"איתור שכבה סטטוטורית","status":"נבדק|לא ישים|לא נבדק","finding":"","certainty":""},
    {"num":6,"label":"מפת תחולה נורמטיבית","status":"נבדק|לא ישים|לא נבדק","finding":"","certainty":""},
    {"num":7,"label":"בדיקת התאמה רישויית","status":"נבדק|לא ישים|לא נבדק","finding":"","certainty":""},
    {"num":8,"label":"סיווג מקצועי של המבנה","status":"נבדק|לא ישים|לא נבדק","finding":"","certainty":""},
    {"num":9,"label":"בדיקה מול כרטיס המבנה","status":"נבדק|לא ישים|לא נבדק","finding":"","certainty":""},
    {"num":10,"label":"בדיקות משלימות","status":"נבדק|לא ישים|לא נבדק","finding":"","certainty":""},
    {"num":11,"label":"זיהוי חסרים וסתירות","status":"נבדק|לא ישים|לא נבדק","finding":"","certainty":""},
    {"num":12,"label":"גיבוש מסלול הכרעה","status":"נבדק|לא ישים|לא נבדק","finding":"","certainty":""}
  ],
  "documents": {
    "uploaded": [{"name":"שם קובץ","type":"pdf|image|doc","status":"parsed|ocr|failed","parsedContent":"","ocrWarning":false,"keyData":{}}],
    "missing": [{"name":"שם מסמך חסר","reason":"מדוע נדרש","criticality":"קריטי|חשוב|רצוי"}],
  },
  "normativeMap": {
    "zone": "ייעוד",
    "applicablePlans": ["תכנית 1"],
    "applicableRegulations": ["חוק התכנון והבנייה תשכ\"ה-1965"],
    "ministryPolicy": "מדיניות משרד רלוונטית",
    "specialConditions": [],
    "gaps": []
  },
  "comparisonTable": [
    {"component":"סוג מבנה","requested":"","source":"","allowed":"","match":"תואם|אי-התאמה|לא ידוע","gap":"","action":"","certainty":""},
    {"component":"שימוש","requested":"","source":"","allowed":"","match":"לא ידוע","gap":"","action":"","certainty":"לא מספקת"},
    {"component":"מיקום","requested":"","source":"","allowed":"","match":"לא ידוע","gap":"","action":"","certainty":"לא מספקת"},
    {"component":"שטח","requested":"","source":"","allowed":"","match":"לא ידוע","gap":"","action":"","certainty":"לא מספקת"},
    {"component":"גובה","requested":"","source":"","allowed":"","match":"לא ידוע","gap":"","action":"","certainty":"לא מספקת"},
    {"component":"מרחקים","requested":"","source":"","allowed":"","match":"לא ידוע","gap":"","action":"","certainty":"לא מספקת"},
    {"component":"אישורים נדרשים","requested":"","source":"","allowed":"","match":"לא ידוע","gap":"","action":"","certainty":"לא מספקת"},
    {"component":"תנאים מיוחדים","requested":"","source":"","allowed":"","match":"לא ידוע","gap":"","action":"","certainty":"לא מספקת"},
    {"component":"חוסרים קריטיים","requested":"","source":"","allowed":"","match":"לא ידוע","gap":"","action":"","certainty":"לא מספקת"}
  ],
  "determinations": [
    {
      "category": "סטטוטורית|רישויית|מדיניות משרד|עובדתית-ראייתית|מערכתית-נגזרת",
      "type": "סוג הקביעה",
      "determination": "הקביעה עצמה",
      "sourceType": "סטטוטורי|רישויי|מדיניות משרד|עובדתי-ראייתי|מערכתי-נגזר",
      "docName": "שם המסמך",
      "location": "מיקום במסמך",
      "quote": "ציטוט קצר",
      "professional": "משמעות מקצועית",
      "impact": "השפעה על ההכרעה",
      "certainty": "גבוהה|בינונית|נמוכה|לא מספקת",
      "action": "פעולה נדרשת",
      "ocrBased": false
    }
  ],
  "blockers": [
    {"type":"קשיח|רך","category":"ראייתי|פרשני|מהותי","description":"","source":"","required":"","why":"","impact":"","closureStatus":"פתוח|נסגר","closedHow":""}
  ],
  "opinion": {
    "recommendation": "להמליץ|להמליץ בתנאים|נדרש בירור|לא להמליץ",
    "certainty": "גבוהה|בינונית|נמוכה|לא מספקת",
    "rationale": "נימוק מפורט לחוות הדעת",
    "conditions": [{"condition":"","source":"","required":"","why":"","impact":"","closureStatus":"פתוח","type":"קשיח|רך"}],
    "redFlags": [],
    "internalNote": "",
    "disclaimer": "חוות דעת ראשונית פנימית בלבד. אינה מחליפה שיקול דעת מקצועי ואינה מהווה החלטה רשמית."
  },
  "appendix": {
    "processingLog": [],
    "ocrWarnings": [],
    "assumptions": [],
    "internalNotes": ""
  }
}"""

REC_ICON = {"להמליץ": "✅", "להמליץ בתנאים": "⚠️", "נדרש בירור": "ℹ️", "לא להמליץ": "❌"}
CERT_ICON = {"גבוהה": "🟢", "בינונית": "🟡", "נמוכה": "🟠", "לא מספקת": "🔴"}


# ─────────────────────────────────────────────────────────────────────────────
#  OCR HELPER — pdfplumber text + table extraction
# ─────────────────────────────────────────────────────────────────────────────
def _extract_pdf_text(data: bytes) -> str:
    try:
        import pdfplumber
        parts = []
        with pdfplumber.open(BytesIO(data)) as pdf:
            for page in pdf.pages:
                text = (page.extract_text() or "").strip()
                if text:
                    parts.append(f"[עמוד {page.page_number}]\n{text}")
                for tbl in (page.extract_tables() or []):
                    rows = [
                        " | ".join(str(c or "").strip() for c in row)
                        for row in tbl if any(c for c in row)
                    ]
                    if rows:
                        parts.append(f"[טבלה עמוד {page.page_number}]\n" + "\n".join(rows))
        return "\n\n".join(parts)[:8000]
    except Exception:
        return ""




# ─────────────────────────────────────────────────────────────────────────────
#  FILE → API CONTENT BLOCKS  (returns list to allow multi-block per file)
# ─────────────────────────────────────────────────────────────────────────────
def file_to_block(f) -> tuple:
    f.seek(0)
    data = f.read()
    name = f.name
    ext = name.rsplit(".", 1)[-1].lower()
    size = f"{f.size / 1024:.1f}KB" if f.size < 1_048_576 else f"{f.size / 1_048_576:.1f}MB"

    if ext == "pdf":
        parts: list = []
        extracted = _extract_pdf_text(data)
        if extracted:
            parts.append(genai_types.Part.from_text(
                text=f"=== טקסט שחולץ מ-{name} (pdfplumber OCR) ===\n{extracted}"
            ))
        parts.append(genai_types.Part.from_bytes(data=data, mime_type="application/pdf"))
        ocr_note = "+OCR" if extracted else "+Vision"
        return parts, f"- {name} ({size}, סטטוס: נקלט/PDF{ocr_note})"

    if ext in ("jpg", "jpeg"):
        return (
            [genai_types.Part.from_bytes(data=data, mime_type="image/jpeg")],
            f"- {name} ({size}, סטטוס: נקלט/תמונה)",
        )
    if ext == "png":
        return (
            [genai_types.Part.from_bytes(data=data, mime_type="image/png")],
            f"- {name} ({size}, סטטוס: נקלט/תמונה)",
        )
    if ext in ("tif", "tiff"):
        return (
            [genai_types.Part.from_text(
                text=f"[{name} — TIFF אינו נתמך לקריאה ישירה. יסומן OCR-required.]")],
            f"- {name} ({size}, סטטוס: OCR-required)",
        )
    # DOCX / DOC / plain text
    try:
        from docx import Document as DocxDocument
        doc = DocxDocument(BytesIO(data))
        text = "\n".join(p.text for p in doc.paragraphs)[:5000]
    except Exception:
        text = data.decode("utf-8", errors="replace")[:5000]
    return (
        [genai_types.Part.from_text(text=f"=== {name} ===\n{text}")],
        f"- {name} ({size}, סטטוס: נקלט/טקסט)",
    )


# ─────────────────────────────────────────────────────────────────────────────
#  ANALYSIS
# ─────────────────────────────────────────────────────────────────────────────
def run_analysis(api_key: str, meta: dict, files, live=None) -> dict:
    parts: list = []
    lines: list[str] = []
    for f in files:
        file_parts, desc = file_to_block(f)
        parts.extend(file_parts)
        lines.append(desc)

    today = date.today().strftime("%d/%m/%Y")

    prompt_text = f"""אתה מנתח תכנוני בכיר במשרד החקלאות וביטחון המזון.
נתח את תיק הבקשה שלהלן בצורה מקיפה, מקצועית ומבוססת-מקורות.

פרטי התיק:
- מספר תיק: {meta.get('caseId') or 'לא צוין'}
- ישוב: {meta.get('yishuv') or 'לא צוין'} | ועדה: {meta.get('vaada') or 'לא צוין'}
- גוש: {meta.get('gush') or 'לא צוין'} | חלקה: {meta.get('helka') or 'לא צוין'}
- סוג בקשה: {meta.get('reqType') or 'לא צוין'}
- סוג מבנה: {meta.get('bldgType') or 'לא צוין'}
- הערות מתכנן: {meta.get('notes') or 'אין'}
- תאריך ניתוח: {today}

קבצים שהועלו:
{chr(10).join(lines)}

כללי ניתוח מחייבים:
1. OCR על מסמכים סרוקים: אם פענוח אינו ודאי — סמן ocrWarning:true ו"דורש אימות ידני".
2. Rules Gate: אם ודאות כוללת "לא מספקת" — overallStatus חייב להיות "נדרש בירור" או "לא להמליץ".
3. לוגיקת חסמים: חסם קשיח פתוח => "נדרש בירור" או "לא להמליץ". חסמים רכים בלבד => "להמליץ בתנאים". ללא חסמים => "להמליץ".
4. לכל קביעה — ציין מאיזה מסמך / מקור בדיוק.
5. analysisDate חייב להיות: {today}

החזר JSON בלבד — ללא backticks, ללא טקסט נוסף:
""" + JSON_SCHEMA

    parts.append(genai_types.Part.from_text(text=prompt_text))

    import truststore
    truststore.inject_into_ssl()
    client = google_genai.Client(api_key=api_key)

    chunks: list[str] = []
    for chunk in client.models.generate_content_stream(
        model=GEMINI_MODEL,
        contents=parts,
        config=genai_types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            max_output_tokens=32000,
            temperature=0.1,
        ),
    ):
        text = chunk.text or ""
        if text:
            chunks.append(text)
            if live is not None:
                accumulated = "".join(chunks)
                char_count = len(accumulated)
                rows, row = [], []
                for _key, _lbl in _SECTION_LABELS:
                    _icon = "✅" if _key in accumulated else "⏳"
                    row.append(f"{_icon} {_lbl}")
                    if len(row) == 3:
                        rows.append("　　".join(row))
                        row = []
                if row:
                    rows.append("　　".join(row))
                import re as _re
                _matches = _re.findall(r':\s*"([^"]{15,})"', accumulated)
                _last = f'\n\n📝 *{_matches[-1][:130]}*' if _matches else ""
                live.markdown(
                    f"**📡 {GEMINI_MODEL} — {char_count:,} תווים**\n\n"
                    + "\n\n".join(rows) + _last
                )

    raw = "".join(chunks)
    clean = raw.replace("```json", "").replace("```", "").strip()
    start, end = clean.find("{"), clean.rfind("}")
    if start != -1 and end != -1:
        clean = clean[start : end + 1]

    for attempt in [
        lambda t: json.loads(t),
        lambda t: json.loads(t.replace(",\n}", "\n}").replace(",\n]", "\n]")),
        lambda t: json.loads(t.replace(",}", "}").replace(",]", "]")),
    ]:
        try:
            return attempt(clean)
        except json.JSONDecodeError:
            continue
    raise ValueError(f"__RAW__:{raw}")


# ─────────────────────────────────────────────────────────────────────────────
#  RENDER HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def safe(arr):
    return [x for x in (arr or []) if x and x != "..."]


def cert_label(c):
    return f"{CERT_ICON.get(c, '⚪')} {c or '—'}"


def rec_label(r):
    return f"{REC_ICON.get(r, '❓')} {r or '—'}"


def _rec_fn(rec):
    return {
        "להמליץ": st.success,
        "להמליץ בתנאים": st.warning,
        "נדרש בירור": st.info,
        "לא להמליץ": st.error,
    }.get(rec, st.info)


# ─────────────────────────────────────────────────────────────────────────────
#  SECTION RENDERERS
# ─────────────────────────────────────────────────────────────────────────────
def render_status(r):
    s = r.get("summary", {})
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("מספר תיק", s.get("caseId") or "—")
    c2.metric("ישוב / גוש-חלקה",
              f"{s.get('yishuv','—')} / {s.get('gush','—')}-{s.get('helka','—')}")
    c3.metric("סוג מבנה", s.get("bldgType") or "—")
    c4.metric("תאריך ניתוח",
              s.get("analysisDate") or date.today().strftime("%d/%m/%Y"))

    rec, cert = s.get("overallStatus", ""), s.get("certainty", "")
    _rec_fn(rec)(f"**{rec_label(rec)}** | ודאות: {cert_label(cert)} | {s.get('reqType','')}")

    findings = safe(s.get("keyFindings", []))
    if findings:
        st.markdown("**ממצאים מרכזיים:**")
        for f in findings:
            st.markdown(f"• {f}")

    gaps = safe(s.get("criticalGaps", []))
    if gaps:
        with st.expander("🔴 פערים קריטיים"):
            for g in gaps:
                st.markdown(f"• {g}")

    st.warning("⚠ זוהי חוות דעת ראשונית פנימית בלבד. "
               "אינה מחליפה שיקול דעת מקצועי ואינה מהווה החלטה רשמית.")


def render_documents(r):
    d = r.get("documents", {})

    st.subheader(f"מסמכים שנקלטו ({len(d.get('uploaded', []))})")
    for f in d.get("uploaded", []):
        icon = "📄" if f.get("type") == "pdf" else "🖼" if f.get("type") == "image" else "📝"
        st_map = {"parsed": "✅ נותח", "ocr": "⚠ OCR", "failed": "❌ שגיאה"}
        st_label = st_map.get(f.get("status", ""), f.get("status", ""))
        with st.expander(f"{icon} {f.get('name','—')} — {st_label}"):
            st.write(f.get("parsedContent") or "אין תיאור")
            if f.get("ocrWarning"):
                st.warning("⚠ OCR — דורש אימות ידני")

    missing = d.get("missing", [])
    if missing:
        st.subheader(f"מסמכים חסרים ({len(missing)})")
        for m in missing:
            crit = m.get("criticality", "")
            fn = st.error if crit == "קריטי" else st.warning if crit == "חשוב" else st.info
            fn(f"**{m.get('name','—')}** — {m.get('reason','')}")



def render_threshold(r):
    cl = r.get("checklist", [])
    done = sum(1 for c in cl if c.get("status") == "נבדק")
    st.progress(done / max(len(cl), 1), text=f"{done}/{len(cl)} נבדקו")
    for c in cl:
        s = c.get("status", "")
        icon = "✅" if s == "נבדק" else "⚫" if s == "לא ישים" else "⏳"
        with st.expander(
            f"{icon} {c.get('num','')}. {c.get('label','—')} — {cert_label(c.get('certainty',''))}"
        ):
            st.write(c.get("finding") or "—")


def render_normative(r):
    n = r.get("normativeMap", {})
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"**ייעוד קרקע:** {n.get('zone') or '—'}")
        st.markdown(f"**מדיניות משרד:** {n.get('ministryPolicy') or '—'}")
    with c2:
        plans = n.get("applicablePlans", [])
        if plans:
            st.markdown("**תכניות חלות:** " + " | ".join(plans))
        regs = n.get("applicableRegulations", [])
        if regs:
            st.markdown("**תקנות:** " + " | ".join(regs))
    conditions = safe(n.get("specialConditions", []))
    if conditions:
        st.markdown("**תנאים מיוחדים:** " + " | ".join(conditions))
    gaps = safe(n.get("gaps", []))
    if gaps:
        st.error("**פערי מידע:** " + " | ".join(gaps))


def render_analysis(r):
    s = r.get("summary", {})
    cl = r.get("checklist", [])
    c1, c2 = st.columns(2)
    c1.markdown(f"**סוג מבנה מסווג:** {s.get('bldgType') or 'לא הוגדר'}")
    c2.markdown(f"**סטטוס:** {rec_label(s.get('overallStatus',''))}")
    st.divider()
    for c in cl:
        if c.get("status") == "נבדק":
            with st.expander(
                f"**{c.get('num')}. {c.get('label')}** — {cert_label(c.get('certainty',''))}"
            ):
                st.write(c.get("finding") or "—")


def render_determinations(r):
    dets = r.get("determinations", [])
    cats = ["סטטוטורית", "רישויית", "מדיניות משרד", "עובדתית-ראייתית", "מערכתית-נגזרת"]
    icons = {
        "סטטוטורית": "⚖", "רישויית": "📜", "מדיניות משרד": "🏛",
        "עובדתית-ראייתית": "🔎", "מערכתית-נגזרת": "⚙",
    }
    shown = False
    for cat in cats:
        items = [d for d in dets if d.get("category") == cat]
        if not items:
            continue
        shown = True
        st.subheader(f"{icons.get(cat,'📌')} קביעות {cat} ({len(items)})")
        for d in items:
            with st.expander(
                f"**{d.get('determination','—')}** — {cert_label(d.get('certainty',''))}"
            ):
                cc1, cc2 = st.columns(2)
                cc1.markdown(f"**מסמך:** {d.get('docName') or '—'}")
                cc2.markdown(f"**מיקום:** {d.get('location') or '—'}")
                if d.get("quote") and d["quote"] != "...":
                    st.markdown(f"> *\"{d['quote']}\"*")
                if d.get("professional"):
                    st.markdown(d["professional"])
                tags = []
                if d.get("sourceType"):
                    tags.append(f"🏷 {d['sourceType']}")
                if d.get("ocrBased"):
                    tags.append("⚠ OCR — דורש אימות ידני")
                if d.get("action") and d["action"] != "...":
                    tags.append(f"→ {d['action']}")
                if tags:
                    st.caption(" | ".join(tags))
    if not shown:
        st.info("לא נמצאו קביעות.")


def render_comparison(r):
    rows = r.get("comparisonTable", [])
    if not rows:
        st.info("אין נתוני השוואה.")
        return
    df = pd.DataFrame([
        {
            "רכיב נבדק": row.get("component", ""),
            "המבוקש": row.get("requested", "—"),
            "המקור הקובע": row.get("source", "—"),
            "המותר/המומלץ": row.get("allowed", "—"),
            "התאמה": row.get("match", "—"),
            "פער/סתירה": row.get("gap", "—") if row.get("gap") not in ("", "...", None) else "—",
            "פעולה נדרשת": row.get("action", "—") if row.get("action") not in ("", "...", None) else "—",
            "ודאות": row.get("certainty", "—"),
        }
        for row in rows
    ])
    st.dataframe(df, use_container_width=True, hide_index=True)


def render_blockers(r):
    bl = r.get("blockers", [])
    hard = [b for b in bl if b.get("type") == "קשיח"]
    soft = [b for b in bl if b.get("type") == "רך"]
    if not bl:
        st.success("✅ לא זוהו חסמים פתוחים.")
        return
    if hard:
        st.error(f"⛔ **חסמים קשיחים ({len(hard)})**")
        for b in hard:
            closed = b.get("closureStatus") == "נסגר"
            with st.expander(
                f"⛔ {b.get('description','—')} — {'✅ נסגר' if closed else '🔴 פתוח'}"
            ):
                cc1, cc2 = st.columns(2)
                cc1.markdown(f"**קטגוריה:** {b.get('category','—')}")
                cc2.markdown(f"**מקור:** {b.get('source','—')}")
                st.markdown(f"**נדרש:** {b.get('required','—')}")
                st.markdown(f"**מדוע:** {b.get('why','—')}")
                st.markdown(f"**השפעה:** {b.get('impact','—')}")
    if soft:
        st.warning(f"⚠ **חסמים רכים/תנאים ({len(soft)})**")
        for b in soft:
            closed = b.get("closureStatus") == "נסגר"
            with st.expander(
                f"⚠ {b.get('description','—')} — {'✅ נסגר' if closed else '🟡 פתוח'}"
            ):
                cc1, cc2 = st.columns(2)
                cc1.markdown(f"**מקור:** {b.get('source','—')}")
                cc2.markdown(f"**נדרש:** {b.get('required','—')}")


def render_opinion(r):
    op = r.get("opinion", {})
    st.warning(
        f"⚠ **הצהרת כלי:** {op.get('disclaimer','חוות דעת ראשונית פנימית בלבד.')}"
    )
    rec, cert = op.get("recommendation", ""), op.get("certainty", "")
    _rec_fn(rec)(f"**{rec_label(rec)}** | ודאות: {cert_label(cert)}")
    if op.get("rationale"):
        st.markdown(op["rationale"])

    conds = [c for c in safe(op.get("conditions", []))
             if c.get("condition") and c["condition"] != "..."]
    if conds:
        st.subheader("תנאים לסגירה")
        for c in conds:
            t = c.get("type", "תנאי")
            icon = "⛔" if t == "קשיח" else "⚠"
            with st.expander(f"{icon} {c.get('condition','—')}"):
                cc1, cc2 = st.columns(2)
                cc1.markdown(f"**מקור:** {c.get('source','—')}")
                cc2.markdown(f"**נדרש:** {c.get('required','—')}")
                st.markdown(f"**מדוע:** {c.get('why','—')}")
                st.markdown(f"**השפעה:** {c.get('impact','—')}")

    flags = safe(op.get("redFlags", []))
    if flags:
        st.error("🚩 **דגלים אדומים:**")
        for f in flags:
            st.markdown(f"🚩 {f}")

    if op.get("internalNote") and op["internalNote"] != "...":
        st.info(f"📋 **הערה פנימית:** {op['internalNote']}")


def render_appendix(r):
    ap = r.get("appendix", {})
    log = safe(ap.get("processingLog", []))
    if log:
        st.subheader("יומן עיבוד")
        st.code("\n".join(f"▸ {l}" for l in log), language=None)

    ocr = safe(ap.get("ocrWarnings", []))
    if ocr:
        st.subheader("אזהרות OCR")
        for w in ocr:
            st.warning(f"⚠ {w}")

    assumptions = safe(ap.get("assumptions", []))
    if assumptions:
        st.subheader("הנחות ניתוח")
        for a in assumptions:
            st.markdown(f"• {a}")

    if ap.get("internalNotes") and ap["internalNotes"] != "...":
        st.subheader("הערות פנימיות נוספות")
        st.write(ap["internalNotes"])


# ─────────────────────────────────────────────────────────────────────────────
#  SESSION STATE
# ─────────────────────────────────────────────────────────────────────────────
def _load_api_key() -> str:
    try:
        return st.secrets["GOOGLE_API_KEY"]
    except Exception:
        return os.environ.get("GOOGLE_API_KEY", "")

for _k, _v in {
    "result": None,
    "api_key": _load_api_key(),
}.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v

# ─────────────────────────────────────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🌾 מנת\"ח חקלאי")
    st.caption("מערכת ניתוח תכנוני — משרד החקלאות וביטחון המזון")
    st.divider()

    if st.session_state.api_key:
        st.success("✓ מחובר ל-Google Gemini")
    else:
        st.error("⚠ מפתח GOOGLE_API_KEY חסר — פנה למנהל המערכת")

    st.divider()
    if st.button("🔄 תיק חדש", use_container_width=True):
        st.session_state.result = None
        st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
#  HEADER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("# 🌾 מנת\"ח חקלאי — מערכת ניתוח תכנוני")
st.warning("⚠ **כלי פנימי בלבד** — אינו מחליף שיקול דעת מקצועי ואינו מהווה החלטה רשמית.")

# ─────────────────────────────────────────────────────────────────────────────
#  INTAKE FORM
# ─────────────────────────────────────────────────────────────────────────────
with st.expander("📂 קליטת תיק — מטא-דאטה ומסמכים",
                 expanded=st.session_state.result is None):

    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.markdown("**📋 פרטי התיק**")
        case_id = st.text_input("מספר תיק / מזהה בקשה",
                                placeholder="לדוג׳ 2025-YYYY-001", key="f_case")
        if not case_id:
            st.caption("⚠ ללא מספר תיק — שם קובץ הייצוא יהיה: ישוב_גוש_חלקה")
        yishuv = st.selectbox("ישוב", options=[""] + sorted(YISHUVIM),
                              index=0, key="f_yishuv")
        vaada = st.text_input("ועדה מקומית", placeholder="שם הועדה", key="f_vaada")
        cg, ch = st.columns(2)
        with cg:
            gush = st.text_input("גוש *", placeholder="מספר גוש", key="f_gush")
        with ch:
            helka_raw = st.text_input("חלקה *", placeholder="מספר חלקה, או מרובות: 1, 2, 3", key="f_helka")
        req_type = st.selectbox("סוג בקשה", options=[""] + REQ_TYPES, key="f_req_type")
        bldg_type = st.selectbox("סוג מבנה מוצע", options=[""] + BLDG_OPTIONS,
                                 key="f_bldg_type")
        notes = st.text_area("הערות המתכנן",
                             placeholder="הקשר מיוחד, נקודות לתשומת לב...",
                             height=100, key="f_notes")

    with col_right:
        st.markdown("**📎 העלאת מסמכים**")
        uploaded_files = st.file_uploader(
            "גרור קבצים לכאן או לחץ לבחירה",
            type=["pdf", "jpg", "jpeg", "png", "docx", "doc", "tif", "tiff"],
            accept_multiple_files=True,
            key="file_uploader",
        )
        if uploaded_files:
            for f in uploaded_files:
                _ext = f.name.rsplit(".", 1)[-1].lower()
                _icon = "📄" if _ext == "pdf" else "🖼" if _ext in ["jpg","jpeg","png","tif","tiff"] else "📝"
                _sz = (f"{f.size/1024:.1f}KB" if f.size < 1_048_576
                       else f"{f.size/1_048_576:.1f}MB")
                st.markdown(f"{_icon} **{f.name}** — {_sz}")

        st.divider()
        st.markdown("**מסמכי ליבה נדרשים:**")
        for _doc, _status in [
            ("תוכנית מצב קיים", "חובה"), ("תוכנית מצב מוצע", "חובה"),
            ("גרמושקה / נסח טאבו", "חובה"), ("היתרים קיימים", "לא חובה"),
            ("חוות דעת אגרונום", "חובה"), ("אישורים משלימים", "לפי סוג"),
        ]:
            _ico = "⚪" if _status == "חובה" else "🔵"
            st.markdown(f"{_ico} {_doc} — *{_status}*")

    st.divider()
    analyze_btn = st.button(
        "▶ הרץ ניתוח מלא",
        type="primary",
        use_container_width=True,
        key="btn_analyze",
    )

# ─────────────────────────────────────────────────────────────────────────────
#  TRIGGER ANALYSIS
# ─────────────────────────────────────────────────────────────────────────────
if analyze_btn:
    helka_list = [h.strip() for h in helka_raw.split(",") if h.strip()]
    _errors = []
    if not yishuv:
        _errors.append("ישוב הוא שדה חובה.")
    if not gush.strip():
        _errors.append("גוש הוא שדה חובה.")
    elif not gush.strip().isdigit():
        _errors.append("גוש חייב להיות מספר שלם.")
    if not helka_list:
        _errors.append("חלקה היא שדה חובה.")
    else:
        _bad = [h for h in helka_list if not h.isdigit()]
        if _bad:
            _errors.append(f"חלקה חייבת להיות מספר שלם (שגוי: {', '.join(_bad)}).")
    if not uploaded_files:
        _errors.append("נא להעלות לפחות מסמך אחד לניתוח.")
    if _errors:
        for _e in _errors:
            st.error(_e)
    else:
        with st.status("🔄 מנתח תיק...", expanded=True) as status:
            try:
                total_size = sum(f.size for f in uploaded_files)
                size_str = (f"{total_size/1024:.1f}KB" if total_size < 1_048_576
                            else f"{total_size/1_048_576:.1f}MB")
                status.write(
                    f"📄 שלב 1/2 — מעבד {len(uploaded_files)} קבצים ({size_str}) "
                    f"עם OCR + pdfplumber..."
                )

                status.write(f"🤖 שלב 2/2 — שולח ל-{GEMINI_MODEL} (max 32,000 אסימונים)...")
                live_placeholder = st.empty()

                result = run_analysis(
                    api_key=st.session_state.api_key,
                    meta={
                        "caseId": case_id, "yishuv": yishuv, "vaada": vaada,
                        "gush": gush, "helka": ", ".join(helka_list), "reqType": req_type,
                        "bldgType": bldg_type, "notes": notes,
                    },
                    files=uploaded_files,
                    live=live_placeholder,
                )
                live_placeholder.empty()
                st.session_state.result = result
                status.update(label="✅ ניתוח הושלם!", state="complete", expanded=False)
                st.rerun()
            except Exception as exc:
                status.update(label="❌ שגיאה בניתוח", state="error")
                msg = str(exc)
                if msg.startswith("__RAW__:"):
                    raw_text = msg[8:]
                    st.error(f"תשובת API אינה JSON תקין ({len(raw_text):,} תווים התקבלו).")
                    with st.expander("🔍 תגובה גולמית מ-Claude (לאבחון)"):
                        st.code(raw_text[:6000], language="json")
                else:
                    st.error(f"שגיאה בניתוח: {exc}")

# ─────────────────────────────────────────────────────────────────────────────
#  RESULTS
# ─────────────────────────────────────────────────────────────────────────────
if st.session_state.result:
    r = st.session_state.result
    s = r.get("summary", {})
    case_label = s.get("caseId") or s.get("yishuv") or "תיק"

    st.divider()
    st.markdown(f"### 📊 תוצאות ניתוח — {case_label}")

    tabs = st.tabs([
        "📋 סטטוס",
        "📄 מסמכים",
        "🔒 בדיקת סף",
        "🗺 מפה נורמטיבית",
        "🔍 ניתוח",
        "📌 קביעות",
        "⚖️ השוואה",
        "🚫 חסמים",
        "📝 חוות דעת",
        "🗃 נספח",
    ])

    with tabs[0]:  render_status(r)
    with tabs[1]:  render_documents(r)
    with tabs[2]:  render_threshold(r)
    with tabs[3]:  render_normative(r)
    with tabs[4]:  render_analysis(r)
    with tabs[5]:  render_determinations(r)
    with tabs[6]:  render_comparison(r)
    with tabs[7]:  render_blockers(r)
    with tabs[8]:  render_opinion(r)
    with tabs[9]:  render_appendix(r)

    st.divider()
    _cid = s.get("caseId", "")
    _helka_str = "_".join(s.get("helka", "0").replace(" ", "").split(","))
    _filename = (
        _cid if _cid and _cid not in ("לא צוין", "—")
        else f"{s.get('yishuv','תיק')}_{s.get('gush','0')}_{_helka_str}"
    )
    st.download_button(
        "⬇ הורד תוצאות JSON",
        data=json.dumps(r, ensure_ascii=False, indent=2),
        file_name=f"analysis_{_filename}.json",
        mime="application/json",
    )
