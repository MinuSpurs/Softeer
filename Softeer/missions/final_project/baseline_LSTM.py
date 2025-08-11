# -*- coding: utf-8 -*-
import os
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import tensorflow as tf

# (선택) 애플 실리콘 GPU 활성화 확인용
print("TF version:", tf.__version__)
print("Physical GPUs:", tf.config.list_physical_devices('GPU'))

# ------------------------
# 0) 설정
# ------------------------
DATA_PATH = "/Users/minwoo/Desktop/softeer/data_engineering_course_materials/missions/final_project/data/172_시간대별_정류장_노선_추정승하차+운행횟수+순서.csv"
OUT_PATH  = "/Users/minwoo/Desktop/softeer/data_engineering_course_materials/missions/final_project/data/172_LSTM_preds_정류장별_시간별_승하차_예측.csv"

SEQ_LEN_HOURS = 24         # 과거 몇 시간 시퀀스로 학습할지 (예: 24시간)
TARGET_COLS = ['승차인원','하차인원']
FEAT_COLS   = ['승차인원','하차인원','운행횟수']  # 필요시 요일/시간 더 추가 가능

TRAIN_START = "2025-06-01"
TRAIN_END   = "2025-06-21"
TEST_START  = "2025-06-22"
TEST_END    = "2025-06-29"

# ------------------------
# 1) 데이터 로드 & 기본 전처리
# ------------------------
df = pd.read_csv(DATA_PATH, encoding='utf-8-sig')
df['기준_날짜'] = pd.to_datetime(df['기준_날짜'])
df['timestamp'] = df['기준_날짜'] + pd.to_timedelta(df['시간'], unit='h')

# 172번 한 노선 내 정류장 순서 고정셋 확보 (누락/중복 대비)
stops = (df[['정류장_ID','정류장_순서','역명']]
         .drop_duplicates(subset=['정류장_ID','정류장_순서'])
         .sort_values('정류장_순서'))
stop_ids = stops['정류장_ID'].tolist()
n_stops = len(stop_ids)
print(f"정류장 수: {n_stops}")
# 정류장 순서를 안전하게 사용하기 위한 맵 (정류장_ID -> 0..n-1)
order_map = {sid: idx for idx, sid in enumerate(stop_ids)}

# 누락 방지: 모든 timestamp × 정류장_ID 그리드 생성
all_ts = pd.date_range(df['timestamp'].min().floor('h'),
                       df['timestamp'].max().ceil('h'),
                       freq='h')
full_idx = pd.MultiIndex.from_product([all_ts, stop_ids], names=['timestamp','정류장_ID'])
df_panel = (df.set_index(['timestamp','정류장_ID'])
              .reindex(full_idx)
              .reset_index())

# 기본 컬럼 채우기
# 정류장_순서 / 역명 붙이기
df_panel = df_panel.merge(stops[['정류장_ID','정류장_순서','역명']], on='정류장_ID', how='left')
# 날짜/시간 복구
df_panel['기준_날짜'] = df_panel['timestamp'].dt.date
df_panel['시간'] = df_panel['timestamp'].dt.hour

# 결측치 처리: 승하/운행횟수 NaN은 0으로 (없으면 0으로 가정)
for c in ['승차인원','하차인원','운행횟수']:
    if c in df_panel.columns:
        df_panel[c] = df_panel[c].fillna(0.0)
    else:
        df_panel[c] = 0.0

# 요일/주말 플래그 추가(원하면 feature에 포함 가능)
df_panel['weekday'] = pd.to_datetime(df_panel['기준_날짜']).dt.weekday
df_panel['is_weekend'] = (df_panel['weekday'] >= 5).astype(int)

# ------------------------
# 2) 학습/테스트 구간 분리
# ------------------------
train_mask = (pd.to_datetime(df_panel['기준_날짜']) >= TRAIN_START) & (pd.to_datetime(df_panel['기준_날짜']) <= TRAIN_END)
test_mask  = (pd.to_datetime(df_panel['기준_날짜']) >= TEST_START)  & (pd.to_datetime(df_panel['기준_날짜']) <= TEST_END)

df_train = df_panel[train_mask].copy()
df_test  = df_panel[test_mask].copy()

# ------------------------
# 3) 시간별로 정류장 순서로 정렬해 "한 시간의 모든 정류장"을 한 덩어리로 만듦
#    시계열 축 = 과거 HOURS × (정류장 순서로 Concatenate)
# ------------------------
def build_hourly_blocks(df_):
    # 한 timestamp(=한 시간)에 대해 정류장 순서대로 정렬 후 matrix (n_stops × feat_dim) 생성
    blocks = {}
    for ts, g in df_.groupby('timestamp'):
        # 안전 정렬: 마스터 순서를 기반으로 정렬 (정류장_순서가 없거나 NaN인 경우 대비)
        g = g.copy()
        g['_ord'] = g['정류장_ID'].map(order_map)
        g['_ord'] = g['_ord'].fillna(len(order_map) + 1)
        g = g.sort_values('_ord')
        # 보장: 모든 정류장 존재하도록 (누락은 이미 reindex로 채움)
        X = g[FEAT_COLS].values.astype('float32')    # (n_stops, feat_dim)
        Y = g[TARGET_COLS].values.astype('float32')  # (n_stops, 2)
        blocks[ts] = (X, Y)
    return blocks

