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
    פנייה ל-API הממשלתי (data.gov.il) במידה והתרופה לא נמצאה ב-CSV המקומי
    """
    api_url = "https://data.gov.il/api/3/action/datastore_search"
    resource_id = "36bf15b0-30b0-4973-a2ab-323871239c3e" 
    params = {
        "resource_id": resource_id,
        "q": query,
        "limit": 5
    }
    try:
        response = requests.get(api_url, params=params, timeout=3)
        if response.status_code == 200:
            data = response.json()
            records = data.get("result", {}).get("records", [])
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
            df['Brand Name'].str.contains(search_query, case=False, na=False) |
            df['Generic Name'].str.contains(search_query, case=False, na=False)
        ]
        
        if not results.empty:
            for _, row in results.iterrows():
                category = row.get('Category', '')
                notes = row.get('Notes / Source', 'missing basic information')
                
                if category == 'FORBIDDEN_CRITICAL':
                    st.error(f"❌ **{row['Brand Name']}** ({row['Generic Name']})\n\n**אסור לכתוש!**\n\n**הנחיות ומקור:** {notes}")
                elif category == 'ENTERIC_COATED':
                    st.warning(f"⚠️ **{row['Brand Name']}** ({row['Generic Name']})\n\n**ציפוי אנטרי / פתיחה בלבד**\n\n**הנחיות ומקור:** {notes}")
                elif category == 'ALLOWED':
                    st.success(f"✅ **{row['Brand Name']}** ({row['Generic Name']})\n\n**מותר לכתוש**\n\n**הנחיות ומקור:** {notes}")
                else:
                    st.info(f"ℹ️ **{row['Brand Name']}** ({row['Generic Name']})\n\n**מידע:** {notes}")
        else:
            # 2. אם לא נמצא ב-CSV המקומי - בדיקה אוטומטית ב-API של משרד הבריאות
            moh_records = search_moh_api(search_query)
            
            if moh_records:
                st.info("🔎 **התרופה אותרה במאגר התרופות הרשמי של משרד הבריאות:**")
                for rec in moh_records:
                    brand = rec.get("DRUG_NAME", rec.get("DRUG_ENGLISH_NAME", search_query))
                    generic = rec.get("DRUG_GENERIC_NAME", "")
                    form = rec.get("DOSAGE_FORM", "")
                    
                    st.warning(
                        f"💊 **{brand}** ({generic})\n\n"
                        f"**צורת מתן רשומה:** {form}\n\n"
                        f"⚠️ **סטטוס קליני:** `missing basic information`\n\n"
                        f"*התרופה רשומה בישראל, אך טרם הוגדרה לגביה הנחיית כתישה מאומתת במאגר. יש להיוועץ ברוקח/ת.*"
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
