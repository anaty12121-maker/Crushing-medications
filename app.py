import streamlit as st
import pandas as pd
import requests

st.set_page_config(
    page_title="מנוע חיפוש כתישת תרופות",
    page_icon="💊",
    layout="centered"
)

@st.cache_data(ttl=60)
def load_data():
    url = "https://raw.githubusercontent.com/anaty12121-maker/Crushing-medications/main/medications.csv"
    df = pd.read_csv(url)
    return df

def search_moh_api(query):
    """
    שאילתה מורחבת ל-API הממשלתי (data.gov.il) הפונה גם לחיפוש כללי 
    וגם לחיפוש לפי שדות חומר פעיל ושם מסחרי
    """
    api_url = "https://data.gov.il/api/3/action/datastore_search"
    resource_id = "36bf15b0-30b0-4973-a2ab-323871239c3e" 
    clean_query = query.strip().upper()
    
    # 1. ניסיון חיפוש חופשי
    try:
        res = requests.get(api_url, params={"resource_id": resource_id, "q": clean_query, "limit": 10}, timeout=4)
        if res.status_code == 200:
            records = res.json().get("result", {}).get("records", [])
            if records:
                return records
    except Exception:
        pass

    # 2. ניסיון חיפוש ממוקד במידה וחיפוש חופשי לא החזיר תוצאה
    try:
        filters = f'{{"DRUG_GENERIC_NAME": "{clean_query}"}}'
        res = requests.get(api_url, params={"resource_id": resource_id, "filters": filters, "limit": 10}, timeout=4)
        if res.status_code == 200:
            records = res.json().get("result", {}).get("records", [])
            if records:
                return records
    except Exception:
        pass

    return []

st.title("💊 מנוע חיפוש והנחיות לכתישת תרופות")

try:
    df = load_data()
    search_query = st.text_input("הקלידי שם תרופה (מסחרי או גנרי):", "").strip()
    
    if search_query:
        # 1. חיפוש במאגר המאומת המקומי (medications.csv)
        results = df[
            df['Brand Name'].astype(str).str.contains(search_query, case=False, na=False) |
            df['Generic Name'].astype(str).str.contains(search_query, case=False, na=False)
        ]
        
        if not results.empty:
            for _, row in results.iterrows():
                category = str(row.get('Category', '')).strip()
                notes = str(row.get('Notes / Source', 'missing basic information')).strip()
                brand = row['Brand Name']
                generic = row['Generic Name']
                
                if category == 'FORBIDDEN_CRITICAL':
                    st.error(f"❌ **{brand}** ({generic})\n\n**אסור לכתוש!**\n\n**הנחיות ומקור:** {notes}")
                elif category == 'ENTERIC_COATED':
                    st.warning(f"⚠️ **{brand}** ({generic})\n\n**ציפוי אנטרי / פתיחה בלבד**\n\n**הנחיות ומקור:** {notes}")
                elif category == 'ALLOWED':
                    st.success(f"✅ **{brand}** ({generic})\n\n**מותר לכתוש**\n\n**הנחיות ומקור:** {notes}")
                else:
                    st.info(f"ℹ️ **{brand}** ({generic})\n\n**מידע:** {notes}")
        else:
            # 2. שליפה אוטומטית ממאגר משרד הבריאות במידה ולא נמצא ב-CSV
            moh_records = search_moh_api(search_query)
            
            if moh_records:
                st.info("🔎 **התרופה אותרה במאגר התרופות הרשמי של משרד הבריאות:**")
                for rec in moh_records:
                    brand = rec.get("DRUG_NAME") or rec.get("DRUG_ENGLISH_NAME") or search_query
                    generic = rec.get("DRUG_GENERIC_NAME") or ""
                    form = rec.get("DOSAGE_FORM") or "לא צוין"
                    
                    st.warning(
                        f"💊 **{brand}** ({generic})\n\n"
                        f"**צורת מתן רשומה:** {form}\n\n"
                        f"⚠️ **סטטוס קליני:** `missing basic information`\n\n"
                        f"*התרופה רשומה בישראל, אך טרם הוגדרה לגביה הנחיית כתישה מאומתת בבסיס הנתונים. יש להיוועץ ברוקח/ת.*"
                    )
            else:
                st.warning("missing basic information (התרופה לא נמצאה במאגר המקומי או בסיס הנתונים)")

except Exception as e:
    st.error("אירעה שגיאה בטעינת המידע.")

st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray; font-size: 0.85em;'>"
    "נבנה על ידי ענת יהלום, רוקחת בבתי אבות | סיוע בפיתוח טכני: AI<br>"
    "<i>⚠️ <b>הבהרה משפטית:</b> המידע מיועד לסיוע ואינו מחליף שיקול דעת מקצועי, עלון לרופא או היוועצות ברוקח/ת. המאגר מתבסס על מקורות מורשים (Micromedex, Open Evidence, עלוני משרד הבריאות).</i>"
    "</div>",
    unsafe_allow_html=True
)
