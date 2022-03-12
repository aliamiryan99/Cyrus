import torch
import torch.nn as nn
import copy

class TimeDistributed(nn.Module):
    def __init__(self, module, batch_first=False):
        super(TimeDistributed, self).__init__()
        self.module = module
        self.batch_first = batch_first

    def forward(self, x):

        if len(x.size()) <= 2:
            return self.module(x)

        # Squash samples and timesteps into a single axis
        x_reshape = x.contiguous().view(-1, x.size(-1))  # (samples * timesteps, input_size)

        y = self.module(x_reshape)

        # We have to reshape Y
        if self.batch_first:
            y = y.contiguous().view(x.size(0), -1, y.size(-1))  # (samples, timesteps, output_size)
        else:
            y = y.view(-1, x.size(1), y.size(-1))  # (timesteps, samples, output_size)

        return y

class SelectItem(nn.Module):
    def __init__(self, item_index):
        super(SelectItem, self).__init__()
        self._name = 'selectitem'
        self.item_index = item_index

    def forward(self, inputs):
        return inputs[self.item_index]

class BN_Sequential(nn.Module):
    def __init__(self, in_dim):
        super(BN_Sequential, self).__init__()
        self._name = 'bn_seq'
        self.bn = nn.BatchNorm1d(in_dim)

    def forward(self, inputs):
        inputs = inputs.permute(0, 2, 1)
        return self.bn(inputs).permute(0, 2, 1)

class BN_Linear(nn.Module):
    def __init__(self, in_dim):
        super(BN_Linear, self).__init__()
        self._name = 'bn_linear'
        self.bn = nn.BatchNorm1d(in_dim)

    def forward(self, inputs):
        return self.bn(inputs)

class LSTM_AE(nn.Module):

    def __init__(self, seq_len, n_features, hidden_layer_list):

        super(LSTM_AE, self).__init__()
        assert isinstance(hidden_layer_list, list) and len( hidden_layer_list ) > 0
        self.seq_len, self.n_features = seq_len, n_features
        self.hiddens = hidden_layer_list

        # Encoder
        modules = []

        in_dim = self.n_features
        for n_neurons in self.hiddens:
            modules.extend([nn.GRU(input_size=in_dim, hidden_size=n_neurons, num_layers=1, batch_first=True), SelectItem(0)])
            in_dim = n_neurons

        print(modules)
        self.encoder = nn.Sequential(*modules)

        # Decoder
        self.hiddens.reverse()
        modules = []

        in_dim = self.hiddens[0]
        for n_neurons in self.hiddens:
            modules.extend([nn.GRU(input_size=in_dim, hidden_size=n_neurons, num_layers=1, batch_first=True), SelectItem(0)])
            in_dim = n_neurons

        modules.extend([TimeDistributed(nn.Linear(self.hiddens[-1], self.n_features), batch_first=True)])

        self.decoder = nn.Sequential(*modules)

    def forward(self, x):
        
        x = self.encoder(x)
        x = x[:, -1, :].unsqueeze(1).repeat(1, self.seq_len, 1)
        x = self.decoder(x)

        return x


class LSTM_AE_v2(nn.Module):

    def __init__(self, seq_len, n_features, hidden_layer_list):

        super(LSTM_AE_v2, self).__init__()
        assert isinstance(hidden_layer_list, list) and len( hidden_layer_list ) > 0
        self.seq_len, self.n_features = seq_len, n_features
        self.hiddens = hidden_layer_list

        # Encoder
        modules = []

        in_dim = self.n_features
        for n_neurons in self.hiddens:
            modules.extend([nn.GRU(input_size=in_dim, hidden_size=n_neurons, num_layers=1, batch_first=True), SelectItem(0)])
            in_dim = n_neurons

        print(modules)
        self.encoder = nn.Sequential(*modules)

        # Decoder
        self.hiddens.reverse()
        modules = []

        in_dim = self.hiddens[0]
        for n_neurons in self.hiddens:
            modules.extend([nn.GRU(input_size=in_dim, hidden_size=n_neurons, num_layers=1, batch_first=True), SelectItem(0)])
            in_dim = n_neurons

        modules.extend([TimeDistributed(nn.Linear(self.hiddens[-1], self.n_features), batch_first=True), nn.Sigmoid()])#, BN_Sequential(self.n_features)

        self.decoder = nn.Sequential(*modules)

    def forward(self, x):
        
        x = self.encoder(x)
        x = x[:, -1, :].unsqueeze(1).repeat(1, self.seq_len, 1)
        x = self.decoder(x)

        return x


