from torch.cuda import random
from AlgorithmFactory.AlgorithmTools.Elliott.utility import *
from AlgorithmFactory.AlgorithmTools.Elliott.mw_utils import *
from AlgorithmFactory.AlgorithmTools.Elliott.polywave import PolyWave
from AlgorithmFactory.AlgorithmTools.Elliott.monowave import MonoWave
from AlgorithmFactory.AlgorithmTools.Elliott.node import Node
from AlgorithmFactory.AlgorithmTools.Elliott.recurrent_autoencoder import LSTM_AE, LSTM_AE_v2
from AlgorithmFactory.AlgorithmTools.Elliott.ml_utils import *

from random import random
import torch
import torch.nn as nn

import warnings
import glob
ROOT_MODEL_PATH = './AlgorithmFactory/AlgorithmTools/Elliott/models'
MODEL_PATH = f'{ROOT_MODEL_PATH}/model.pth'
all_labels = {'x.c3': 0, '[:L5]': 1, ':5': 2, ':c3': 3, '(:F3)': 4, ':s5': 5, '(:5)': 6, '(:sL3)': 7, 'x.c3?': 8,
              ':?H:?': 9, '(:L3)': 10, ':L5': 11, '(:L5)': 12, ':F3': 13, '[:F3]': 14, '(:s5)': 15, '[:c3]': 16,
              ':L3': 17, ':sL3': 18, ':F3?': 19, '(:c3)': 20}
all_labels_rev = {0: 'x.c3', 1: '[:L5]', 2: ':5', 3: ':c3', 4: '(:F3)', 5: ':s5', 6: '(:5)', 7: '(:sL3)', 8: 'x.c3?',
                  9: ':?H:?', 10: '(:L3)', 11: ':L5', 12: '(:L5)', 13: ':F3', 14: '[:F3]', 15: '(:s5)', 16: '[:c3]',
                  17: ':L3', 18: ':sL3', 19: ':F3?', 20: '(:c3)'}


# all_labels = {'x.c3':0, '[:L5]':1, ':5':2, ':c3':3, '(:F3)':4, ':s5':5, '(:5)':2, '(:sL3)':6, 'x.c3?':0, ':?H:?':7, '(:L3)':8, ':L5':1, '(:L5)':1, ':F3':4, '[:F3]':4, '(:s5)':5, '[:c3]':3, ':L3':8, ':sL3':6, ':F3?':4, '(:c3)': 3}
labels_merged = dict([(idx, l) for idx, l in enumerate(['x.c3', ':L5', ':5', ':c3', ':F3', ':s5', ':sL3', ':?H:?', ':L3'])])

seq_len = 7
n_features = len(all_labels)
# n_features = len(labels_merged)



