from torch import nn


class NeuralNet(nn.Module):

    def __init__(self, input_dim, output_dim):
        super().__init__()
        # input_dim = state space
        # output_dim = number of players available for that posn
        channels = input_dim 
        self.neural_net = nn.Sequential(
            nn.Linear(in_channels=channels, out_channels=256),
            nn.Mish(),
            nn.Linear(in_channels=256, out_channels=64),
            nn.Mish(),
            nn.Linear(in_channels=128, out_channels=16),
            nn.Mish(),
            nn.Linear(in_channels=16, out_channels=output_dim),
        )
        
    # forward pass definition
    def forward(self, input):
        return self.neural_net(input)