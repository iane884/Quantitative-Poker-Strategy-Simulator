import random
from typing import List, Tuple, Dict, Optional
from deuces import Card as DeucesCard, Deck, Evaluator
from ..models.game_models import Card, GameState, ActionType, Street, PlayerAction

class PokerEngine:
    def __init__(self):
        self.evaluator = Evaluator()
        self.reset_game()
    
    def reset_game(self):
        """Reset for a new hand"""
        self.deck = Deck()
        print(f"DEBUG: reset_game - new deck created with {len(self.deck.cards)} cards")
        self.user_cards = []
        self.bot_cards = []
        self.community_cards = []
        self.pot = 0
        self.user_stack = 100
        self.bot_stack = 100
        self.current_bet = 0
        self.user_bet_this_street = 0
        self.bot_bet_this_street = 0
        self.street = Street.PREFLOP
        self.action_history = []
        self.hand_over = False
        self.winner = None
    
    def deal_new_hand(self) -> GameState:
        """Deal a new hand and return initial game state"""
        self.reset_game()
        
        # Deal hole cards
        self.user_cards = [self._deuces_to_card(self.deck.draw(1)), 
                          self._deuces_to_card(self.deck.draw(1))]
        self.bot_cards = [self._deuces_to_card(self.deck.draw(1)), 
                         self._deuces_to_card(self.deck.draw(1))]
        
        # Post blinds (simplified: user posts 2, bot posts 1)
        self.user_stack -= 2
        self.bot_stack -= 1
        self.pot = 3
        self.current_bet = 2
        self.user_bet_this_street = 2
        self.bot_bet_this_street = 1
        
        return self._get_game_state("user")
    
    def process_action(self, action_type: ActionType, amount: int = 0, player: str = "user") -> GameState:
        """Process a player action and return updated game state"""
        print(f"DEBUG: Processing action - player: {player}, action: {action_type}, amount: {amount}")
        action = PlayerAction(action_type=action_type, amount=amount, player=player)
        self.action_history.append(action)
        
        if player == "user":
            self._process_user_action(action_type, amount)
        else:
            self._process_bot_action(action_type, amount)
        
        # Check if betting round is complete
        if self._is_betting_round_complete():
            self._advance_street()
        
        # Determine next active player
        next_player = self._get_next_active_player()
        
        return self._get_game_state(next_player)
    
    def _process_user_action(self, action_type: ActionType, amount: int):
        """Process user's action"""
        print(f"DEBUG: _process_user_action - action: {action_type}, amount: {amount}")
        print(f"DEBUG: Current game state - user_stack: {self.user_stack}, current_bet: {self.current_bet}, user_bet_this_street: {self.user_bet_this_street}")
        
        if action_type == ActionType.FOLD:
            self.hand_over = True
            self.winner = "bot"
        elif action_type == ActionType.CALL:
            call_amount = min(self.current_bet - self.user_bet_this_street, self.user_stack)
            self.user_stack -= call_amount
            self.pot += call_amount
            self.user_bet_this_street += call_amount
        elif action_type == ActionType.CHECK:
            pass  # No money movement
        elif action_type in [ActionType.BET, ActionType.RAISE]:
            bet_amount = min(amount, self.user_stack)
            self.user_stack -= bet_amount
            self.pot += bet_amount
            self.user_bet_this_street += bet_amount
            self.current_bet = self.user_bet_this_street
        elif action_type == ActionType.ALL_IN:
            all_in_amount = self.user_stack
            self.user_stack = 0
            self.pot += all_in_amount
            self.user_bet_this_street += all_in_amount
            self.current_bet = self.user_bet_this_street
    
    def _process_bot_action(self, action_type: ActionType, amount: int):
        """Process bot's action"""
        if action_type == ActionType.FOLD:
            self.hand_over = True
            self.winner = "user"
        elif action_type == ActionType.CALL:
            call_amount = min(self.current_bet - self.bot_bet_this_street, self.bot_stack)
            self.bot_stack -= call_amount
            self.pot += call_amount
            self.bot_bet_this_street += call_amount
        elif action_type == ActionType.CHECK:
            pass  # No money movement
        elif action_type in [ActionType.BET, ActionType.RAISE]:
            bet_amount = min(amount, self.bot_stack)
            self.bot_stack -= bet_amount
            self.pot += bet_amount
            self.bot_bet_this_street += bet_amount
            self.current_bet = self.bot_bet_this_street
    
    def _is_betting_round_complete(self) -> bool:
        """Check if current betting round is complete"""
        if self.hand_over:
            return True
        
        # Both players have acted and bets are equal
        return (self.user_bet_this_street == self.bot_bet_this_street == self.current_bet or
                self.user_stack == 0 or self.bot_stack == 0)
    
    def _advance_street(self):
        """Advance to next street and deal community cards"""
        if self.hand_over:
            return
        
        print(f"DEBUG: _advance_street - current street: {self.street}, cards left in deck: {len(self.deck.cards)}")
        
        # Reset betting for new street
        self.user_bet_this_street = 0
        self.bot_bet_this_street = 0
        self.current_bet = 0
        
        if self.street == Street.PREFLOP:
            # Deal flop (3 cards)
            for _ in range(3):
                card = self.deck.draw(1)
                print(f"DEBUG: Drew flop card: {card}")
                if card == 0 or card is None:
                    print(f"ERROR: Invalid card drawn: {card}")
                    raise ValueError(f"Invalid card drawn from deck: {card}")
                self.community_cards.append(self._deuces_to_card(card))
            self.street = Street.FLOP
        elif self.street == Street.FLOP:
            # Deal turn (1 card)
            card = self.deck.draw(1)
            print(f"DEBUG: Drew turn card: {card}")
            if card == 0 or card is None:
                print(f"ERROR: Invalid card drawn: {card}")
                raise ValueError(f"Invalid card drawn from deck: {card}")
            self.community_cards.append(self._deuces_to_card(card))
            self.street = Street.TURN
        elif self.street == Street.TURN:
            # Deal river (1 card)
            card = self.deck.draw(1)
            print(f"DEBUG: Drew river card: {card}")
            if card == 0 or card is None:
                print(f"ERROR: Invalid card drawn: {card}")
                raise ValueError(f"Invalid card drawn from deck: {card}")
            self.community_cards.append(self._deuces_to_card(card))
            self.street = Street.RIVER
        elif self.street == Street.RIVER:
            # Showdown
            self._determine_winner()
    
    def _determine_winner(self):
        """Determine winner at showdown"""
        if len(self.community_cards) < 5:
            return
        
        user_deuces_cards = [self._card_to_deuces(card) for card in self.user_cards]
        bot_deuces_cards = [self._card_to_deuces(card) for card in self.bot_cards]
        board_deuces = [self._card_to_deuces(card) for card in self.community_cards]
        
        user_score = self.evaluator.evaluate(board_deuces, user_deuces_cards)
        bot_score = self.evaluator.evaluate(board_deuces, bot_deuces_cards)
        
        if user_score < bot_score:  # Lower score is better in deuces
            self.winner = "user"
        elif bot_score < user_score:
            self.winner = "bot"
        else:
            self.winner = "tie"
        
        self.hand_over = True
    
    def _get_next_active_player(self) -> str:
        """Determine who should act next"""
        if self.hand_over:
            return "none"
        
        # Simplified: user always acts first preflop, alternating after
        if self.street == Street.PREFLOP:
            if len([a for a in self.action_history if a.player == "user"]) == 0:
                return "user"
            elif len([a for a in self.action_history if a.player == "bot"]) == 0:
                return "bot"
        
        # Check if betting is balanced
        if self.user_bet_this_street == self.bot_bet_this_street:
            return "user"  # User acts first on new streets
        elif self.user_bet_this_street < self.current_bet:
            return "user"
        else:
            return "bot"
    
    def get_hand_equity(self, player_cards: List[Card], community_cards: List[Card], 
                       opponent_range: Optional[List[List[Card]]] = None) -> float:
        """Calculate hand equity using deuces evaluator"""
        if len(community_cards) == 5:
            # River - exact calculation
            user_deuces = [self._card_to_deuces(card) for card in player_cards]
            board_deuces = [self._card_to_deuces(card) for card in community_cards]
            
            # If we don't know opponent cards, assume random
            if opponent_range is None:
                wins = 0
                total = 0
                remaining_deck = self._get_remaining_cards(player_cards + community_cards)
                
                # Sample opponent hands
                for _ in range(100):  # Sample for speed
                    random.shuffle(remaining_deck)
                    opp_cards = remaining_deck[:2]
                    opp_deuces = [self._card_to_deuces(card) for card in opp_cards]
                    
                    user_score = self.evaluator.evaluate(board_deuces, user_deuces)
                    opp_score = self.evaluator.evaluate(board_deuces, opp_deuces)
                    
                    if user_score < opp_score:
                        wins += 1
                    total += 1
                
                return wins / total if total > 0 else 0.5
        
        # For earlier streets, use simplified equity calculation
        return self._estimate_preflop_equity(player_cards)
    
    def _estimate_preflop_equity(self, cards: List[Card]) -> float:
        """Simplified preflop equity estimation"""
        # Basic hand strength heuristic
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
        rank_values = {rank: i for i, rank in enumerate(ranks)}
        
        card1_val = rank_values[cards[0].rank]
        card2_val = rank_values[cards[1].rank]
        
        # Pocket pairs
        if card1_val == card2_val:
            return 0.5 + (card1_val / 26)  # 50% + bonus for higher pairs
        
        # Suited hands
        if cards[0].suit == cards[1].suit:
            high_card = max(card1_val, card2_val)
            return 0.45 + (high_card / 30)
        
        # Offsuit hands
        high_card = max(card1_val, card2_val)
        gap = abs(card1_val - card2_val)
        return 0.35 + (high_card / 35) - (gap / 50)
    
    def _get_remaining_cards(self, used_cards: List[Card]) -> List[Card]:
        """Get remaining cards in deck"""
        all_cards = []
        for suit in ['h', 'd', 'c', 's']:
            for rank in ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']:
                card = Card(rank=rank, suit=suit)
                if card not in used_cards:
                    all_cards.append(card)
        return all_cards
    
    def _deuces_to_card(self, deuces_card: int) -> Card:
        """Convert deuces card to our Card model"""
        rank_map = {2: '2', 3: '3', 4: '4', 5: '5', 6: '6', 7: '7', 8: '8', 
                   9: '9', 10: 'T', 11: 'J', 12: 'Q', 13: 'K', 14: 'A'}
        suit_map = {1: 's', 2: 'h', 4: 'd', 8: 'c'}
        
        print(f"DEBUG: Converting deuces card: {deuces_card}")
        rank = DeucesCard.get_rank_int(deuces_card)
        suit = DeucesCard.get_suit_int(deuces_card)
        print(f"DEBUG: Extracted rank: {rank}, suit: {suit}")
        
        if rank not in rank_map:
            raise ValueError(f"Invalid rank extracted from deuces card {deuces_card}: rank={rank}")
        if suit not in suit_map:
            raise ValueError(f"Invalid suit extracted from deuces card {deuces_card}: suit={suit}")
        
        return Card(rank=rank_map[rank], suit=suit_map[suit])
    
    def _card_to_deuces(self, card: Card) -> int:
        """Convert our Card model to deuces card"""
        return DeucesCard.new(card.rank + card.suit.lower())
    
    def _get_game_state(self, active_player: str) -> GameState:
        """Get current game state"""
        return GameState(
            session_id="default",  # TODO: implement session management
            street=self.street,
            pot_size=self.pot,
            user_stack=self.user_stack,
            bot_stack=self.bot_stack,
            user_cards=self.user_cards,
            community_cards=self.community_cards,
            current_bet=self.current_bet,
            to_call=max(0, self.current_bet - (self.user_bet_this_street if active_player == "user" else self.bot_bet_this_street)),
            active_player=active_player,
            action_history=self.action_history,
            hand_number=1,  # TODO: track hand numbers
            is_hand_over=self.hand_over,
            winner=self.winner
        ) 