import torch.nn as nn

class SelectItem(nn.Module):
    def __init__(self, item_index):
        super(SelectItem, self).__init__()
        self._name = 'selectitem'
        self.item_index = item_index

    def forward(self, inputs):
        return inputs[self.item_index]


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

        self.encoder = nn.Sequential(*modules)

        # Decoder
        self.hiddens.reverse()
        modules = []

        in_dim = self.hiddens[0]
        for n_neurons in self.hiddens:
            modules.extend([nn.GRU(input_size=in_dim, hidden_size=n_neurons, num_layers=1, batch_first=True), SelectItem(0)])
            in_dim = n_neurons

        modules.extend([nn.Linear(self.hiddens[-1], self.n_features), nn.Sigmoid()])

        self.decoder = nn.Sequential(*modules)

    def forward(self, x):
        
        x = self.encoder(x)
        x = x[:, -1, :].unsqueeze(1).repeat(1, self.seq_len, 1)
        x = self.decoder(x)

        return x


class LSTM_AE_Composite(nn.Module):

    def __init__(self, seq_len, n_features, hidden_layer_list):

        super(LSTM_AE_Composite, self).__init__()
        assert isinstance(hidden_layer_list, list) and len( hidden_layer_list ) > 0
        self.seq_len, self.n_features = seq_len, n_features
        self.hiddens = hidden_layer_list

        # Encoder
        modules = []

        in_dim = self.n_features
        for n_neurons in self.hiddens:
            modules.extend([nn.GRU(input_size=in_dim, hidden_size=n_neurons, num_layers=1, batch_first=True), SelectItem(0)])
            in_dim = n_neurons

        self.encoder = nn.Sequential(*modules)

        self.hiddens.reverse()

        # Decoder 1 (reconstructor)
        modules = []

        in_dim = self.hiddens[0]
        for n_neurons in self.hiddens:
            modules.extend([nn.GRU(input_size=in_dim, hidden_size=n_neurons, num_layers=1, batch_first=True), SelectItem(0)])
            in_dim = n_neurons

        modules.extend([nn.Linear(self.hiddens[-1], self.n_features), nn.Sigmoid()])

        self.decoder1 = nn.Sequential(*modules)
        
        # Decoder 1 (label counter)
        self.decoder2 = nn.Sequential(nn.Linear(self.hiddens[0], 1), nn.ReLU())

    def forward(self, x):
        
        x = self.encoder(x)
        x = x[:, -1, :].unsqueeze(1).repeat(1, self.seq_len, 1)
        out1 = self.decoder1(x)

        out2 = self.decoder2(x)
        out2 = out2.squeeze()
        
        return out1, out2