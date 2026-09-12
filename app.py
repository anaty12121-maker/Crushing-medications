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
                if category == 'FORBIDDEN_CRITICAL':
                    st.error(f"❌ **{row['Brand Name']}** ({row['Generic Name']})\n\n**אסור לכתוש!**\n\nהערות: {row['Notes / Source']}")
                elif category == 'ENTERIC_COATED':
                    st.warning(f"⚠️ **{row['Brand Name']}** ({row['Generic Name']})\n\n**ציפוי אנטרי / פתיחה בלבד**\n\nהערות: {row['Notes / Source']}")
                elif category == 'ALLOWED':
                    st.success(f"✅ **{row['Brand Name']}** ({row['Generic Name']})\n\n**מותר לכתוש**\n\nהערות: {row['Notes / Source']}")
                else:
                    st.info(f"ℹ️ **{row['Brand Name']}** ({row['Generic Name']})\n\n**מידע:** {row['Notes / Source']}")
        else:
            st.warning("לא נמצאו תרופות התואמות את החיפוש.")
            
except Exception as e:
    st.error("אירעה שגיאה בטעינת המידע.")

st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray; font-size: 0.9em;'>"
    "נבנה ועובד קלינית על ידי ענת יהלום, רוקחת בבתי אבות | סיוע בפיתוח טכני: AI"
    "</div>",
    unsafe_allow_html=True
)