def calculate(df, wave4_enable, wave5_enable, zigzag_wc_enable, flat_wc_enable, post_prediction_enable, price_type='mean', step=8,
              iteration_cnt=1, removes_enabled=False, process_monowave=False, triangle_enabled=False,
              candle_timeframe="mon1", offset=0, neo_wo_merge=False, neo_timeframe=None, single_level_merging_enabled=True, triangle_order_offset=0):
    # df_nodes, mark = Node().build_node(df, offset=offset, price=price_type, step=step, timeframe=timeframe)
    df_nodes, mark = Node().build_node(df, offset=offset, price=price_type, step=step,
                                       candle_timeframe=candle_timeframe, neo_timeframe=neo_timeframe)
    monowaves1 = MonoWave(df_nodes)
    if neo_wo_merge and price_type == 'neo':
        monowaves1.buildMonoWaveFromNEO(mark, 'Price')  # Glenn Nilly (Neo without merging)
    else:
        monowaves1.buildMonoWave('Price')  # with merging)

    polywave_list = []
    triangles = []
    hyper_monowaves_list = []
    post_prediction_list = []
    In_impulse_prediction_list_w4 = []
    In_impulse_prediction_list_w5 = []
    In_zigzag_prediction_list = []
    In_flat_prediction_list = []
    triangle_df = pd.DataFrame()

    if process_monowave:
        m1 = monowaves1.monowaves.iloc[0]
        hyper_monowaves = monowaves1.build_hyper_monowaves(m1)

    hyper_monowaves = df2list(monowaves1.monowaves)

    if single_level_merging_enabled:
        hyper_monowaves = pre_process_single_level_merging(df, hyper_monowaves)

    for j in range(iteration_cnt):
        monowaves1.EW_rules(hyper_monowaves)
        for i in range(len(hyper_monowaves)):
            region_ew_rules_handler(hyper_monowaves, monowaves1, i)
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
        model = LSTM_AE_v2(seq_len, n_features, [128, 64])
        model = model.to(device)
        global MODEL_PATH
        model_file = glob.glob(f"{ROOT_MODEL_PATH}/*_hmw_{candle_timeframe}_*")
        if len(model_file) > 0:
            # model = model_file[0]
            MODEL_PATH = f"{model_file[0]}"
        else:
            warnings.warn(f"No Model Available for {candle_timeframe} and {neo_timeframe}\nDefault model is loaded")

        model.load_state_dict(torch.load(MODEL_PATH, map_location=torch.device(device)))
        model.eval()

        for i in range(seq_len, len(hyper_monowaves)):
            if len(hyper_monowaves[i].Structure_list_label) == 0:
                labels_list = [hyper_monowaves[j].Structure_list_label for j in range(i - seq_len, i)]
                labels_onehot = label_to_net(labels_list, seq_len)
                labels_onehot = np.expand_dims(labels_onehot, axis=0)
                x = torch.from_numpy(labels_onehot).to(device)
                pred = predict(model, x).squeeze()
                pred_masked = (pred > 0.5).astype(float)
                if (sum(pred_masked[-1,:]) == 0):
                    pred_masked[-1,np.argmax(pred[-1,:])] = 1
                labels_list = net_to_label(pred_masked, seq_len)
                hyper_monowaves[i].EW_structure = ['AI']
                hyper_monowaves[i].Structure_list_label = labels_list[-1]

        # Similarity check for future legs prediction

        similarity_pred = {'names':[],'start_time':[],'start_price':[],'end_time':[],"end_price":[]}
        labels_list_curr = [hyper_monowaves[j].Structure_list_label for j in range(len(hyper_monowaves) - seq_len, len(hyper_monowaves))]
        for i in range(seq_len, len(hyper_monowaves) - seq_len):
            labels_list_past = [hyper_monowaves[j].Structure_list_label for j in range(i - seq_len, i)]
            
            if is_subset(labels_list_curr ,labels_list_past):
                names = [f'{i}_{seq_len}_{j}_{int(random() *1000)}_similarity_pred' for j in range(i,i+3)]
                # _price_coeff = hyper_monowaves[i].Start_price / hyper_monowaves[i].Price_range
                # start_price = [hyper_monowaves[i].Start_price + _p for _p in hyper_monowaves[i+1:i+4].Price_range]
                # start_time = [hyper_monowaves[i].Start_candle_index + _p for _p in hyper_monowaves[i+1:i+4].Start_candle_index]
                # end_price = [hyper_monowaves[i].End_price + _p for _p in hyper_monowaves[i+1:i+4].Price_range]
                # end_time = [hyper_monowaves[i].Start_candle_index + _p for _p in hyper_monowaves[i+1:i+4].Start_candle_index]

                start_price = [0]*3
                end_price = []
                
                end_price.append(hyper_monowaves[-1].Start_price -\
                    hyper_monowaves[i+1].Price_range / hyper_monowaves[i].Price_range * hyper_monowaves[-1].Price_range *\
                    hyper_monowaves[-1].Direction
                )
                end_price.append(end_price[-1] -\
                    hyper_monowaves[i+2].Price_range / hyper_monowaves[i].Price_range * hyper_monowaves[-1].Price_range *\
                    -hyper_monowaves[-1].Direction
                )

                end_price.append(end_price[-1] -\
                    hyper_monowaves[i+3].Price_range / hyper_monowaves[i].Price_range * hyper_monowaves[-1].Price_range *\
                    hyper_monowaves[-1].Direction
                )

                start_price[0] = hyper_monowaves[-1].End_price
                start_price[1:] = end_price[:-1]
                
                # end_price.append(hyper_monowaves[-1].End_price - hyper_monowaves[i+1].Price_range * (hyper_monowaves[-1].Direction))
                # end_price.append(
                #     end_price[-1] - hyper_monowaves[i+2].Price_range * (hyper_monowaves[-1].Direction*-1)
                # )
                # end_price.append(
                #     end_price[-1] - hyper_monowaves[i+3].Price_range * (hyper_monowaves[-1].Direction)
                # )
                
                # start_price[0] = hyper_monowaves[-1].End_price
                # start_price[1:] = end_price[:-1]
                
                # hyper_monowaves[i].End_candle_index - hyper_monowaves[i].Start_candle_index + hyper_monowaves[-1].Start_candle_index
                end_time = [
                    hyper_monowaves[i].End_candle_index - hyper_monowaves[i].Start_candle_index + hyper_monowaves[-1].End_candle_index
                ]
                end_time.append(
                    end_time[-1] + hyper_monowaves[i+1].End_candle_index - hyper_monowaves[i+1].Start_candle_index
                )
                end_time.append(
                    end_time[-1] + hyper_monowaves[i+2].End_candle_index - hyper_monowaves[i+2].Start_candle_index
                )

                start_time = [0] * 3
                start_time[0] = hyper_monowaves[-1].End_candle_index
                start_time[1:] = end_time[:-1]

                similarity_pred['names'].extend(names)
                similarity_pred['start_price'].extend(start_price)
                similarity_pred['end_price'].extend(end_price)
                similarity_pred['start_time'].extend(start_time)
                similarity_pred['end_time'].extend(end_time)

                if len(names) > 0:
                    break

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

        hyper_monowaves_list.append(pd.DataFrame(hyper_monowaves).reset_index().drop(columns=['index']))
        # hyper_monowaves = compaction(hyper_monowaves, valid_pairs)
        if triangle_enabled:
            # self.data[int(tri_obj['legs'][0].Start_candle_index)]['Time']
            # triangle_df = df_empty(columns=['Time', 'order'], dtypes=["datetime64[ns]", np.int32], index="Time")

            # triangle_df = pd.DataFrame(columns=['Time'], dtype='datetime64[ns]')
            # triangle_df['order'] = pd.DataFrame(columns=['order'], dtype=int)
            # triangle_df = triangle_df.set_index('Time')

            t_orders = []
            t_times  = []

            # triangle_order_offset
            for j in range(2, hyper_monowaves_list[0].shape[0] - 4):
                triangle_validation, tri_obj = merging_triangle_fibo_rel_rule(hyper_monowaves_list[0], df, j)
                # print("NEXT")
                # triangle_validation, tri_obj = triangle_fibo_rel_rule(hyper_monowaves_list[0], df, i)
                if triangle_validation:
                    triangle_idx = df.loc[int(tri_obj['legs'][0].Start_candle_index)]['Time']
                    # offset_idx = df.loc[int(tri_obj['legs'][0].Start_candle_index)-3]['Time']
                    triangle_order_offset += 1
                    t_orders.append(triangle_order_offset)
                    t_times.append(triangle_idx)

                    triangles.append((j, tri_obj))
                    # print(f"YESSSS\t\t{i}\t\t{tri_obj}")
                # triangle_df = pd.concat([triangle_df,
                #                          pd.DataFrame({'Time': t_times, 'order': t_orders}, dtype=int,).set_index("Time")],
                #                         ignore_index=False,)
                triangle_df = pd.DataFrame({'Time': t_times, 'order': t_orders}, dtype=int, )#.set_index("Time")

                triangle_df['Time'] = triangle_df['Time'].astype(dtype='datetime64[ns]')
                triangle_df = triangle_df.set_index("Time")
        k = 0
        if wave4_enable:
            # index1, pred_x1, pred_x2, pred_y1, pred_y2, pred_y3, pred_y4 = monowaves1.Impulse_In_prediction_zone_label_M4(hyper_monowaves , step)
            # In_impulse_prediction_list_w4.append({"idx":index1 , "X1": pred_x1, "X2": pred_x2,"Y1":pred_y1, "Y2":pred_y2 , "Y3":pred_y3, "Y4":pred_y4})
            index1, pred_x1, pred_x2, preds, directions = monowaves1.Impulse_In_prediction_zone_label_M4(hyper_monowaves, step)
            In_impulse_prediction_list_w4.append({"idx": index1, "X1": pred_x1, "X2": pred_x2, "Y1": preds, "Dr": directions})

        if wave5_enable:
            index1, pred_x1, pred_x2, preds, directions = monowaves1.Impulse_In_prediction_zone_label_M5(hyper_monowaves, step)
            In_impulse_prediction_list_w5.append({"idx": index1, "X1": pred_x1, "X2": pred_x2, "Y1": preds, "Dr": directions})

        if zigzag_wc_enable:
            index1, pred_xb, pred_yb, pred_xc, pred1_yc, pred2_yc, pred3_yc = monowaves1.Zigzag_prediction_zone_label_Mc(hyper_monowaves)
            # inter_prediction_list.append({"X1": pred_xb, "X2": pred_xc, "Y1": pred1_yc, "Y2": pred2_yc, "Y3": pred3_yc})
            In_zigzag_prediction_list.append({"X1": pred_xb, "X2": pred_xc, "Y1": pred1_yc, "Y2": pred2_yc, "Y3": pred3_yc})
        
        if flat_wc_enable:
            index1, pred_xb, pred_yb, pred_xc, pred1_yc, pred2_yc, pred3_yc = monowaves1.Flat_prediction_zone_label_Mc(hyper_monowaves)
            In_flat_prediction_list.append({"X1": pred_xb, "X2": pred_xc, "Y1": pred1_yc, "Y2": pred2_yc, "Y3": pred3_yc})

    return hyper_monowaves_list, triangles, triangle_df, polywave_list, post_prediction_list, In_impulse_prediction_list_w4, In_impulse_prediction_list_w5, In_zigzag_prediction_list, In_flat_prediction_list, similarity_pred


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




