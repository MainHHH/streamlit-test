import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import koreanize_matplotlib

df=pd.read_csv("HR Data.csv")

candidate_columns = [
    '퇴직여부', '나이', '성별', '출장빈도', '부서', '집과의거리', '전공',
    '업무환경만족도', '업무참여도', '업무만족도', '결혼여부', '월급여',
    '일한회사수', '야근정도', '급여증가분백분율', '스톡옵션정도',
    '근속연수', '현재역할년수', '마지막승진년수'
]

hr = df[candidate_columns].copy()
hr['퇴직'] = hr['퇴직여부'].map({'No': 0, 'Yes': 1}).astype('int8')
hr['연령대'] = pd.cut(
    hr['나이'],
    bins=[0, 29, 39, 49, 59, 100],
    labels=['20대 이하', '30대', '40대', '50대', '60대 이상']
)

total_employees = len(hr) # 직원수
total_attritions = hr['퇴직'].sum()  # 퇴직자수
overall_rate = round( hr['퇴직'].mean() * 100 , 1) # 퇴직률

def attrition_summary(data, group_column) :
    result = data.groupby(group_column,observed=True ).agg(직원수=('퇴직', 'size'),
                        퇴직자수 = ('퇴직', 'sum'),
                        퇴직률 = ('퇴직', 'mean') ).reset_index()
    result['퇴직률'] = (result['퇴직률'] * 100).round(1)
    return result.sort_values('퇴직률', ascending=False)

department_result = attrition_summary(hr, '부서')
age_result = attrition_summary(hr, '연령대')

st.title("HR 퇴직현황")

# KPI 3개 (전체 직원수, 퇴직자수, 전체 퇴직률)
col_1, col_2, col_3 = st.columns(3)

col_1.metric(label="직원 수", value=f"{total_employees}명")
col_2.metric(label="퇴직자 수", value=f"{total_attritions}명")
col_3.metric(label="퇴직률", value=f"{overall_rate}%")

# 사이드바 필터
with st.sidebar:
    dept = st.selectbox("부서를 선택하세요.", ["전체", "Sales", "Human Resources", "Research & Development"])
    age = st.pills("연령대를 선택하세요.", ["20대 이하", "30대", "40대", "50대", "60대 이상"], selection_mode="multi", default=["20대 이하", "30대", "40대", "50대", "60대 이상"])
    # st.write(age)
if dept != '전체':
    department_result = department_result[department_result["부서"] == dept]

# 그래프 2개
graph_col1, graph_col2 = st.columns(2)

graph_col1.subheader("부서별 퇴직률")

fig1, ax1 = plt.subplots(figsize=(6, 4))
sns.barplot(data=department_result, y="부서", x="퇴직률", ax=ax1)
ax1.set_xlabel("퇴직률")
ax1.axvline(overall_rate, color='red', linestyle='--')
graph_col1.pyplot(fig1)

if age:
    age_result = age_result[age_result["연령대"].isin(age)].copy()
    age_result["연령대"] = age_result["연령대"].cat.remove_unused_categories()

graph_col2.subheader("연령대별 퇴직률")

fig2, ax2 = plt.subplots(figsize=(6, 4))
sns.barplot(data=age_result, x='연령대', y='퇴직률', ax=ax2)
ax2.axhline(overall_rate, color='red', linestyle='--')
graph_col2.pyplot(fig2)