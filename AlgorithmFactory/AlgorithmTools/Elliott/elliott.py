from AlgorithmFactory.AlgorithmTools.Elliott.utility import *
from AlgorithmFactory.AlgorithmTools.Elliott.mw_utils import *
from AlgorithmFactory.AlgorithmTools.Elliott.polywave import PolyWave
from AlgorithmFactory.AlgorithmTools.Elliott.monowave import MonoWave
from AlgorithmFactory.AlgorithmTools.Elliott.node import Node
from AlgorithmFactory.AlgorithmTools.Elliott.recurrent_autoencoder import LSTM_AE

import torch
import torch.nn as nn

all_labels = {'x.c3': 0, '[:L5]': 1, ':5': 2, ':c3': 3, '(:F3)': 4, ':s5': 5, '(:5)': 6, '(:sL3)': 7, 'x.c3?': 8,
              ':?H:?': 9, '(:L3)': 10, ':L5': 11, '(:L5)': 12, ':F3': 13, '[:F3]': 14, '(:s5)': 15, '[:c3]': 16,
              ':L3': 17, ':sL3': 18, ':F3?': 19, '(:c3)': 20}
all_labels_rev = {0: 'x.c3', 1: '[:L5]', 2: ':5', 3: ':c3', 4: '(:F3)', 5: ':s5', 6: '(:5)', 7: '(:sL3)', 8: 'x.c3?',
                  9: ':?H:?', 10: '(:L3)', 11: ':L5', 12: '(:L5)', 13: ':F3', 14: '[:F3]', 15: '(:s5)', 16: '[:c3]',
                  17: ':L3', 18: ':sL3', 19: ':F3?', 20: '(:c3)'}
MODEL_PATH = './AlgorithmFactory/AlgorithmTools/Elliott/model.pth'
seq_len = 8
n_features = len(all_labels)


def label_to_net(labels_list) -> np.array:
    labels_onehot = np.zeros((8, len(all_labels)), dtype='float32')

    for i in range(seq_len):
        labels = labels_list[i]
        for j in range(len(labels)):
            labels_onehot[i][all_labels[labels[j]]] = 1.0

    return labels_onehot


def net_to_label(labels_onehot) -> np.array:
    labels_list = []

    for i in range(seq_len):
        temp = []
        for j in range(len(all_labels)):
            if labels_onehot[i][j] != 0:
                temp.append(all_labels_rev[j])
        labels_list.append(temp)
    return labels_list


def predict(model, data):
    with torch.no_grad():
        seq_pred = model(data)
        pred = seq_pred.cpu().numpy()

    return pred


