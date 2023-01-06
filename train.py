import torch
import config as cfg

class Train:
    def __init__(self) -> None:
        # model is our nn that we update constantly
        """self.model = NeuralNet(state_space, self.action_space).to(torch.float32).to(device=self.device)"""
        # using ADAM loss
        self.model_optimizer = torch.optim.Adam(self.model.parameters(), lr=cfg.learning_rate)
        self.loss = torch.nn.SmoothL1Loss()

    def update_model(self, pred, target):
        loss = self.loss(pred, target)
        self.model_optimizer.zero_grad()
        loss.backward()
        self.model_optimizer.step()
    
    def train():
        # Total number of players in each position to input x Opponents is the input layer dimension
        # Pass data through network in batches of 64?
        # Contrast with predicted outputs from GA
        pass