train_blocks = build_hourly_blocks(df_train)
test_blocks  = build_hourly_blocks(df_test)

# ------------------------
# 4) 스케일러 (train에 fit → train/test에 transform)
#    feature와 target을 동일 스케일링(선호) 또는 분리 스케일링(정밀) 가능
# ------------------------
feat_scaler = MinMaxScaler()
tgt_scaler  = MinMaxScaler()

# train의 모든 시간 블록 concat 후 fit
train_feats_concat = np.concatenate([train_blocks[ts][0].reshape(-1, len(FEAT_COLS)) for ts in sorted(train_blocks)], axis=0)
train_tgts_concat  = np.concatenate([train_blocks[ts][1].reshape(-1, len(TARGET_COLS)) for ts in sorted(train_blocks)], axis=0)

feat_scaler.fit(train_feats_concat)
tgt_scaler.fit(train_tgts_concat)

def scale_blocks(blocks, feat_scaler, tgt_scaler):
    scaled = {}
    for ts, (X, Y) in blocks.items():
        Xs = feat_scaler.transform(X)  # (n_stops, feat_dim)
        Ys = tgt_scaler.transform(Y)   # (n_stops, 2)
        scaled[ts] = (Xs, Ys)
    return scaled

train_blocks_s = scale_blocks(train_blocks, feat_scaler, tgt_scaler)
test_blocks_s  = scale_blocks(test_blocks,  feat_scaler, tgt_scaler)

# ------------------------
# 5) 시퀀스 생성 (SEQ_LEN_HOURS 시간 창)
#    LSTM time-steps = SEQ_LEN_HOURS * n_stops
#    각 time-step은 "정류장 순서대로 이어붙인 1개 정류장"의 feature 벡터
#    타겟 = 다음 1시간의 모든 정류장 목표 (n_stops × 2) → 평탄화하여 벡터화
# ------------------------
def make_sequences(blocks_s, seq_len_hours):
    times = sorted(blocks_s.keys())
    X_list, y_list, ts_anchor = [], [], []
    for i in range(len(times) - seq_len_hours):
        past_times = times[i:i+seq_len_hours]
        next_time  = times[i+seq_len_hours]

        # 입력: (seq_len_hours, n_stops, feat_dim) → (seq_len_hours*n_stops, feat_dim)
        past_mats = [blocks_s[t][0] for t in past_times]
        X_mat = np.vstack(past_mats)  # (seq_len_hours*n_stops, feat_dim)

        # 타겟: 다음 1시간의 모든 정류장 (n_stops, 2) → 평탄화
        y_mat = blocks_s[next_time][1].reshape(-1)  # (n_stops*2,)

        X_list.append(X_mat)
        y_list.append(y_mat)
        ts_anchor.append(next_time)  # 이 샘플의 예측 기준 timestamp

    X = np.stack(X_list, axis=0)  # (samples, seq_len_hours*n_stops, feat_dim)
    y = np.stack(y_list, axis=0)  # (samples, n_stops*2)
    return X.astype('float32'), y.astype('float32'), ts_anchor

X_train, y_train, train_ts = make_sequences(train_blocks_s, SEQ_LEN_HOURS)
X_test,  y_test,  test_ts  = make_sequences(test_blocks_s,  SEQ_LEN_HOURS)

print("X_train:", X_train.shape, "y_train:", y_train.shape)
print("X_test :", X_test.shape,  "y_test :", y_test.shape)

# ------------------------
# 6) 모델 정의/학습
# ------------------------
tf.keras.backend.clear_session()
model = tf.keras.Sequential([
    tf.keras.layers.Input(shape=(X_train.shape[1], X_train.shape[2])),
    tf.keras.layers.LSTM(128),
    tf.keras.layers.Dense(64, activation='relu'),
    tf.keras.layers.Dense(y_train.shape[1])  # n_stops*2
])

model.compile(optimizer='adam', loss='mse')
history = model.fit(
    X_train, y_train,
    validation_split=0.1,
    epochs=40,
    batch_size=32,
    verbose=1
)

# ------------------------
# 7) 예측 (6/22~6/29 구간)
#    예측 결과는 스케일 역변환 후, 정류장/시간별로 복원
# ------------------------
y_pred_s = model.predict(X_test)
# 역변환: scaler는 (n_samples*n_stops) x 2 형태 기대하므로 reshape해서 inverse_transform
y_pred = []
for i in range(y_pred_s.shape[0]):
    y_one = y_pred_s[i].reshape(n_stops, 2)
    y_one_inv = tgt_scaler.inverse_transform(y_one)
    y_pred.append(y_one_inv)