def calculate(df, wave4_enable, wave5_enable, inside_flat_zigzag_wc, post_prediction_enable, price_type='mean', step=8,
              iteration_cnt=1, removes_enabled=False, process_monowave=False,
              candle_timeframe="mon1", offset=0, neo_wo_merge=False, neo_timeframe=None):
    # df_nodes, mark = Node().build_node(df, offset=offset, price=price_type, step=step, timeframe=timeframe)
    df_nodes, mark = Node().build_node(df, offset=offset, price=price_type, step=step,
                                       candle_timeframe=candle_timeframe, neo_timeframe=neo_timeframe)
    monowaves1 = MonoWave(df_nodes)
    if neo_wo_merge and price_type == 'neo':
        monowaves1.buildMonoWaveFromNEO(mark, 'Price')  # Glenn Nilly (Neo without merging)
    else:
        monowaves1.buildMonoWave('Price')  # with merging)

    polywave_list = []
    hyper_monowaves_list = []
    post_prediction_list = []
    In_impulse_prediction_list_w4 = []
    In_impulse_prediction_list_w5 = []
    In_zigzag_flat_prediction_list = []

    if process_monowave:
        m1 = monowaves1.monowaves.iloc[0]
        hyper_monowaves = monowaves1.build_hyper_monowaves(m1)

    hyper_monowaves = df2list(monowaves1.monowaves)
    for j in range(iteration_cnt):
        monowaves1.EW_rules(hyper_monowaves)
        for i in range(len(hyper_monowaves)):
            M1 = hyper_monowaves[i]
            if M1.Num_retracement_rule == 1:
                if M1.Num_condition == 'a':
                    monowaves1.EW_R1a(hyper_monowaves, i)
                if M1.Num_condition == 'b':
                    monowaves1.EW_R1b(hyper_monowaves, i)
                if M1.Num_condition == 'c':
                    monowaves1.EW_R1c(hyper_monowaves, i)
                if M1.Num_condition == 'd':
                    monowaves1.EW_R1d(hyper_monowaves, i)

            if M1.Num_retracement_rule == 2:
                if M1.Num_condition == 'a':
                    monowaves1.EW_R2a(hyper_monowaves, i)
                if M1.Num_condition == 'b':
                    monowaves1.EW_R2b(hyper_monowaves, i)
                if M1.Num_condition == 'c':
                    monowaves1.EW_R2c(hyper_monowaves, i)
                if M1.Num_condition == 'd':
                    monowaves1.EW_R2d(hyper_monowaves, i)
                if M1.Num_condition == 'e':
                    monowaves1.EW_R2e(hyper_monowaves, i)

            if M1.Num_retracement_rule == 3:
                if M1.Num_condition == 'a':
                    monowaves1.EW_R3a(hyper_monowaves, i)
                if M1.Num_condition == 'b':
                    monowaves1.EW_R3b(hyper_monowaves, i)
                if M1.Num_condition == 'c':
                    monowaves1.EW_R3c(hyper_monowaves, i)
                if M1.Num_condition == 'd':
                    monowaves1.EW_R3d(hyper_monowaves, i)
                if M1.Num_condition == 'e':
                    monowaves1.EW_R3e(hyper_monowaves, i)
                if M1.Num_condition == 'f':
                    monowaves1.EW_R3f(hyper_monowaves, i)

            if M1.Num_retracement_rule == 4:
                if M1.Num_condition == 'a':
                    monowaves1.EW_R4a(hyper_monowaves, i)
                if M1.Num_condition == 'b':
                    monowaves1.EW_R4b(hyper_monowaves, i)
                if M1.Num_condition == 'c':
                    monowaves1.EW_R4c(hyper_monowaves, i)
                if M1.Num_condition == 'd':
                    monowaves1.EW_R4d(hyper_monowaves, i)
                if M1.Num_condition == 'e':
                    monowaves1.EW_R4e(hyper_monowaves, i)

            if M1.Num_retracement_rule == 5:
                if M1.Num_condition == 'a':
                    monowaves1.EW_R5a(hyper_monowaves, i)
                if M1.Num_condition == 'b':
                    monowaves1.EW_R5b(hyper_monowaves, i)
                if M1.Num_condition == 'c':
                    monowaves1.EW_R5c(hyper_monowaves, i)
                if M1.Num_condition == 'd':
                    monowaves1.EW_R5d(hyper_monowaves, i)

            if M1.Num_retracement_rule == 6:
                if M1.Num_condition == 'a':
                    monowaves1.EW_R6a(hyper_monowaves, i)
                if M1.Num_condition == 'b':
                    monowaves1.EW_R6b(hyper_monowaves, i)
                if M1.Num_condition == 'c':
                    monowaves1.EW_R6c(hyper_monowaves, i)
                if M1.Num_condition == 'd':
                    monowaves1.EW_R6d(hyper_monowaves, i)

            if M1.Num_retracement_rule == 7:
                if M1.Num_condition == 'a':
                    monowaves1.EW_R7a(hyper_monowaves, i)
                if M1.Num_condition == 'b':
                    monowaves1.EW_R7b(hyper_monowaves, i)
                if M1.Num_condition == 'c':
                    monowaves1.EW_R7c(hyper_monowaves, i)
                if M1.Num_condition == 'd':
                    monowaves1.EW_R7d(hyper_monowaves, i)

        if removes_enabled:
            for i in range(len(hyper_monowaves)):
                monowaves1.rem_f3(hyper_monowaves, i)
                monowaves1.rem_c3(hyper_monowaves, i)
                monowaves1.rem_x_c3(hyper_monowaves, i)
                monowaves1.rem_sL3(hyper_monowaves, i)
                monowaves1.rem_L3(hyper_monowaves, i)
                monowaves1.rem_5(hyper_monowaves, i)
                monowaves1.rem_s5(hyper_monowaves, i)
                monowaves1.rem_L5(hyper_monowaves, i)

        # Labeling with Machine Learning Models
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        model = LSTM_AE(seq_len, n_features, [128, 32])
        model = model.to(device)

        if device == 'cpu':
            model.load_state_dict(torch.load(MODEL_PATH, map_location=torch.device('cpu')))
        else:
            model.load_state_dict(torch.load(MODEL_PATH))
        model.eval()

        for i in range(seq_len, len(hyper_monowaves)):
            if len(hyper_monowaves[i].Structure_list_label) == 0:
                labels_list = [hyper_monowaves[j].Structure_list_label for j in range(i - seq_len, i)]
                labels_onehot = label_to_net(labels_list)
                labels_onehot = np.expand_dims(labels_onehot, axis=0)
                x = torch.from_numpy(labels_onehot).to(device)
                pred = predict(model, x)
                pred = (pred > 0.2).astype(float)
                pred = pred.squeeze()
                labels_list = net_to_label(pred)
                hyper_monowaves[i].EW_structure = ['AI']
                hyper_monowaves[i].Structure_list_label = labels_list[-1]

        pairs = monowaves1.pattern_isolation(hyper_monowaves)

        polywaves1 = PolyWave(hyper_monowaves)
        polywaves1.build_polywave(pairs)
        polywaves1.candidate_patterns()
        valid_pairs = polywaves1.analyzing_rules()

        start_candle_idx, end_candle_idx, start_price, end_price, ew_type, pred_x1, pred_x2, pred_y1, pred_y2, pred_y3, directions = polywaves1.visualize_valid_polywave()
        polywave_list.append({"Start_index": start_candle_idx, "Start_price": start_price, "End_index": end_candle_idx,
                              "End_price": end_price, "Type": ew_type})
        if post_prediction_enable:
            post_prediction_list.append({"X1": pred_x1, "X2": pred_x2, "Y1": pred_y1, "Y2": pred_y2, "Y3": pred_y3 , "Dr": directions})

        hyper_monowaves_list.append(pd.DataFrame(hyper_monowaves))
        # hyper_monowaves = compaction(hyper_monowaves, valid_pairs)

        k = 0
        if wave4_enable:
            # index1, pred_x1, pred_x2, pred_y1, pred_y2, pred_y3, pred_y4 = monowaves1.Impulse_In_prediction_zone_label_M4(hyper_monowaves , step)
            # In_impulse_prediction_list_w4.append({"idx":index1 , "X1": pred_x1, "X2": pred_x2,"Y1":pred_y1, "Y2":pred_y2 , "Y3":pred_y3, "Y4":pred_y4})
            index1, pred_x1, pred_x2, preds, directions = monowaves1.Impulse_In_prediction_zone_label_M4(hyper_monowaves, step)
            In_impulse_prediction_list_w4.append({"idx": index1, "X1": pred_x1, "X2": pred_x2, "Y1": preds, "Dr": directions})

        if wave5_enable:
            index1, pred_x1, pred_x2, preds, directions = monowaves1.Impulse_In_prediction_zone_label_M5(hyper_monowaves, step)
            In_impulse_prediction_list_w5.append({"idx": index1, "X1": pred_x1, "X2": pred_x2, "Y1": preds, "Dr": directions})

        if inside_flat_zigzag_wc:
            index1, pred_xb, pred_yb, pred_xc, pred1_yc, pred2_yc, pred3_yc = monowaves1.Zigzag_prediction_zone_label_Mc(
                hyper_monowaves)
            # inter_prediction_list.append({"X1": pred_xb, "X2": pred_xc, "Y1": pred1_yc, "Y2": pred2_yc, "Y3": pred3_yc})
            index1_flat, pred_xb_flat, pred_yb_flat, pred_xc_flat, pred1_yc_flat, pred2_yc_flat, pred3_yc_flat = monowaves1.Flat_prediction_zone_label_Mc(
                hyper_monowaves)
            pred_xb.extend(pred_xb_flat)
            pred_xc.extend(pred_xc_flat)
            pred1_yc.extend(pred1_yc_flat)
            pred2_yc.extend(pred2_yc_flat)
            pred3_yc.extend(pred3_yc_flat)
            In_zigzag_flat_prediction_list.append(
                {"X1": pred_xb, "X2": pred_xc, "Y1": pred1_yc, "Y2": pred2_yc, "Y3": pred3_yc})

    return hyper_monowaves_list, polywave_list, post_prediction_list, In_impulse_prediction_list_w4, In_impulse_prediction_list_w5, In_zigzag_flat_prediction_list


def next_time(cur_time, time_frame, step):
    if time_frame == "mon1":
        return cur_time + pd.Timedelta(days=cur_time.daysinmonth * step)
    if time_frame == "d1":
        return cur_time + pd.Timedelta(days=1 * step)
    if time_frame == "W1":
        return cur_time + pd.Timedelta(weeks=1 * step)
    if time_frame == "H12":
        return cur_time + pd.Timedelta(hours=12 * step)
    if time_frame == "H4":
        return cur_time + pd.Timedelta(hours=4 * step)
    if time_frame == "H1":
        return cur_time + pd.Timedelta(hours=1 * step)
    if time_frame == "M30":
        return cur_time + pd.Timedelta(minutes=30 * step)
    if time_frame == "M15":
        return cur_time + pd.Timedelta(minutes=15 * step)
    if time_frame == "M5":
        return cur_time + pd.Timedelta(minutes=5 * step)
    if time_frame == "M1":
        return cur_time + pd.Timedelta(minutes=1 * step)