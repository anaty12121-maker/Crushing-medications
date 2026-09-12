import streamlit as st
import pandas as pd

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

st.title("💊 מנוע חיפוש והנחיות לכתישת תרופות")

try:
    df = load_data()
    search_query = st.text_input("הקלידי שם תרופה (מסחרי או גנרי):", "")
    
    if search_query:
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
            st.warning("missing basic information (התרופה לא נמצאה במאגר)")
            
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
