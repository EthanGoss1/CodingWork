from Card import Card, Deck
class Hand:
    def __init__(self):
        self.cards = []
        self.sum = 0
        self.usable_ace = 0

    def add_card(self, card):
        self.cards.append(card)
        self.sum += card.value
        if card.rank == 'A':
            self.usable_ace += 1
        
        # If bot busted, check if it couldve turned an 11-Ace into a 1-Ace
        while self.sum > 21 and self.usable_ace > 0:
            self.sum -= 10
            self.usable_ace -= 1

class Blackjack:
    def __init__(self):
        self.deck = Deck()
        self.player_hand = None
        self.dealer_hand = None

    def reset(self):
        """Resets the game and returns the initial observation."""
        self.deck = Deck()
        self.player_hand = Hand()
        self.dealer_hand = Hand()

        # Initial deal
        self.player_hand.add_card(self.deck.deal())
        self.dealer_hand.add_card(self.deck.deal())
        self.player_hand.add_card(self.deck.deal())

        return self._get_obs()

    def _get_obs(self):
        """This returns the percept to the agent"""
        return (self.player_hand.sum, self.dealer_hand.cards[0].value, self.player_hand.usable_ace > 0)

    def step(self, action):
        """
        Hold = 0, Hit = 1
        Returns: (observation, reward, done)
        """
        if action == 1:  # Hit
            self.player_hand.add_card(self.deck.deal())
            if self.player_hand.sum > 21:
                return self._get_obs(), -1, True  # Player Bust
            return self._get_obs(), 0, False

        else:  # Hold
            # Dealer hits until sum > 16
            while self.dealer_hand.sum <= 16:
                self.dealer_hand.add_card(self.deck.deal())

            # Everyone done getting cards, determine winner
            p_sum = self.player_hand.sum
            d_sum = self.dealer_hand.sum

            if d_sum > 21 or p_sum > d_sum:
                reward = 1
            elif p_sum < d_sum:
                reward = -1
            else:
                reward = 0  # Draw
            
            return self._get_obs(), reward, True