class LSTM_Simple(nn.Module):

    def __init__(self, seq_len, n_features, hidden_layer_list):

        super(LSTM_Simple, self).__init__()
        assert isinstance(hidden_layer_list, list) and len( hidden_layer_list ) > 0
        self.seq_len, self.n_features = seq_len, n_features
        self.hiddens = hidden_layer_list

        # Encoder
        modules = []

        in_dim = self.n_features
        for n_neurons in self.hiddens:
            modules.extend([nn.GRU(input_size=in_dim, hidden_size=n_neurons, num_layers=1, batch_first=True), SelectItem(0)])
            in_dim = n_neurons

        print(modules)
        self.encoder = nn.Sequential(*modules)

        # Decoder
        self.hiddens.reverse()
        modules = []

        in_dim = self.hiddens[0]
        for n_neurons in self.hiddens:
            modules.extend([nn.GRU(input_size=in_dim, hidden_size=n_neurons, num_layers=1, batch_first=True), SelectItem(0)])
            in_dim = n_neurons

        modules.extend([TimeDistributed(nn.Linear(self.hiddens[-1], self.n_features), batch_first=True)]) #, nn.Sigmoid()

        self.decoder = nn.Sequential(*modules)

    def forward(self, x):

        return self.decoder(self.encoder(x))

class LSTM_Simple_v2(nn.Module):

    def __init__(self, seq_len, n_features, hidden_layer_list):

        super(LSTM_Simple_v2, self).__init__()
        assert isinstance(hidden_layer_list, list) and len( hidden_layer_list ) > 0
        self.seq_len, self.n_features = seq_len, n_features
        self.hiddens = hidden_layer_list

        # Encoder
        modules = []

        in_dim = self.n_features
        for n_neurons in self.hiddens:
            modules.extend([nn.GRU(input_size=in_dim, hidden_size=n_neurons), SelectItem(0)]) #, BN_Sequential(n_neurons)
            in_dim = n_neurons

        print(modules)
        self.encoder = nn.Sequential(*modules)

        # Decoder
        self.hiddens.reverse()
        modules = []

        in_dim = self.hiddens[0]
        for n_neurons in self.hiddens:
            modules.extend([nn.GRU(input_size=in_dim, hidden_size=n_neurons), SelectItem(0)]) # ,BN_Sequential(n_neurons)
            in_dim = n_neurons

        modules.extend([nn.Linear(self.hiddens[-1], self.n_features), nn.ReLU()]) #, nn.Sigmoid()

        self.decoder = nn.Sequential(*modules)

    def forward(self, x):
        return self.decoder(self.encoder(x))

class LSTM_AE_Composite(nn.Module):

    def __init__(self, seq_len, n_features, hidden_layer_list, max_labeled):

        super(LSTM_AE_Composite, self).__init__()
        assert isinstance(hidden_layer_list, list) and len( hidden_layer_list ) > 0
        self.seq_len, self.n_features = seq_len, n_features
        self.hiddens = hidden_layer_list

        # Encoder
        modules = []

        in_dim = self.n_features

        # https://pytorch.org/docs/stable/generated/torch.nn.GRU.html
        # all the layers except final one, we want first output; so we add SelectItem(0)
        for n_neurons in self.hiddens[:-1]:
            modules.extend([nn.GRU(input_size=in_dim, hidden_size=n_neurons, num_layers=1, batch_first=True), SelectItem(0)])
            in_dim = n_neurons
        
        # final layer of the encoder (also known as code layer, bottleneck,...)
        modules.extend([nn.GRU(input_size=in_dim, hidden_size=self.hiddens[-1], num_layers=1, batch_first=True), SelectItem(1)])

        self.encoder = nn.Sequential(*modules)

        self.hiddens.reverse()

        # Decoder 1 (reconstruction)
        modules = []

        in_dim = self.hiddens[0]
        for n_neurons in self.hiddens:
            modules.extend([nn.GRU(input_size=in_dim, hidden_size=n_neurons, num_layers=1, batch_first=True), SelectItem(0)])
            in_dim = n_neurons
        modules2 = copy.deepcopy(modules)


        modules.extend([nn.Linear(self.hiddens[-1], self.n_features), nn.Sigmoid()])
        self.decoder1 = nn.Sequential(*modules)
        
        # Decoder 2 (label counter)
        modules2.extend([nn.Linear(self.hiddens[-1], max_labeled), nn.Softmax(dim=-1)])
        self.decoder2 = nn.Sequential(*modules2)
        # self.decoder2 = nn.Sequential(nn.Linear(self.hiddens[0], max_labeled), nn.Sigmoid())

    def forward(self, x):
        
        h_code = self.encoder(x)
        h_code = h_code.reshape(h_code.shape[1], h_code.shape[0], h_code.shape[2]).repeat(1, self.seq_len, 1)
        out1 = self.decoder1(h_code)

        out2 = self.decoder2(h_code)
        # out2 = torch.sum(out2 > .5, dim=2).to(torch.float16)
        return out1, out2