def merging_triangle_fibo_rel_rule(mwlist, data, index,):
    # cols = [
    #     'MW_start_index', 'MW_end_index', 'Start_candle_index',
    #     'End_candle_index', 'Start_price', 'End_price', 'Max_candle_index', 'Max_price', 'Min_candle_index',
    #     'Min_price', 'Duration',
    #     'Price_range', 'Price_coverage', 'Direction', 'Slop', 'Num_sub_monowave', 'Prev_wave_retracement_ratio',
    #     'Next_wave_retracement_ratio', 'Num_retracement_rule', 'Num_condition',
    #     # 'Wave_category', 'Structure_list_label', 'Candid_elliott_end', 'EW_structure'
    # ]  # Wave_category is only relevant/valid for Rule 4
    cols = [
        'MW_start_index', 'MW_end_index','Start_candle_index', 'End_candle_index',
        'Start_price', 'End_price', 'Duration', 'Price_range', 'Direction',
        'Max_candle_index', 'Max_price','Min_candle_index', 'Min_price',
    ]
    dtype = [np.int32, np.int32, np.int32, np.int32, np.float32, np.float32, np.int32, np.float32, np.int16,
             np.int32, np.float32, np.int32, np.float32,]
    leg_offset = 0
    _step = 1.0
    triangle_mwlist = df_empty(cols, dtype,)


    _start_index = 0    # it refers to the wave index in triangle_mwlist - (you can change its value)
    start_index = index     # it refers to the wave index in mwlist - (it should not be changed)
    while _start_index < 5:

        next_idx = leg_offset+start_index
        while triangle_mwlist.shape[0] < 8 and next_idx < mwlist.shape[0]:
            triangle_mwlist = triangle_mwlist.append(mwlist.iloc[[next_idx]][cols])
            leg_offset += 1
            next_idx = leg_offset+start_index

        try:
            __start_index = int(_start_index)
            _Ma = triangle_mwlist.iloc[[__start_index]]
            _Mb = triangle_mwlist.iloc[[__start_index+1]]
            _Mc = triangle_mwlist.iloc[[__start_index+2]]
        except Exception as ex:
            print(f"ex: {next_idx}  {mwlist.shape[0]}  {triangle_mwlist.shape[0]}",)
            break

        if balance_similarity(_Ma.iloc[0], _Mb.iloc[0],_Mc.iloc[0], small_middle=True):

            vals = {
                'MW_start_index': _Ma.iloc[0].MW_start_index, 'MW_end_index': _Mc.iloc[0].MW_end_index,
                'Start_candle_index': _Ma.iloc[0].Start_candle_index, 'End_candle_index': _Mc.iloc[0].End_candle_index,
                'Start_price': _Ma.iloc[0].Start_price, 'End_price': _Mc.iloc[0].End_price,
                'Duration': (_Mc.iloc[0].End_candle_index-_Ma.iloc[0].Start_candle_index),
                'Price_range': abs(_Mc.iloc[0].End_price-_Ma.iloc[0].Start_price)+0.001, 'Direction': _Ma.iloc[0].Direction,
                'Price_coverage': -1,'Max_candle_index': -1, 'Max_price': -1, 'Min_candle_index': -1, 'Min_price': -1,
            }

            M = pd.DataFrame.from_dict(data= {_Ma.index.values[0]: [vals[c] for c in cols]}, orient='index', columns=cols)
            M_index = _Ma.index.values[0]
            idxmax = data.loc[M.iloc[0].Start_candle_index:M.iloc[0].End_candle_index].High.idxmax()
            M.Max_price = data.loc[idxmax].High
            M.Max_candle_index = idxmax

            idxmin = data.loc[M.iloc[0].Start_candle_index:M.iloc[0].End_candle_index].Low.idxmin()
            M.Min_price = data.loc[idxmin].Low
            M.Min_candle_index = idxmin

            M.Price_coverage = M.Max_price - M.Min_price

            triangle_mwlist = triangle_mwlist.drop(index=triangle_mwlist.iloc[[__start_index+1,__start_index+2]].index.values)

            triangle_mwlist.iloc[__start_index, :] = M.iloc[0]
            _start_index += _step
            # print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
            # print(data[int(M.iloc[0].Start_candle_index):int(M.iloc[0].End_candle_index)].Time)
        else:
            _start_index = int(_start_index + 1)

    triangle_mwlist = triangle_mwlist.iloc[:5]
    return check_fibo_rel_rule(triangle_mwlist)


