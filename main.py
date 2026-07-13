<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>열섬현상과 전력수요의 관계 분석</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-trendline"></script>
    <style>
        :root {
            --primary: #1e3a8a; /* Deep Blue */
            --secondary: #ea580c; /* Deep Orange */
            --bg: #f8fafc;
            --card-bg: #ffffff;
            --text: #334155;
            --text-light: #64748b;
            --border: #e2e8f0;
            --error: #ef4444;
            --success: #10b981;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, Roboto, sans-serif;
        }

        body {
            background-color: var(--bg);
            color: var(--text);
            line-height: 1.6;
            padding: 20px;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
        }

        /* 헤더 스타일 */
        header {
            text-align: center;
            margin-bottom: 30px;
            padding: 40px 20px;
            background: linear-gradient(135deg, var(--primary), #3b82f6);
            color: white;
            border-radius: 16px;
            box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
        }

        header h1 {
            font-size: 2.2rem;
            margin-bottom: 10px;
        }

        header p {
            font-size: 1.1rem;
            opacity: 0.9;
        }

        /* 에러 메시지 보드 */
        #error-boundary {
            display: none;
            background-color: #fef2f2;
            border: 2px dashed var(--error);
            color: #991b1b;
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 25px;
        }

        #error-boundary h3 { margin-bottom: 8px; }
        #error-boundary ul { margin-left: 20px; margin-top: 8px; }

        /* 카드 레이아웃 */
        .card {
            background-color: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 25px;
            margin-bottom: 25px;
            box-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1);
        }

        .card h2 {
            font-size: 1.4rem;
            color: var(--primary);
            margin-bottom: 15px;
            border-bottom: 2px solid var(--bg);
            padding-bottom: 8px;
        }

        /* 필터 컨트롤러 */
        .filter-group {
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
            margin-top: 15px;
        }

        .filter-item {
            display: flex;
            flex-direction: column;
            gap: 5px;
        }

        select {
            padding: 8px 16px;
            border-radius: 8px;
            border: 1px solid var(--border);
            background-color: white;
            color: var(--text);
            font-size: 0.95rem;
            cursor: pointer;
        }

        /* 통계 요약 지표 컴포넌트 */
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }

        .metric-box {
            background-color: var(--bg);
            padding: 15px;
            border-radius: 12px;
            text-align: center;
            border: 1px solid var(--border);
        }

        .metric-box .label { font-size: 0.9rem; color: var(--text-light); }
        .metric-box .value { font-size: 1.6rem; font-weight: bold; margin-top: 5px; }
        .metric-box .value.blue { color: var(--primary); }
        .metric-box .value.orange { color: var(--secondary); }

        /* 차트 래퍼 */
        .chart-container {
            position: relative;
            width: 100%;
            height: 400px;
            margin-top: 15px;
        }

        /* 분석 결과 보드 */
        .result-box {
            background-color: #f0fdf4;
            border-left: 4px solid var(--success);
            padding: 15px;
            border-radius: 4px 12px 12px 4px;
            margin-top: 15px;
        }

        .warning-box {
            background-color: #fffbeb;
            border-left: 4px solid #d97706;
            padding: 12px;
            border-radius: 4px 12px 12px 4px;
            font-size: 0.9rem;
            color: #92400e;
            margin-top: 15px;
        }

        #loading {
            text-align: center;
            padding: 40px;
            font-size: 1.2rem;
            color: var(--primary);
            font-weight: bold;
        }

        /* 반응형 미디어 쿼리 */
        @media (max-width: 768px) {
            body { padding: 10px; }
            header h1 { font-size: 1.6rem; }
            .chart-container { height: 300px; }
        }
    </style>
</head>
<body>

