import pandas as pd
import streamlit as st

st.set_page_config(page_title="בדיקת כתישת תרופות", layout="centered")

st.title("💊 בדיקת אפשרות לכתישה/ריסוק תרופות")

# טעינת נתונים
@st.cache_data
def load_data():
    return pd.read_csv("medications.csv")

try:
    df = load_data()
    search = st.text_input("הקלידי שם תרופה (גנרי או מסחרי):")

    if search:
        results = df[df['Generic Name'].str.contains(search, case=False, na=False) | 
                     df['Brand Name'].str.contains(search, case=False, na=False)]
        
        if not results.empty:
            for _, row in results.iterrows():
                st.subheader(f"{row['Brand Name']} ({row['Generic Name']})")
                
                status = row['Can Crush?']
                if status == "Yes":
                    st.success("✅ מותר לרסק")
                elif status == "No":
                    st.error("❌ אסור לרסק")
                else:
                    st.warning("⚠️ missing basic information")
                
                st.write(f"**חלופות:** {row.get('Alternative Form', 'אין')}")
                st.write(f"**הערות ומקור:** {row.get('Notes / Source', '-')}")
                st.markdown("---")
        else:
            st.info("missing basic information")
except Exception as e:
    st.error("יש להעלות קובץ נתונים תקין.")
