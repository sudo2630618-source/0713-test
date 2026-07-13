import streamlit as st
import pandas as pd

# 1. 페이지 설정
st.set_page_config(page_title="도시 열섬 및 전력수요 분석", layout="wide")
st.title("🏙️ 기후와 환경: 도시 열섬현상 및 기온-전력수요 상관분석 대시보드")
st.markdown("본 웹앱은 2025년 시간별 데이터를 바탕으로 대도시의 기온 특성(열섬현상)과 기온에 따른 에너지 소비 패턴을 분석합니다.")

# 2. 데이터 로드 및 전처리 (캐싱 적용)
@st.cache_data
def load_all_data():
    seoul = pd.read_csv("서울_기온.csv", encoding="cp949")
    yangpyeong = pd.read_csv("양평_기온.csv", encoding="cp949")
    power = pd.read_csv("전력수요.csv", encoding="cp949")
    
    seoul['일시'] = pd.to_datetime(seoul['일시'])
    yangpyeong['일시'] = pd.to_datetime(yangpyeong['일시'])
    power['일시'] = pd.to_datetime(power['일시'])
    
    seoul['월'] = seoul['일시'].dt.month
    seoul['시각'] = seoul['일시'].dt.hour
    
    return seoul, yangpyeong, power

try:
    seoul_df, yp_df, power_df = load_all_data()
    
    # 탭 1용 데이터 병합
    geo_df = pd.merge(seoul_df, yp_df, on="일시", suffixes=("_서울", "_양평"))
    geo_df['기온차(서울-양평)'] = geo_df['기온(°C)_서울'] - geo_df['기온(°C)_양평']
    
    # 탭 2용 데이터 병합
    energy_df = pd.merge(seoul_df, power_df, on="일시")
    
    # ----------------------------------------------------------------
    # 3. 레이아웃: st.tabs 분할
    # ----------------------------------------------------------------
    tab1, tab2 = st.tabs(["🌡️ 탭1: 도시 열섬 분석", "⚡ 탭2: 기온과 전력수요 연결"])
    
    # ==========================================
    # [탭 1: 열섬 분석]
    # ==========================================
    with tab1:
        st.header("🏙️ 서울 - 양평 기온 비교를 통한 열섬현상 탐구")
        
        st.subheader("① 1년간 두 지역의 기온 변화 추이")
        df_trend = geo_df[['일시', '기온(°C)_서울', '기온(°C)_양평']].copy()
        df_trend.columns = ['일시', '서울 기온(°C)', '양평 기온(°C)']
        # 브라우저 노드 충돌을 막기 위해 x축 명시 및 명확한 데이터 분리
        st.line_chart(df_trend, x='일시', y=['서울 기온(°C)', '양평 기온(°C)'])
        
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("② 시각별 평균 기온차 (서울 - 양평)")
            # reset_index()를 사용해 정형 데이터프레임으로 강제 변환 (가장 중요!)
            hourly_diff = geo_df.groupby('시각')['기온차(서울-양평)'].mean().reset_index()
            st.bar_chart(hourly_diff, x='시각', y='기온차(서울-양평)')
            st.caption("💡 인공열 방출과 아스팔트 복사열 보존 효과로 보통 야간 및 새벽에 기온차가 뚜렷해집니다.")
            
        with col2:
            st.subheader("③ 월별 평균 기온차 (서울 - 양평)")
            # reset_index()로 인덱스가 아닌 일반 컬럼으로 변환하여 차트에 전달
            monthly_diff = geo_df.groupby('월')['기온차(서울-양평)'].mean().reset_index()
            st.bar_chart(monthly_diff, x='월', y='기온차(서울-양평)')
            st.caption("💡 난방기구 사용이 많은 겨울철이나 대기 정체가 심한 계절에 열섬현상이 강해질 수 있습니다.")

    # ==========================================
    # [탭 2: 전력 연결]
    # ==========================================
    with tab2:
        st.header("⚡ 대도시 기온 변동에 따른 전력수요 패턴 탐구")
        
        st.subheader("① 기온과 전력수요의 분포 (산점도)")
        st.markdown("기온의 변화가 전체적인 전력수요 양상에 미치는 영향력을 시각화합니다.")
        st.scatter_chart(data=energy_df, x='기온(°C)', y='전력수요(MWh)')
        st.caption("💡 일반적으로 기온이 매우 낮을 때(겨울철 난방)와 매우 높을 때(여름철 냉방) 전력수요가 급증하는 U자형 곡선이 나타납니다.")
        
        st.markdown("---")
        col3, col4 = st.columns(2)
        
        with col3:
            st.subheader("② 기온 구간별 평균 전력수요")
            energy_df['기온구간'] = (energy_df['기온(°C)'] // 5) * 5
            temp_band_power = energy_df.groupby('기온구간')['전력수요(MWh)'].mean().reset_index()
            st.bar_chart(temp_band_power, x='기온구간', y='전력수요(MWh)')
            st.caption("💡 정량화된 온도 바스켓별 평균 소비량을 비교하여 냉난방 임계 온도를 파악할 수 있습니다.")
            
        with col4:
            st.subheader("③ 월별 평균 전력수요")
            monthly_power = energy_df.groupby('월')['전력수요(MWh)'].mean().reset_index()
            st.bar_chart(monthly_power, x='월', y='전력수요(MWh)')
            st.caption("💡 계절 변화에 따른 대한민국 전력 소비의 주기적 흐름을 보여줍니다.")

except FileNotFoundError as e:
    st.error("🚨 데이터 파일을 찾을 수 없습니다. '서울_기온.csv', '양평_기온.csv', '전력수요.csv' 세 파일이 현재 스크립트와 동일한 디렉토리에 존재하는지 확인해주세요.")
except Exception as e:
    st.error(f"🚨 애플리케이션 구동 중 오류가 발생했습니다: {e}")