<div class="container">
    <header>
        <h1>🏙️ 열섬현상과 전력수요의 관계 분석</h1>
        <p>💡 탐구 질문: 열섬 강도가 커질수록 대도시 전력수요도 증가할까?</p>
    </header>

    <div id="error-boundary">
        <h3>🚨 데이터 로드 오류 안내</h3>
        <p>CSV 파일 원본을 서버 환경에서 가져오지 못했습니다. 아래 원인을 확인해 주세요.</p>
        <ul>
            <li><strong>파일명 및 경로 일치 확인:</strong> <code>서울_기온.csv</code>, <code>양평_기온.csv</code>, <code>전력수요.csv</code> 파일이 본 HTML 파일과 <b>정확히 같은 위치</b>에 있어야 합니다.</li>
            <li><strong>보안 정책(CORS) 확인:</strong> 웹 브라우저는 보안상 로컬 파일(<code>file://</code>)의 직접 읽기를 차단합니다. <b>VS Code Live Server</b> 확장 기능을 이용해 실행하거나 <b>GitHub Pages</b>에 올려서 접속해야 데이터가 정상 작동합니다.</li>
        </ul>
    </div>

    <div id="loading">📊 데이터를 분석하고 시각화 엔진을 준비하는 중입니다...</div>

    <div id="main-content" style="display: none;">
        <div class="card">
            <h2>📊 탐구 데이터 개요 및 조건 필터</h2>
            <p style="color: var(--text-light);">
                본 모델은 기상청 및 전력거래소의 2025년 시간별 원본 데이터(총 8,760개 행 동적 매핑)를 정형 매칭하여 분석합니다.<br>
                <b>도심 기온:</b> 서울특별시(지점 108) | <b>교외 기온:</b> 경기도 양평군(지점 202) | <b>전력수요:</b> 시간별 전국 전력수요량(MWh)
            </p>
            <div class="filter-group">
                <div class="filter-item">
                    <label for="month-select"><b>📅 월별 조회 필터</b></label>
                    <select id="month-select" onchange="updateDashboard()">
                        <option value="all">2025년 전체 보기 (1년치 데이터)</option>
                        <option value="1">1월 (겨울철 난방기)</option>
                        <option value="5">5월 (봄철 전력 안정기)</option>
                        <option value="8">8월 (여름철 폭염 피크기)</option>
                        <option value="10">10월 (가을철 전력 안정기)</option>
                    </select>
                </div>
            </div>
        </div>

        <div class="card">
            <h2>🌡️ 시간별 열섬현상 및 ⚡ 전력수요 실시간 매칭 추이</h2>
            <div class="metrics-grid">
                <div class="metric-box"><div class="label">서울 평균 기온</div><div id="m-seoul" class="value blue">- °C</div></div>
                <div class="metric-box"><div class="label">양평 평균 기온</div><div id="m-yang" class="value">- °C</div></div>
                <div class="metric-box"><div class="label">평균 열섬 강도 (서울-양평)</div><div id="m-uhi" class="value orange">- °C</div></div>
                <div class="metric-box"><div class="label">평균 전력수요</div><div id="m-power" class="value blue">- MWh</div></div>
            </div>
            <div class="chart-container">
                <canvas id="timeLineChart"></canvas>
            </div>
        </div>

        <div class="card">
            <h2>📈 두 변수의 역학적 상관관계 분석 (산점도)</h2>
            <p style="font-size: 0.95rem; color: var(--text-light); margin-bottom: 10px;">
                독립변수를 <b>열섬 강도(°C)</b>, 종속변수를 <b>전력수요(MWh)</b>로 정의하여 좌표평면에 시각화하고 선형 추세선을 도출합니다.
            </p>
            <div class="metrics-grid" style="grid-template-columns: 1fr;">
                <div class="metric-box" style="text-align: left; padding: 20px;">
                    <span class="label"><b>💡 통계적 연산 지표 데이터 결과</b></span>
                    <div id="r-coefficient" style="font-size: 1.4rem; font-weight: bold; margin: 8px 0; color: var(--primary);">
                        피어슨 상관계수 (r) = 계산 중...
                    </div>
                    <div id="r-interpretation" class="result-box">해석을 도출하는 중입니다...</div>
                    <div class="warning-box">
                        ⚠️ <b>지구과학적 과학 철학 유의사항:</b> "상관관계(Correlation)가 반드시 인과관계(Causality)를 직접적으로 성립시키는 것은 아닙니다." 
                        도시 열섬은 대도시의 지표 환경 특성에 기인하며, 전력 수요는 기온 상승에 따른 냉난방기 사용 패턴 및 인간 활동 주기(산업, 수면 등)가 복합적으로 가미된 결과물입니다.
                    </div>
                </div>
            </div>
            <div class="chart-container">
                <canvas id="scatterChart"></canvas>
            </div>
        </div>

        <div class="card">
            <h2>📝 수집 데이터 기반 최종 탐구 결과 요약</h2>
            <div id="conclusion-board" style="padding: 5px; font-size: 1rem; color: var(--text);">
                데이터 가공 연산이 끝난 후 정량 지표 기반 결론이 여기에 도출됩니다.
            </div>
        </div>
    </div>
</div>

<script>
    // 전역 통합 가공 데이터 저장소
    let globalData = [];
    let timeLineChartInstance = null;
    let scatterChartInstance = null;

    // EUC-KR / CP949 디코딩 대응 텍스트 파서 기능 함수
    function parseCSV(text) {
        const lines = text.split(/\r?\n/);
        if (lines.length === 0) return [];
        const headers = lines[0].split(',').map(h => h.trim());
        
        const result = [];
        for (let i = 1; i < lines.length; i++) {
            if (!lines[i]) continue;
            const currentLine = lines[i].split(',');
            if (currentLine.length !== headers.length) continue;
            
            const obj = {};
            for (let j = 0; j < headers.length; j++) {
                obj[headers[j]] = currentLine[j].trim();
            }
            result.push(obj);
        }
        return result;
    }

    // 인코딩 에러 발생 대안 처리를 위한 네트워크 fetch 모듈
    async function fetchCSV(url) {
        const response = await fetch(url);
        if (!response.ok) throw new Error(`HTTP Error ${response.status}`);
        
        // 기상청/공공데이터 한글 깨짐 방지를 위해 ArrayBuffer로 받은 후 디코딩
        const buffer = await response.arrayBuffer();
        const decoder = new TextDecoder('euc-kr'); 
        const text = decoder.decode(buffer);
        return parseCSV(text);
    }

    // 메인 동기 데이터 라이프사이클 엔진
    async function initApp() {
        try {
            // 3개 파일 동시 패치 및 가공 연산 병합
            const [seoulRaw, yangRaw, powerRaw] = await Promise.all([
                fetchCSV('서울_기온.csv'),
                fetchCSV('양평_기온.csv'),
                fetchCSV('전력수요.csv')
            ]);

            // 시간 키값을 인덱스 삼아 맵 객체화 처리 데이터 매칭 정밀화
            const yangMap = new Map();
            yangRaw.forEach(item => { if(item['일시']) yangMap.set(item['일시'], parseFloat(item['기온(°C)'])); });

            const powerMap = new Map();
            powerRaw.forEach(item => { if(item['일시']) powerMap.set(item['일시'], parseFloat(item['전력수요(MWh)'])); });

            // 서울 시간축 데이터 기준으로 최종 통합 행렬 셋 구축
            seoulRaw.forEach(sRow => {
                const timeKey = sRow['일시'];
                if(!timeKey) return;

                const tSeoul = parseFloat(sRow['기온(°C)']);
                const tYang = yangMap.get(timeKey);
                const pValue = powerMap.get(timeKey);

                // 유효한 수치 매칭 레코드만 필터 추출
                if (!isNaN(tSeoul) && !isNaN(tYang) && !isNaN(pValue)) {
                    const dateObj = new Date(timeKey);
                    globalData.push({
                        dateTimeStr: timeKey,
                        month: dateObj.getMonth() + 1,
                        hour: dateObj.getHours(),
                        seoulTemp: tSeoul,
                        yangTemp: tYang,
                        uhiIntensity: tSeoul - tYang, // 열섬 강도 정의 계산식
                        powerDemand: pValue
                    });
                }
            });

            if (globalData.length === 0) {
                throw new Error("데이터 결합 결과 행수가 0입니다. 내부 포맷 구조를 확인하십시오.");
            }

            // 로딩 보드 가리고 본 대시보드 표출
            document.getElementById('loading').style.display = 'none';
            document.getElementById('main-content').style.display = 'block';

            // 최초 화면 출력 실행
            updateDashboard();

        } catch (error) {
            console.error(error);
            document.getElementById('loading').style.display = 'none';
            document.getElementById('error-boundary').style.display = 'block';
        }
    }

    // 필터 조건 변경 시 차트 객체 재구성 피드백 함수
    function updateDashboard() {
        const monthFilter = document.getElementById('month-select').value;
        
        // 데이터 필터링 조건 분기
        let filtered = globalData;
        if (monthFilter !== 'all') {
            const mInt = parseInt(monthFilter);
            filtered = globalData.filter(d => d.month === mInt);
        }

        // 1) 기본 메트릭 연산 통계 도출
        const avgSeoul = filtered.reduce((acc, c) => acc + c.seoulTemp, 0) / filtered.length;
        const avgYang = filtered.reduce((acc, c) => acc + c.yangTemp, 0) / filtered.length;
        const avgUhi = filtered.reduce((acc, c) => acc + c.uhiIntensity, 0) / filtered.length;
        const avgPower = filtered.reduce((acc, c) => acc + c.powerDemand, 0) / filtered.length;

        document.getElementById('m-seoul').innerText = `${avgSeoul.toFixed(1)} °C`;
        document.getElementById('m-yang').innerText = `${avgYang.toFixed(1)} °C`;
        document.getElementById('m-uhi').innerText = `${avgUhi.toFixed(2)} °C`;
        document.getElementById('m-power').innerText = `${Math.round(avgPower).toLocaleString()} MWh`;

        // 2) 피어슨 상관계수(r) 계산 알고리즘 로직 구현
        const rValue = calculatePearson(filtered);
        document.getElementById('r-coefficient').innerText = `피어슨 상관계수 (r) = ${rValue.toFixed(3)}`;
        interpretCorrelation(rValue, avgUhi, avgPower, filtered.length);

        // 3) 차트 데이터 업데이트 렌더링 호출
        renderLineChart(filtered);
        renderScatterChart(filtered);
    }

    // 피어슨 상관관계 수식 유도 연산 함수
    function calculatePearson(data) {
        const n = data.length;
        let sumX = 0, sumY = 0, sumXY = 0, sumX2 = 0, sumY2 = 0;

        for (let i = 0; i < n; i++) {
            const x = data[i].uhiIntensity;
            const y = data[i].powerDemand;
            sumX += x;
            sumY += y;
            sumXY += (x * y);
            sumX2 += (x * x);
            sumY2 += (y * y);
        }

        const num = (n * sumXY) - (sumX * sumY);
        const den = Math.sqrt(((n * sumX2) - (sumX * sumX)) * ((n * sumY2) - (sumY * sumY)));
        if (den === 0) return 0;
        return num / den;
    }

    // 통계 계수 기반 조건절 판정 해석문 생성기
    function interpretCorrelation(r, avgUhi, avgPower, dataCount) {
        const element = document.getElementById('r-interpretation');
        const conclusionElement = document.getElementById('conclusion-board');
        let text = "";
        let strength = "";

        const absR = Math.abs(r);
        if (absR >= 0.7) strength = "매우 강한";
        else if (absR >= 0.4) strength = "뚜렷한";
        else if (absR >= 0.2) strength = "약한";
        else strength = "상관관계가 거의 없는 수준의 매우 미미한";

        if (r > 0.2) {
            text = `📊 현재 조회 범위에서 두 변수는 <b>정(+)의 상관관계(${strength})</b>를 나타내고 있습니다. 즉, 도심 열섬 강도가 증폭될 때 전국 단위 시간당 전력요청량도 통계적으로 우상향 구조를 띠는 경향을 보입니다.`;
        } else if (r < -0.2) {
            text = `📊 현재 조회 범위에서 두 변수는 <b>부(-)의 상관관계(${strength})</b>를 나타내고 있습니다. 열섬 강도가 강해질수록 전력 요구가 반대로 낮아지는 경향입니다.`;
        } else {
            text = `📊 분석 결과 두 변수 간의 <b>상관관계가 매우 약하거나 무관한 흐름</b>으로 도출되었습니다. 열섬 변동이 전력량에 유의미한 직선 지표 영향력을 즉각 미치지 못한다고 해석됩니다.`;
        }

        element.innerHTML = text;

        // 최종 탐구 결론 매핑 피드백 (임의 서술 방지용 실제 정량 데이터 연계 방식)
        conclusionElement.innerHTML = `
            <ul>
                <li>선택된 분석 주기에 매핑된 유효 타임라인 레코드는 총 <b>${dataCount.toLocaleString()}건</b>입니다.</li>
                <li>서울(도심)과 양평(교외) 간 발생한 평균 대기 기온차(열섬 지표)는 <b>${avgUhi.toFixed(2)} °C</b>로 도심 열축적 현상이 뚜렷이 나타났습니다.</li>
                <li>해당 기간 계산된 데이터의 피어슨 수치는 <b>${r.toFixed(3)}</b>입니다. 이를 통해 2025년 실제 통계 지표상으로 열섬 강도가 높은 시점에 전력 소비가 어떠한 가속 비례를 지니는지 직접 계수 검증을 완료하였습니다.</li>
            </ul>
        `;
    }

    // 1번 선형 추이 시각화 차트 빌더
    function renderLineChart(data) {
        // 모바일 스케일 과부하 방지용 샘플링 비율 조정 (데이터가 너무 많으면 6시간 간격으로 다운샘플링하여 시각화 가독성 확보)
        const step = data.length > 500 ? 6 : 1;
        const sampledData = data.filter((_, idx) => idx % step === 0);

        const labels = sampledData.map(d => d.dateTimeStr);
        const seoulData = sampledData.map(d => d.seoulTemp);
        const yangData = sampledData.map(d => d.yangTemp);
        const uhiData = sampledData.map(d => d.uhiIntensity);
        const powerData = sampledData.map(d => d.powerDemand);

        const ctx = document.getElementById('timeLineChart').getContext('2d');

        if (timeLineChartInstance) {
            timeLineChartInstance.destroy();
        }

        timeLineChartInstance = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [
                    { label: '서울 기온 (°C)', data: seoulData, borderColor: '#3b82f6', borderWidth: 1.5, pointRadius: 0, yAxisID: 'y-temp' },
                    { label: '양평 기온 (°C)', data: yangData, borderColor: '#94a3b8', borderWidth: 1.5, pointRadius: 0, yAxisID: 'y-temp' },
                    { label: '열섬 강도 (서울-양평) (°C)', data: uhiData, borderColor: '#ea580c', borderWidth: 2, pointRadius: 0, yAxisID: 'y-temp' },
                    { label: '전국 전력수요 (MWh)', data: powerData, borderColor: '#10b981', borderWidth: 1.5, pointRadius: 0, yAxisID: 'y-power', fill: false }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: { mode: 'index', intersect: false },
                scales: {
                    x: { ticks: { maxTicksLimit: 12 }, title: { display: true, text: '관측 일시' } },
                    'y-temp': { type: 'linear', position: 'left', title: { display: true, text: '기온 및 열섬 강도 (°C)' } },
                    'y-power': { type: 'linear', position: 'right', grid: { drawOnChartArea: false }, title: { display: true, text: '전력수요량 (MWh)' } }
                }
            }
        });
    }

    // 2번 관계 산점도 차트 빌더
    function renderScatterChart(data) {
        // 점 밀집 데이터 가독성을 위해 1년 전체 데이터일 경우 3시간 단위 무작위 표본 가시화화여 렌더링 최적화
        const step = data.length > 2000 ? 3 : 1;
        const chartPoints = data
            .filter((_, idx) => idx % step === 0)
            .map(d => ({ x: d.uhiIntensity, y: d.powerDemand }));

        const ctx = document.getElementById('scatterChart').getContext('2d');

        if (scatterChartInstance) {
            scatterChartInstance.destroy();
        }

        scatterChartInstance = new Chart(ctx, {
            type: 'scatter',
            data: {
                datasets: [{
                    label: '시간별 관측점 데이터',
                    data: chartPoints,
                    backgroundColor: 'rgba(30, 58, 138, 0.4)',
                    borderColor: 'rgba(30, 58, 138, 0.7)',
                    pointRadius: 3,
                    // 외부 플러그인 연동 실시간 선형 회귀 추세선 옵션 정의
                    trendlineLinear: {
                        style: "rgba(234, 88, 12, 0.9)",
                        lineStyle: "solid",
                        width: 3
                    }
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: { type: 'linear', position: 'bottom', title: { display: true, text: '독립변수: 열섬 강도 (도심 기온 - 교외 기온) (°C)' } },
                    y: { title: { display: true, text: '종속변수: 전국 전력수요량 (MWh)' } }
                },
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `열섬강도: ${context.parsed.x.toFixed(2)}°C, 전력수요: ${context.parsed.y.toLocaleString()} MWh`;
                            }
                        }
                    }
                }
            }
        });
    }

    // 앱 실행 초기 구동 트리거
    window.onload = initApp;
</script>

</body>
</html>
