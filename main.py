#WebVPython 3.2
import streamlit as st
import pandas as pd

# 1. 웹앱 기본 설정 및 제목
st.set_page_config(page_title="도시 열섬 및 전력수요 분석", layout="wide")
st.title("🏙️ 기후와 환경: 도시 열섬현상 및 기온-전력수요 상관분석 대시보드")
st.markdown("본 웹앱은 2025년 시간별 데이터를 바탕으로 대도시의 기온 특성(열섬현상)과 기온에 따른 에너지 소비 패턴을 분석합니다.")

# 2. 데이터 로드 및 전처리 함수
@st.cache_data
def load_all_data():
    # 파일 읽기 (cp949 인코딩 반영)
    seoul = pd.read_csv("서울_기온.csv", encoding="cp949")
    yangpyeong = pd.read_csv("양평_기온.csv", encoding="cp949")
    power = pd.read_csv("전력수요.csv", encoding="cp949")
    
    # 일시 컬럼을 datetime 데이터 타입으로 변환
    seoul['일시'] = pd.to_datetime(seoul['일시'])
    yangpyeong['일시'] = pd.to_datetime(yangpyeong['일시'])
    power['일시'] = pd.to_datetime(power['일시'])
    
    # 분석용 파생 변수(월, 시각) 생성
    seoul['월'] = seoul['일시'].dt.month
    seoul['시각'] = seoul['일시'].dt.hour
    
    return seoul, yangpyeong, power

try:
    # 데이터 로드
    seoul_df, yp_df, power_df = load_all_data()
    
    # [공통 데이터 병합] 일시(datetime)를 기준으로 결합
    # 탭 1용: 서울과 양평 기온 병합 (서울_df에 이미 '월', '시각'이 포함되어 있음)
    geo_df = pd.merge(seoul_df, yp_df, on="일시", suffixes=("_서울", "_양평"))
    geo_df['기온차(서울-양평)'] = geo_df['기온(°C)_서울'] - geo_df['기온(°C)_양평']
    
    # 탭 2용: 서울 기온과 전력수요 병합
    energy_df = pd.merge(seoul_df, power_df, on="일시")
    
    # ----------------------------------------------------------------
    # 3. 레이아웃: st.tabs를 활용한 2개 탭 분할
    # ----------------------------------------------------------------
    tab1, tab2 = st.tabs(["🌡️ 탭1: 도시 열섬 분석", "⚡ 탭2: 기온과 전력수요 연결"])
    
    # ==========================================
    # [탭 1: 열섬 분석]
    # ==========================================
    with tab1:
        st.header("🏙️ 서울 - 양평 기온 비교를 통한 열섬현상 탐구")
        
        # ① 1년간 두 지역 기온 변화 (선그래프)
        st.subheader("① 1년간 두 지역의 기온 변화 추이")
        df_trend = geo_df[['일시', '기온(°C)_서울', '기온(°C)_양평']].set_index('일시')
        df_trend.columns = ['서울 기온(°C)', '양평 기온(°C)']
        st.line_chart(df_trend)
        
        st.markdown("---")
        
        # 좌우 배치를 위한 컬럼 분할
        col1, col2 = st.columns(2)
        
        with col1:
            # ② 시각(0~23시)별 평균 기온차 
            # (오류 수정: '시각_서울' 대신에 병합 전 서울_df에서 넘어온 고유 컬럼 '시각' 사용)
            st.subheader("② 시각별 평균 기온차 (서울 - 양평)")
            hourly_diff = geo_df.groupby('시각')['기온차(서울-양평)'].mean()
            st.bar_chart(hourly_diff)
            st.caption("💡 인공열 방출과 아스팔트 복사열 보존 효과로 보통 야간 및 새벽에 기온차가 뚜렷해집니다.")
            
        with col2:
            # ③ 월(1~12월)별 평균 기온차
            # (오류 수정: '월_서울' 대신에 고유 컬럼 '월' 사용)
            st.subheader("③ 월별 평균 기온차 (서울 - 양평)")
            monthly_diff = geo_df.groupby('월')['기온차(서울-양평)'].mean()
            st.bar_chart(monthly_diff)
            st.caption("💡 난방기구 사용이 많은 겨울철이나 대기 정체가 심한 계절에 열섬현상이 강해질 수 있습니다.")

    # ==========================================
    # [탭 2: 전력 연결]
    # ==========================================
    with tab2:
        st.header("⚡ 대도시 기온 변동에 따른 전력수요 패턴 탐구")
        
        # ① 기온(가로)과 전력수요(세로)의 산점도
        st.subheader("① 기온과 전력수요의 분포 (산점도)")
        st.markdown("기온의 변화가 전체적인 전력수요 양상에 미치는 영향력을 시각화합니다.")
        st.scatter_chart(data=energy_df, x='기온(°C)', y='전력수요(MWh)')
        st.caption("💡 일반적으로 기온이 매우 낮을 때(겨울철 난방)와 매우 높을 때(여름철 냉방) 전력수요가 급증하는 U자형 곡선이 나타납니다.")
        
        st.markdown("---")
        
        col3, col4 = st.columns(2)
        
        with col3:
            # ② 기온 구간별 평균 전력수요 (막대그래프)
            st.subheader("② 기온 구간별 평균 전력수요")
            energy_df['기온구간'] = (energy_df['기온(°C)'] // 5) * 5
            temp_band_power = energy_df.groupby('기온구간')['전력수요(MWh)'].mean()
            st.bar_chart(temp_band_power)
            st.caption("💡 정량화된 온도 바스켓별 평균 소비량을 비교하여 냉난방 임계 온도를 파악할 수 있습니다.")
            
        with col4:
            # ③ 월(1~12월)별 평균 전력수요 (막대그래프)
            st.subheader("③ 월별 평균 전력수요")
            monthly_power = energy_df.groupby('월')['전력수요(MWh)'].mean()
            st.bar_chart(monthly_power)
            st.caption("💡 계절 변화에 따른 대한민국 전력 소비의 주기적 흐름을 보여줍니다.")

except FileNotFoundError as e:
    st.error("🚨 데이터 파일을 찾을 수 없습니다. '서울_기온.csv', '양평_기온.csv', '전력수요.csv' 세 파일이 현재 스크립트와 동일한 디렉토리에 존재하는지 확인해주세요.")
except Exception as e:
    st.error(f"🚨 애플리케이션 구동 중 오류가 발생했습니다: {e}")
