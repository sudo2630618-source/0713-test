import streamlit as st
import pandas as pd

# 1. 웹앱 제목 및 설명
st.set_page_config(page_title="도시 열섬현상 분석", layout="wide")
st.title("🏙️ 서울 vs 🌲 양평 기온 데이터 비교를 통한 도시 열섬현상 분석")
st.markdown("""
본 웹앱은 대도시(서울)와 주변 교외 지역(양평)의 2025년 시간별 기온 데이터를 비교하여, 
도시화로 인해 발생하는 **도시 열섬현상(Urban Heat Island)**을 시각적으로 분석합니다.
""")

# 2. 데이터 로드 및 전처리 함수
@st.cache_data
def load_data():
    # 기상청 데이터 특성상 cp949 인코딩 적용
    seoul = pd.read_csv("서울_기온.csv", encoding="cp949")
    yangpyeong = pd.read_csv("양평_기온.csv", encoding="cp949")
    
    # 일시 컬럼을 datetime 객체로 변환
    seoul['일시'] = pd.to_datetime(seoul['일시'])
    yangpyeong['일시'] = pd.to_datetime(yangpyeong['일시'])
    
    # 분석에 필요한 월(Month)과 시각(Hour) 정보 추출
    seoul['월'] = seoul['일시'].dt.month
    seoul['시각'] = seoul['일시'].dt.hour
    yangpyeong['월'] = yangpyeong['일시'].dt.month
    yangpyeong['시각'] = yangpyeong['일시'].dt.hour
    
    return seoul, yangpyeong

# 데이터 불러오기 예외 처리
try:
    seoul_df, yp_df = load_data()
    
    # 두 데이터의 기온 데이터를 하나로 결합 (선그래프용)
    df_trend = pd.DataFrame({
        '일시': seoul_df['일시'],
        '서울 기온(°C)': seoul_df['기온(°C)'],
        '양평 기온(°C)': yp_df['기온(°C)']
    }).set_index('일시')

    # ==========================================
    # ① 1년간 두 지역의 기온 변화 (선그래프)
    # ==========================================
    st.header("① 1년간 두 지역의 기온 변화 추이")
    st.markdown("2025년 전체 기간 동안 두 지역의 기온이 변화하는 전반적인 흐름을 비교합니다.")
    st.line_chart(df_trend, y=['서울 기온(°C)', '양평 기온(°C)'])
    
    st.markdown("---")
    
    # 레이아웃을 좌우 2컬럼으로 분할하여 시각별/월별 차트 배치
    col1, col2 = pd.columns(2) if hasattr(pd, 'columns') else st.columns(2)
    
    with col1:
        # ==========================================
        # ② 시각(0~23시)별 평균 기온차, 서울-양평 (막대그래프)
        # ==========================================
        st.header("② 시각별 평균 기온차 (서울 - 양평)")
        st.markdown("하루 중 어느 시간대에 열섬현상이 가장 뚜렷하게 나타나는지 분석합니다.")
        
        # 시각별 평균 계산
        seoul_hourly = seoul_df.groupby('시각')['기온(°C)'].mean()
        yp_hourly = yp_df.groupby('시각')['기온(°C)'].mean()
        
        # 기온차 산출 (서울 - 양평)
        hourly_diff = pd.DataFrame({'기온차(서울-양평)': seoul_hourly - yp_hourly})
        st.bar_chart(hourly_diff)
        st.caption("💡 대개 인공열 축적과 지표면 방출 제약으로 인해 밤~새벽 시간대에 기온차가 더 벌어집니다.")

    with col2:
        # ==========================================
        # ③ 월(1~12월)별 평균 기온차, 서울-양평 (막대그래프)
        # ==========================================
        st.header("③ 월별 평균 기온차 (서울 - 양평)")
        st.markdown("계절에 따라 도시와 교외 지역의 기온차가 어떻게 변화하는지 분석합니다.")
        
        # 월별 평균 계산
        seoul_monthly = seoul_df.groupby('월')['기온(°C)'].mean()
        yp_monthly = yp_df.groupby('월')['기온(°C)'].mean()
        
        # 기온차 산출 (서울 - 양평)
        monthly_diff = pd.DataFrame({'기온차(서울-양평)': seoul_monthly - yp_monthly})
        st.bar_chart(monthly_diff)
        st.caption("💡 냉난방 에너지 사용량, 식생의 유무, 기단 등의 영향으로 월별 열섬 강도가 달라집니다.")

    # ==========================================
    # 지구과학적 탐구 결론 요약 지표
    # ==========================================
    st.markdown("---")
    st.header("📊 데이터 요약 및 지구과학적 해석")
    
    total_mean_seoul = seoul_df['기온(°C)'].mean()
    total_mean_yp = yp_df['기온(°C)'].mean()
    avg_diff = total_mean_seoul - total_mean_yp
    
    m_col1, m_col2, m_col3 = st.columns(3)
    m_col1.metric("서울 1년 평균 기온", f"{total_mean_seoul:.2f} °C")
    m_col2.metric("양평 1년 평균 기온", f"{total_mean_yp:.2f} °C")
    m_col3.metric("평균 열섬 강도 (서울-양평)", f"+{avg_diff:.2f} °C", delta_color="inverse")
    
    st.info(f"""
    **지구과학적 현상 매칭 요약:** 2025년 데이터 분석 결과, 서울이 양평보다 평균 약 **{avg_diff:.2f}°C** 높게 관측되었습니다. 
    이는 전형적인 **도시 열섬현상**의 증거로, 인공열 발생, 아스팔트와 건물에 의한 비열 및 알베도 변화, 
    빌딩숲으로 인한 바람길 차단 등이 복합적으로 작용하여 대도시 내부의 열이 쉽게 빠져나가지 못했음을 의미합니다.
    """)

except FileNotFoundError:
    st.error("🚨 파일을 찾을 수 없습니다. '서울_기온.csv'와 '양평_기온.csv' 파일이 웹앱 스크립트(`app.py`)와 같은 폴더에 있는지 확인해주세요.")
except Exception as e:
    st.error(f"🚨 오류가 발생했습니다: {e}")
