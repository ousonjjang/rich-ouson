import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

# 페이지 기본 설정
st.set_page_config(page_title="자유 환율 계산기", page_icon="💸")

# --- 1. 사이트 헤더 ---
st.title("💸 자유 환율 계산기")
st.subheader("이 물건을 사면 당신의 은퇴는 얼마나 늦어질까요?")
st.markdown("---")

# --- 2. 사이드바: 내 정보 입력 ---
with st.sidebar:
    st.header("📝 내 소득 정보 입력")
    monthly_income = st.number_input("월 실수령액 (만원)", value=300, step=10)
    work_hours = st.number_input("한 달 총 근무시간 (출퇴근 포함)", value=200, step=10)
    
    # 내 시급 계산
    my_hourly_wage = (monthly_income * 10000) / work_hours
    st.write(f"📊 당신의 진짜 시급: **{int(my_hourly_wage):,}원**")
    st.info("💡 팁: 출퇴근 시간과 야근을 포함해서 냉정하게 적으세요.")

# --- 3. 메인 화면: 소비 입력 ---
st.write("### 👇 지금 지출하려는 금액은?")
cost = st.number_input("금액 입력 (원)", value=25000, step=1000, help="배달비 포함 금액을 적으세요")

# --- 4. 계산 로직 ---
if cost > 0:
    # A. 노동 시간 환산
    time_cost = cost / my_hourly_wage
    
    # B. 미래 가치 (S&P500 10%)
    years = 10
    interest_rate = 0.10
    future_value = cost * ((1 + interest_rate) ** years)
    
    # C. 인플레이션 반영 (짜장면)
    inflation_rate = 0.03
    current_jajang = 7000
    future_jajang_price = current_jajang * ((1 + inflation_rate) ** years)
    jajang_count = future_value / future_jajang_price

    # --- 5. 결과 보여주기 ---
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="😫 이 돈을 벌기 위해 일해야 하는 시간", value=f"{time_cost:.1f} 시간")
    with col2:
        st.metric(label="📉 10년 뒤 잃게 될 자산 (S&P500 10% 기준)", value=f"{int(future_value):,} 원") 

    st.warning(f"🚨 **현실 자각 타임:** \n지금 이 돈을 아껴서 투자하면, 10년 뒤 물가가 올라도 **짜장면 {int(jajang_count)}그릇**을 사먹을 수 있는 돈이 됩니다. 드시겠습니까?")

    # --- 6. 그래프 (Altair) ---
    st.write("#### 📈 내 돈이 10년 동안 S&P500 (연평균 10% 복리)으로 얼마나 불어날까?")
    
    annual_data = []
    for i in range(1, years + 1):
        invest_value = cost * ((1 + interest_rate) ** i)
        cash_value = cost
        annual_data.append({
            "년차": i,
            "S&P500 투자 자산 (10%)": int(invest_value),
            "현금 (0%)": int(cash_value)
        })
    chart_data = pd.DataFrame(annual_data)
    
    df_melted = chart_data.melt('년차', var_name='자산 종류', value_name='금액')
    
    base = alt.Chart(df_melted).encode(
        x=alt.X('년차:O', title='년차', axis=alt.Axis(labelAngle=0)), 
        y=alt.Y('금액', title='금액 (원)', scale=alt.Scale(domain=[0, int(future_value*1.1)])),
        color=alt.Color('자산 종류', scale=alt.Scale(domain=['S&P500 투자 자산 (10%)', '현금 (0%)'], range=['#00CC00', '#FF0000']))
    ).properties(height=300)

    line = base.mark_line().encode(tooltip=['년차:O', alt.Tooltip('금액', format=','), '자산 종류'])
    points = base.mark_circle(size=80).encode(tooltip=['년차:O', alt.Tooltip('금액', format=','), '자산 종류'])
    st.altair_chart(line + points, use_container_width=True) 

    st.write("#### 📝 연도별 자산 변화 상세 수치")
    st.dataframe(chart_data.set_index('년차').style.format('{:,}'), use_container_width=True)
    
    st.markdown("---")

    # --- 7. 판독 결과 및 등급표 (수정된 부분) ---
    st.subheader("🚦 소비 판독 결과")
    
    # 판독 메시지 출력
    if time_cost > 3:
        st.error(f"💀 **[경고] 반나절 노동 삭제!**\n\n이 소비를 위해 당신은 오늘 오전 근무를 전부 공쳤습니다.")
    elif time_cost > 1:
        st.warning(f"🤔 **[고민] 1시간 노동 삭제!**\n\n최저시급 알바생도 1시간은 일해야 이 돈을 법니다. 꼭 필요하신가요?")
    else:
        st.success(f"✅ **[통과] 소소한 행복!**\n\n1시간 미만의 노동으로 감당 가능합니다. 이 정도는 나를 위한 선물로 인정!")

    # 등급 기준표 보여주기 (New!)
    with st.expander("📊 소비 등급 기준표 보기 (다른 단계는 뭐가 있을까?)"):
        st.markdown("""
        * 💀 **경고 (Danger):** 노동 시간 **3시간 초과** (지갑 닫으세요!)
        * 🤔 **고민 (Warning):** 노동 시간 **1시간 ~ 3시간** (신중하세요!)
        * ✅ **통과 (Safe):** 노동 시간 **1시간 미만** (즐기세요!)
        """)

else:
    st.write("☝️ 금액을 입력하면 분석이 시작됩니다.")
