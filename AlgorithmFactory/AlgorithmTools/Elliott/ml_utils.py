import torch
import numpy as np

all_labels = {'x.c3':0, '[:L5]':1, ':5':2, ':c3':3, '(:F3)':4, ':s5':5, '(:5)':6, '(:sL3)':7, 'x.c3?':8, ':?H:?':9, '(:L3)':10, ':L5':11, '(:L5)':12, ':F3':13, '[:F3]':14, '(:s5)':15, '[:c3]':16, ':L3':17, ':sL3':18, ':F3?':19, '(:c3)': 20}
all_labels_rev = {0:'x.c3', 1:'[:L5]', 2:':5', 3:':c3', 4:'(:F3)', 5:':s5', 6:'(:5)', 7:'(:sL3)', 8:'x.c3?', 9:':?H:?', 10:'(:L3)', 11:':L5', 12:'(:L5)', 13:':F3', 14:'[:F3]', 15:'(:s5)', 16:'[:c3]', 17:':L3', 18:':sL3', 19:':F3?', 20:'(:c3)'}

def label_to_net(labels_list, seq_len) -> np.array:

    labels_onehot = np.zeros((8, len(all_labels)), dtype='float32')
    
    for i in range(seq_len):
        labels = labels_list[i]
        for j in range(len(labels)):
            labels_onehot[i][all_labels[labels[j]]] = 1.0
    
    return labels_onehot

def net_to_label(labels_onehot, seq_len) -> np.array:
    
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