def check_fibo_rel_rule(mwlist):
    try:
        Ma, Mb, Mc, Md, Me = mwlist.iloc
    except Exception as ex:
        return False, None

    hmw_price_range = [Ma.Price_range, Mb.Price_range, Mc.Price_range, Md.Price_range, Me.Price_range]

    # if 0.382 * Ma.Price_range < Mb.Price_range < 2.618 * Ma.Price_range:
    if 0.33 * Ma.Price_range < Mb.Price_range < 2.618 * Ma.Price_range:
        cond_list_contracting = []
        # cond_list_expanding = []

        for i in range(4):
            # cond_list_contracting.append(hmw_price_range[i + 1] > 0.5 * hmw_price_range[i])
            cond_list_contracting.append(hmw_price_range[i]*1.15 > hmw_price_range[i + 1] > 0.5 * hmw_price_range[i])

            # cond_list_expanding.append(hmw_price_range[i + 1] < 0.5 * hmw_price_range[i])
        # if sum(cond_list_contracting) < 2:
        #     # print(f"in-out\t\t{sum(cond_list_contracting)}\t{len(cond_list_contracting)}")
        #     return False, None

        # if beyond_trendline(Mb, Md, Mc) or \
        #         beyond_trendline(Mb, Md, Me):  # TODO or beyond_trendline(Ma, Mc, Mb) or beyond_trendline(Ma, Mc, Md):
        #     self.polywaveList.loc[index, 'Validation'] = False
        #     return

        # widest_segment_price = max(hmw_price_range)
        # widest_segment_index = np.argmax(hmw_price_range)
        eps = [1/(1.15**i) for i in range(1,5)]
        if (
                (0.5 * hmw_price_range[0] <= hmw_price_range[2]) and  # a <= 2c | it is 0.618 fibo ratio, but relaxed
                (0.5 * hmw_price_range[2] <= hmw_price_range[4]) and  # c <= 2e | it is 0.618 ratio but relaxed
                sum(cond_list_contracting[:]) >= 3 and
                # (hmw_price_range[1] >= hmw_price_range[3] * 1.1) and  # `b` should be (almost (or absolutely)) larger than `d`
                # (hmw_price_range[0] >= hmw_price_range[2] >= hmw_price_range[4]) and  # a > c > e
                # (hmw_price_range[0] >= hmw_price_range[1] >= hmw_price_range[2])  # and # a > b > c
                (hmw_price_range[0] >= hmw_price_range[1] * eps[0] >= hmw_price_range[2] * eps[1]) and
                fib_ratio * hmw_price_range[1] >= hmw_price_range[3] and
                0.9*hmw_price_range[3] >= hmw_price_range[4]
                # (last_leg_price_range_check(mwlist.iloc[index:index+5]))
        ):
            # np.argmin(hmw_price_range) == 4:  # e-wave is smallest wave
            # self.polywaveList.loc[index, 'EW_structure'].append('Contracting')

            # apex_time_index, apex_price = apex(Ma, Mb, Mc, Md)
            # apex_time_index, apex_price = flex_apex(Ma, Mb, Mc, Md, Me)

            triangle_obj = {
                # 'apex': (round(apex_time_index) if apex_time_index else apex_time_index, apex_price,),
                'legs': (Ma, Mb, Mc, Md, Me),
                'tipe': 'horizontally'
            }
            return True, triangle_obj

    # The most common setup is for waves-a, c, & e to relate by 61.8% or 38.2% and the b & d-waves to relate by 61.8%.
    # return (
    #         (waves_are_fib_related(Mb.Price_range, Md.Price_range, fib_ratio) and
    #
    #         waves_are_fib_related(Ma.Price_range, Mc.Price_range, fib_ratio) and
    #         waves_are_fib_related(Mc.Price_range, Me.Price_range, 1 - fib_ratio) and
    #         waves_are_fib_related(Md.Price_range, Me.Price_range, fib_ratio))
    #
    #     , waves_are_fib_related(Mb.Price_range, Ma.Price_range, fib_ratio, True)
    # )

    # self.polywaveList.loc[index, 'FiboRelatedWaves'] = True

    # if waves_are_fib_related(Mb.Duration, Ma.Duration, fib_ratio, True):
    #     self.polywaveList.loc[index, 'Validation'] = False
    # print("out-out")
    return False, None


