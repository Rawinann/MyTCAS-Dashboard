import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import altair as alt

# โหลดข้อมูล
df = pd.read_csv("programs_info.csv")

# แปลง cost ให้เป็นตัวเลข
def parse_cost(value):
    try:
        return float(str(value).replace(',', '').replace('บาท', '').strip())
    except:
        return None

df['cost_num'] = df['cost'].apply(parse_cost)

# -------------------- Page Setting --------------------
st.set_page_config(page_title="Dashboard ค่าใช้จ่ายหลักสูตร", layout="wide")
st.title("🎓 Dashboard ค่าใช้จ่ายหลักสูตรมหาวิทยาลัย")
st.markdown("📌 ออกแบบสำหรับนักเรียนมัธยมที่กำลังเลือกมหาวิทยาลัย")

# -------------------- Sidebar Filters --------------------
st.sidebar.header("🔍 ตัวกรอง")

universities = df['university'].dropna().unique().tolist()
faculties = df['faculty'].dropna().unique().tolist()
program_types = df['program_type'].dropna().unique().tolist()

# 🏫 มหาวิทยาลัย
select_all_uni = st.sidebar.checkbox("เลือกมหาวิทยาลัยทั้งหมด", value=True)
selected_uni = st.sidebar.multiselect(
    "เลือกมหาวิทยาลัย",
    options=universities,
    default=universities if select_all_uni else []
)

# 🏛️ คณะ
select_all_faculty = st.sidebar.checkbox("เลือกคณะทั้งหมด", value=True)
selected_faculty = st.sidebar.multiselect(
    "เลือกคณะ",
    options=faculties,
    default=faculties if select_all_faculty else []
)

# 📚 ประเภทหลักสูตร
selected_type = st.sidebar.multiselect("เลือกประเภทหลักสูตร", options=program_types, default=program_types)

# 🔍 คำค้นหาชื่อหลักสูตร
keyword = st.sidebar.text_input("🔎 ค้นหาชื่อหลักสูตร (เช่น AI, Data, Robotics)")

# -------------------- Filter Data --------------------
filtered_df = df[
    df['university'].isin(selected_uni) &
    df['faculty'].isin(selected_faculty) &
    df['program_type'].isin(selected_type)
].copy()

if keyword:
    filtered_df = filtered_df[filtered_df['program_name'].str.contains(keyword, case=False, na=False)]

# -------------------- Dashboard --------------------
st.subheader("📊 ค่าใช้จ่ายเฉลี่ยต่อมหาวิทยาลัย")

avg_cost = (
    filtered_df.groupby("university")["cost_num"]
    .mean()
    .dropna()
    .sort_values(ascending=False)
    .reset_index()
)

if not avg_cost.empty:
    chart = alt.Chart(avg_cost).mark_bar().encode(
        x=alt.X("cost_num:Q", title="ค่าใช้จ่ายเฉลี่ย (บาท)"),
        y=alt.Y("university:N", sort='-x', title="มหาวิทยาลัย"),
        tooltip=["university", "cost_num"]
    ).properties(
        width=700,
        height=40 * len(avg_cost)
    )

    st.altair_chart(chart, use_container_width=True)
else:
    st.info("ไม่มีข้อมูลมหาวิทยาลัยที่ตรงกับเงื่อนไข")

# -------------------- Top N Expensive Programs --------------------
st.subheader("💸 5 หลักสูตรที่ถูกที่สุด")
cheapest_programs = (
    filtered_df
    .dropna(subset=['cost_num'])
    .sort_values('cost_num', ascending=True)
    .head(5)
)
if not cheapest_programs.empty:
    st.table(
        cheapest_programs[["university", "faculty", "program_name", "program_type", "cost"]]
        .reset_index(drop=True)
        .rename(columns={
            "university": "มหาวิทยาลัย",
            "faculty": "คณะ",
            "program_name": "ชื่อหลักสูตร",
            "program_type": "ประเภทหลักสูตร",
            "cost": "ค่าใช้จ่าย"
        })
    )
else:
    st.info("ไม่มีข้อมูลหลักสูตรที่ถูกที่สุด")

st.subheader("💰 5 หลักสูตรที่แพงที่สุด")
expensive_programs = (
    filtered_df
    .dropna(subset=['cost_num'])
    .sort_values('cost_num', ascending=False)
    .head(5)
)
if not expensive_programs.empty:
    st.table(
        expensive_programs[["university", "faculty", "program_name", "program_type", "cost"]]
        .reset_index(drop=True)
        .rename(columns={
            "university": "มหาวิทยาลัย",
            "faculty": "คณะ",
            "program_name": "ชื่อหลักสูตร",
            "program_type": "ประเภทหลักสูตร",
            "cost": "ค่าใช้จ่าย"
        })
    )
else:
    st.info("ไม่มีข้อมูลหลักสูตรที่แพงที่สุด")

# -------------------- รายละเอียดตาราง --------------------
st.subheader("📄 รายละเอียดหลักสูตร")
st.dataframe(filtered_df[["university", "faculty", "program_name", "program_type", "cost"]])

# -------------------- ดาวน์โหลด CSV --------------------
st.download_button(
    label="📥 ดาวน์โหลดข้อมูล (CSV)",
    data=filtered_df.to_csv(index=False),
    file_name="filtered_programs.csv",
    mime="text/csv"
)

# -------------------- Summary --------------------
st.markdown(f"📌 จำนวนหลักสูตรที่แสดง: **{len(filtered_df)}**")
