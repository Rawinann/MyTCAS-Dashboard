import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# โหลดข้อมูล
df = pd.read_csv("programs_info.csv")

# แปลง cost ให้เป็นตัวเลข (ลบ 'บาท', ',' และแปลงเป็น float)
def parse_cost(value):
    try:
        return float(str(value).replace(',', '').replace('บาท', '').strip())
    except:
        return None

df['cost_num'] = df['cost'].apply(parse_cost)

st.set_page_config(page_title="Dashboard ค่าใช้จ่ายหลักสูตร", layout="wide")
st.title("🎓 Dashboard ค่าใช้จ่ายหลักสูตรมหาวิทยาลัย")
st.markdown("นำเสนอสำหรับอาจารย์หรือผู้บริหารในการเปรียบเทียบค่าใช้จ่ายของหลักสูตรต่าง ๆ")

# -------------------- ฟิลเตอร์ --------------------
universities = df['university'].dropna().unique().tolist()
faculties = df['faculty'].dropna().unique().tolist()
program_types = df['program_type'].dropna().unique().tolist()

col1, col2, col3 = st.columns(3)
with col1:
    selected_uni = st.multiselect("เลือกมหาวิทยาลัย", options=universities, default=universities)
with col2:
    selected_faculty = st.multiselect("เลือกคณะ", options=faculties, default=faculties)
with col3:
    selected_type = st.multiselect("เลือกประเภทหลักสูตร", options=program_types, default=program_types)

# -------------------- กรองข้อมูล --------------------
filtered_df = df[
    df['university'].isin(selected_uni) &
    df['faculty'].isin(selected_faculty) &
    df['program_type'].isin(selected_type)
].copy()

# -------------------- แสดงกราฟ --------------------
st.subheader("📊 ค่าใช้จ่ายเฉลี่ยต่อมหาวิทยาลัย")
avg_cost = (
    filtered_df.groupby("university")["cost_num"]
    .mean()
    .dropna()
    .sort_values(ascending=False)
)

st.bar_chart(avg_cost)

# -------------------- แสดงตาราง --------------------
st.subheader("📄 รายละเอียดหลักสูตร")
st.dataframe(filtered_df[["university", "faculty", "program_name", "program_type", "cost"]])

# -------------------- สรุป --------------------
st.markdown(f"🔢 จำนวนหลักสูตรที่แสดง: **{len(filtered_df)}**")