def pre_process_single_level_merging(df, hyper_monowaves):
    default_cols = {'MW_start_index': 0, 'MW_end_index': 0, 'Start_candle_index': 0,
                    'End_candle_index': 0, 'Start_price': 0, 'End_price': 0, 'Max_candle_index': 0,
                    'Max_price': 0,
                    'Min_candle_index': 0, 'Min_price': 0, 'Duration': 0,
                    'Price_range': 0, 'Price_coverage': 0, 'Direction': 0, 'Slop': 0, 'Num_sub_monowave': 1,
                    'Prev_wave_retracement_ratio': 0,
                    'Next_wave_retracement_ratio': 0, 'Num_retracement_rule': 0, 'Num_condition': '-',
                    'Wave_category': 0,
                    'Structure_list_label': [], 'Candid_elliott_end': False, 'EW_structure': []
                    }
    _count = 0
    hmw_length = len(hyper_monowaves)
    _step = 1.0003
    hmw_idx = 0
    _hmw_idx = 0.0
    while hmw_length > hmw_idx + 2:
        _m1 = hyper_monowaves[hmw_idx]
        _m2 = hyper_monowaves[hmw_idx + 1]
        _m3 = hyper_monowaves[hmw_idx + 2]
        if balance_similarity(_m1, _m2, _m3, small_middle=True, lesser=True):
            idxmax = df.loc[_m1.Start_candle_index:_m3.End_candle_index].High.idxmax()
            max_price = df.loc[idxmax].High
            max_candle_index = idxmax

            idxmin = df.loc[_m1.Start_candle_index:_m3.End_candle_index].Low.idxmin()
            min_price = df.loc[idxmin].Low
            min_candle_index = idxmin
            price_range = abs(_m3.End_price - _m1.Start_price) + 0.001
            duration = (_m3.End_candle_index - _m1.Start_candle_index)

            vals = {
                'MW_start_index': _m1.MW_start_index,
                'MW_end_index': _m3.MW_end_index,
                'Start_candle_index': _m1.Start_candle_index,
                'End_candle_index': _m3.End_candle_index,
                'Start_price': _m1.Start_price,
                'End_price': _m3.End_price,
                'Max_candle_index': max_candle_index,
                'Min_candle_index': min_candle_index,
                'Max_price': max_price,
                'Min_price': min_price,
                'Duration': duration,
                'Price_range': price_range,
                'Price_coverage': max_price - min_price,
                'Direction': _m1.Direction,
                'Slop': np.degrees(np.arctan(price_range / duration)),
                'Num_retracement_rule': 0,
            }
            default_vals = copy.deepcopy({**default_cols, **vals})

            hyper_monowaves[hmw_idx] = pd.Series(data=default_vals, )
            hyper_monowaves.pop(hmw_idx + 1)
            hyper_monowaves.pop(hmw_idx + 1)

            hmw_length = len(hyper_monowaves)
            _count += 1
            _hmw_idx += _step
        else:
            _hmw_idx = int(_hmw_idx + 1)
        hmw_idx = int(_hmw_idx)

    print(f"SHALGHAM -----------\t{_count}")
    return hyper_monowaves


def region_ew_rules_handler(hyper_monowaves, monowaves, idx):
    M1 = hyper_monowaves[idx]
    if M1.Num_condition == '-': return
    condition_hashing_index = M1.Num_retracement_rule*10 + ord(M1.Num_condition) - ord('a')
    _temp = get_ew_region_rules_list(monowaves, condition_hashing_index)

    _temp(hyper_monowaves, idx)