y_pred = np.stack(y_pred, axis=0)  # (samples, n_stops, 2)

# ------------------------
# 8) 결과 DataFrame으로 복원/저장
# ------------------------
pred_rows = []
# test_ts[k] = 예측 기준 timestamp (다음 1시간)
# 각 샘플마다 모든 정류장 행 생성
for k, ts in enumerate(test_ts):
    date_k = pd.to_datetime(ts).date()
    hour_k = pd.to_datetime(ts).hour
    for j, stop in enumerate(stop_ids):
        승, 하 = y_pred[k, j, 0], y_pred[k, j, 1]
        row = {
            '기준_날짜': date_k,
            '시간': hour_k,
            '정류장_ID': stop,
            '정류장_순서': int(stops.loc[stops['정류장_ID']==stop, '정류장_순서'].iloc[0]) if (stops['정류장_ID']==stop).any() else np.nan,
            '예측_승차인원': float(승),
            '예측_하차인원': float(하)
        }
        pred_rows.append(row)

pred_df = pd.DataFrame(pred_rows).sort_values(['기준_날짜','시간','정류장_순서'])

# 역명 붙이기
pred_df = pred_df.merge(stops[['정류장_ID','역명']], on='정류장_ID', how='left')

# ------------------------
# 9) 테스트 구간의 실제 운행횟수 붙이기 (추가 배차 계산용)
# ------------------------
panel_test = df_panel[df_panel['timestamp'].isin(test_ts)].copy()
panel_test_small = panel_test[['timestamp','정류장_ID','운행횟수']].copy()
panel_test_small['기준_날짜'] = panel_test_small['timestamp'].dt.date
panel_test_small['시간'] = panel_test_small['timestamp'].dt.hour
panel_test_small = panel_test_small.drop(columns=['timestamp'])

pred_df = pred_df.merge(panel_test_small, on=['기준_날짜','시간','정류장_ID'], how='left')
pred_df['운행횟수'] = pred_df['운행횟수'].fillna(0.0)

# ------------------------
# 10) 혼잡도/추가 배차 계산 (정류장 순서대로 누적 추적)
#     - 버스 한 대 좌석수 55, 보통 상한 1.5배(82)
# ------------------------
SEAT = 33
NORMAL_MAX = int(SEAT * 1.5)  # 82

def compute_congestion_actions(group):
    # group: 동일 (기준_날짜, 시간) 묶음
    onboard = 0.0  # 버스 1대당 누적 탑승 예측 인원
    rows = []
    for _, r in group.sort_values('정류장_순서').iterrows():
        buses = max(float(r['운행횟수']), 1.0)  # 0 방지; 0이면 1대로 간주해 per-bus 계산
        board_per_bus = float(r['예측_승차인원']) / buses
        alight_per_bus = float(r['예측_하차인원']) / buses
        onboard = max(0.0, onboard + board_per_bus - alight_per_bus)

        # 현재 혼잡도
        if onboard <= SEAT:
            level = '여유'
        elif onboard <= NORMAL_MAX:
            level = '보통'
        else:
            level = '혼잡'

        # 혼잡 해소 위해 필요한 최소 총 버스 수 (per-bus 탑승 <= NORMAL_MAX)
        required_buses = int(np.ceil(max(onboard, 0.0) / NORMAL_MAX)) if NORMAL_MAX > 0 else 0
        extra_buses = max(0, required_buses - int(buses))

        row = r.to_dict()
        row.update({
            '버스당_탑승예측': onboard,
            '혼잡도': level,
            '필요_총버스': required_buses,
            '추가_배차': extra_buses
        })
        rows.append(row)
    return pd.DataFrame(rows)

actions = (
    pred_df.groupby(['기준_날짜','시간'], group_keys=False)
           .apply(compute_congestion_actions)
)

# ------------------------
# 11) 결과 저장
# ------------------------
pred_df.to_csv(OUT_PATH, index=False, encoding='utf-8-sig')

out2 = OUT_PATH.replace('.csv', '_혼잡도+추가배차.csv')
actions.to_csv(out2, index=False, encoding='utf-8-sig')

print("✅ 예측 저장:", OUT_PATH)
print("✅ 혼잡/배차 저장:", out2)

# ------------------------
# 12) 간단 성능 평가 (MAE, RMSE)
# ------------------------
# 테스트 구간 실제값 준비 (df_panel 기준)
gt_rows = []
for ts in test_ts:
    g = df_panel[df_panel['timestamp'] == ts].copy()
    g = g.merge(stops[['정류장_ID','정류장_순서']], on='정류장_ID', how='left')
    g = g.sort_values('정류장_순서')
    gt_rows.append(g[['승차인원','하차인원']].values)

gt = np.stack(gt_rows, axis=0)  # (samples, n_stops, 2)

mae = np.mean(np.abs(gt - y_pred))
rmse = np.sqrt(np.mean((gt - y_pred)**2))
print(f"Test MAE: {mae:.4f}  RMSE: {rmse:.4f}")