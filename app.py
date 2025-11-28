import streamlit as st
import pandas as pd
import numpy as np
import altair as alt # Altair 라이브러리 추가

# 페이지 기본 설정 (제목, 아이콘 등)
st.set_page_config(page_title="자유 환율 계산기", page_icon="💸")

# --- 1. 사이트 헤더 (어그로 끌기) ---
st.title("💸 자유 환율 계산기")
st.subheader("이 물건을 사면 당신의 은퇴는 얼마나 늦어질까요?")
st.markdown("---")

# --- 2. 사이드바: 내 정보 입력 (한 번 입력하면 끝) ---
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

# --- 4. 계산 로직 (여기가 뇌입니다) ---
if cost > 0:
    # A. 노동 시간 환산
    time_cost = cost / my_hourly_wage
    
    # B. 미래 가치 (기회비용) - S&P500 연 10% 복리, 10년 뒤
    years = 10
    interest_rate = 0.10  # 연평균 10%로 변경
    future_value = cost * ((1 + interest_rate) ** years)
    
    # C. 인플레이션 반영 (물가상승률 3%) - 짜장면 지수
    inflation_rate = 0.03
    current_jajang = 7000
    future_jajang_price = current_jajang * ((1 + inflation_rate) ** years)
    
    # 미래에 사먹을 수 있는 짜장면 개수
    jajang_count = future_value / future_jajang_price

    # --- 5. 결과 보여주기 (팩트 폭행) ---
    st.markdown("---")
    
    # 결과 1: 노동 시간
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="😫 이 돈을 벌기 위해 일해야 하는 시간", value=f"{time_cost:.1f} 시간")
    with col2:
        # 라벨 수정: S&P500 연평균 10% 명시
        st.metric(label="📉 10년 뒤 잃게 될 자산 (S&P500 연평균 10% 기준)", value=f"{int(future_value):,} 원") 

    # 결과 2: 인플레이션 현실 (짜장면)
    st.warning(f"🚨 **현실 자각 타임:** \n지금 이 돈을 아껴서 투자하면, 10년 뒤 물가가 올라도 **짜장면 {int(jajang_count)}그릇**을 사먹을 수 있는 돈이 됩니다. 드시겠습니까?")

    # --- 6. 그래프 시각화 및 연간 데이터 테이블 (수정된 부분) ---
    st.write("#### 📈 내 돈이 10년 동안 S&P500 (연평균 10% 복리)으로 얼마나 불어날까?")
    
    # 연간 데이터 생성
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
    
    # --- Altair를 사용하여 선 + 점(마커) 그래프 구현 ---
    # 1. 데이터 재구조화 (Altair Long-Format 요구사항)
    df_melted = chart_data.melt('년차', var_name='자산 종류', value_name='금액')

    # 2. 기본 차트 설정
    base = alt.Chart(df_melted).encode(
        x=alt.X('년차:O', title='년차'), # O: 순서형 데이터 (연도 구분)
        y=alt.Y('금액', title='금액 (원)', scale=alt.Scale(domain=[0, int(future_value*1.1)])), # Y축 범위 설정
        color=alt.Color('자산 종류', scale=alt.Scale(domain=['S&P500 투자 자산 (10%)', '현금 (0%)'], range=['#00CC00', '#FF0000']))
    ).properties(
        height=300
    )

    # 3. 선 그래프 레이어
    line = base.mark_line().encode(
        tooltip=['년차:O', alt.Tooltip('금액', format=','), '자산 종류']
    )

    # 4. 점(마커) 그래프 레이어
    points = base.mark_circle(size=80).encode( # size: 점의 크기
        tooltip=['년차:O', alt.Tooltip('금액', format=','), '자산 종류']
    )

    # 5. 선과 점 레이어 결합 후 Streamlit에 출력
    st.altair_chart(line + points, use_container_width=True) 
    # --------------------------------------------------------
    
    # 표로 나타내기 (연도별 수치)
    st.write("#### 📝 연도별 자산 변화 상세 수치 (S&P500 10% vs 현금)")
    st.dataframe(
        chart_data.set_index('년차').style.format('{:,}'), # 천 단위 구분 기호 추가
        use_container_width=True
    )
    st.markdown("---")


    # --- 7. 마지막 한마디 ---
    if time_cost > 3:
        st.error("💀 경고: 이 소비를 위해 당신은 오늘 오전 근무를 전부 공쳤습니다.")
    elif time_cost > 1:
        st.warning("🤔 고민: 1시간 노동을 태울 가치가 있나요?")
    else:
        st.success("✅ 통과: 이 정도는 나를 위한 선물로 인정!")

else:
    st.write("☝️ 금액을 입력하면 분석이 시작됩니다.")
