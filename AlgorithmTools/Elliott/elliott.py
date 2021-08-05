from AlgorithmTools.Elliott.utility import *
from AlgorithmTools.Elliott.mw_utils import *
from AlgorithmTools.Elliott.polywave import PolyWave
from AlgorithmTools.Elliott.monowave import MonoWave
from AlgorithmTools.Elliott.node import Node


def calculate(df, price_type='mean', step=8, iteration_cnt=1, removes_enabled=False, process_monowave=False,
              timeframe="mon1", offset=0, neo_wo_merge=False):
    df_nodes, mark = Node().build_node(df, offset=offset, price=price_type, step=step, timeframe=timeframe)
    monowaves1 = MonoWave(df_nodes)
    if neo_wo_merge and price_type == 'neo':
        monowaves1.buildMonoWaveFromNEO(mark, 'Price')  # Glenn Nilly (Neo without merging)
    else:
        monowaves1.buildMonoWave('Price')  # with merging)

    polywave_list = []
    hyper_monowaves_list = []

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

        pairs = monowaves1.pattern_isolation(hyper_monowaves)

        polywaves1 = PolyWave(hyper_monowaves)
        polywaves1.build_polywave(pairs)
        polywaves1.candidate_patterns()
        valid_pairs = polywaves1.analyzing_rules()
        start_candle_idx, end_candle_idx, start_price, end_price, ew_type = polywaves1.visualize_valid_polywave()
        polywave_list.append({"Start_index": start_candle_idx, "Start_price": start_price, "End_index": end_candle_idx, "End_price": end_price, "Type": ew_type})

        hyper_monowaves_list.append(pd.DataFrame(hyper_monowaves))
        hyper_monowaves = compaction(hyper_monowaves, valid_pairs)
        print(f"{j} finished")

    return hyper_monowaves_list, polywave_list