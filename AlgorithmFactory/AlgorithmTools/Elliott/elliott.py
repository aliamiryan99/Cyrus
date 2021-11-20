
from AlgorithmFactory.AlgorithmTools.Elliott.utility import *
from AlgorithmFactory.AlgorithmTools.Elliott.mw_utils import *
from AlgorithmFactory.AlgorithmTools.Elliott.polywave import PolyWave
from AlgorithmFactory.AlgorithmTools.Elliott.monowave import MonoWave
from AlgorithmFactory.AlgorithmTools.Elliott.node import Node

## ML imports
from AlgorithmFactory.AlgorithmTools.Elliott.recurrent_autoencoder import LSTM_AE
from AlgorithmFactory.AlgorithmTools.Elliott.ml_utils import *

import torch
import torch.nn as nn

# ML model config
seq_len = 8
n_features = len(all_labels)
MODEL_PATH = './model.pth'

def calculate(df, wave4_enable, wave5_enable, inside_flat_zigzag_wc, post_prediction_enable, price_type='mean', step=8, iteration_cnt=1, removes_enabled=False, process_monowave=False,
              candle_timeframe="mon1", offset=0, neo_wo_merge=False, neo_timeframe=None):
    # df_nodes, mark = Node().build_node(df, offset=offset, price=price_type, step=step, timeframe=timeframe)
    df_nodes, mark = Node().build_node(df, offset=offset, price=price_type, step=step, candle_timeframe=candle_timeframe, neo_timeframe=neo_timeframe)
    monowaves1 = MonoWave(df_nodes)
    if neo_wo_merge and price_type == 'neo':
        monowaves1.buildMonoWaveFromNEO(mark, 'Price')  # Glenn Nilly (Neo without merging)
    else:
        monowaves1.buildMonoWave('Price')  # with merging)

    polywave_list = []
    hyper_monowaves_list = []
    post_prediction_list = []
    In_impulse_prediction_list_w4=[]
    In_impulse_prediction_list_w5=[]
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
            model.load_state_dict(torch.load(MODEL_PATH, map_location = torch.device('cpu')))
        else:
            model.load_state_dict(torch.load(MODEL_PATH))
        model.eval()

        for i in range(seq_len, len(hyper_monowaves)):
            if len(hyper_monowaves[i].Structure_list_label) == 0:
                labels_list = [hyper_monowaves[j].Structure_list_label for j in range(i-seq_len, i)]
                labels_onehot = label_to_net(labels_list, seq_len)
                labels_onehot = np.expand_dims(labels_onehot, axis=0)
                x = torch.from_numpy(labels_onehot).to(device)
                pred = predict(model, x)
                pred = (pred > 0.2).astype(float)
                pred = pred.squeeze()
                labels_list = net_to_label(pred, seq_len)
                hyper_monowaves[i].EW_structure = ['AI']
                hyper_monowaves[i].Structure_list_label = labels_list[-1]

        
        pairs = monowaves1.pattern_isolation(hyper_monowaves)

        polywaves1 = PolyWave(hyper_monowaves)
        polywaves1.build_polywave(pairs)
        polywaves1.candidate_patterns()
        valid_pairs = polywaves1.analyzing_rules()
        
        start_candle_idx, end_candle_idx, start_price, end_price, ew_type, pred_x1, pred_x2, pred_y1, pred_y2, pred_y3 = polywaves1.visualize_valid_polywave()
        polywave_list.append({"Start_index": start_candle_idx, "Start_price": start_price, "End_index": end_candle_idx, "End_price": end_price, "Type": ew_type})
        if post_prediction_enable:
            post_prediction_list.append({"X1": pred_x1, "X2": pred_x2, "Y1": pred_y1, "Y2": pred_y2, "Y3": pred_y3})

        hyper_monowaves_list.append(pd.DataFrame(hyper_monowaves))
        # hyper_monowaves = compaction(hyper_monowaves, valid_pairs)
        print(f"{j} finished")

        k = 0
        if wave4_enable:
            index1, pred_x1, pred_x2, pred_y1, pred_y2, pred_y3, pred_y4 = monowaves1.Impulse_In_prediction_zone_label_M4(hyper_monowaves , step)
            In_impulse_prediction_list_w4.append({"idx":index1 , "X1": pred_x1, "X2": pred_x2,"Y1":pred_y1, "Y2":pred_y2 , "Y3":pred_y3, "Y4":pred_y4})

        if wave5_enable:
            index1, pred_x1, pred_x2, pred_y1 = monowaves1.Impulse_In_prediction_zone_label_M5_truncated(hyper_monowaves , step)
            In_impulse_prediction_list_w5.append({"idx":index1 , "X1": pred_x1, "X2": pred_x2,"Y1":pred_y1})
        
        if inside_flat_zigzag_wc:
            index1, pred_xb, pred_yb, pred_xc, pred1_yc, pred2_yc, pred3_yc = monowaves1.Zigzag_prediction_zone_label_Mc(hyper_monowaves)
        # inter_prediction_list.append({"X1": pred_xb, "X2": pred_xc, "Y1": pred1_yc, "Y2": pred2_yc, "Y3": pred3_yc})
            index1_flat, pred_xb_flat, pred_yb_flat, pred_xc_flat, pred1_yc_flat, pred2_yc_flat, pred3_yc_flat = monowaves1.Flat_prediction_zone_label_Mc(hyper_monowaves)
            pred_xb.extend(pred_xb_flat)
            pred_xc.extend(pred_xc_flat) 
            pred1_yc.extend(pred1_yc_flat)
            pred2_yc.extend(pred2_yc_flat)
            pred3_yc.extend(pred3_yc_flat)
            In_zigzag_flat_prediction_list.append({"X1": pred_xb, "X2": pred_xc, "Y1": pred1_yc, "Y2": pred2_yc, "Y3": pred3_yc})



    return hyper_monowaves_list, polywave_list, post_prediction_list, In_impulse_prediction_list_w4, In_impulse_prediction_list_w5, In_zigzag_flat_prediction_list