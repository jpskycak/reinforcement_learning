# Reinforcement Learning -- Sutton & Barto

### PAGES 1-8

* RL system = policy + reward signal + value function + (optional) model
  * policy maps environment to action
  * reward signal is given each step (short-term gain)
  * value function is total amount of reward agent can expect to accumulate over future (long-term gain). Example: P(win|state)
  * model allows inferences to be made about environment, which allows for planning
  
* evolutionary methods not well-suited to RL because they don't leverage individual behavioral interactions (if the player
wins or loses, then all of its behavior in the game is given credit for that win or loss)

* temporal-difference learning method
  1. assign values V(s) to all states s
  2. move greedily through all states, with the occasionally random move for exploration
  3. after each greedy move, update V(s_n) <-- V(s_n) + \alpha [ V(s_{n+1}) - V(s_n)]. This is the "temporal-difference' learning method and the step-size parameter \alpha is reduced properly over time, it converges, for any fixed opponent, to the true probabilities of winning from each state given optimal play by us. I.e. converges to optimal policy. (If you don't reduce \alpha, then the policy will also perform well against opponents who slowly change their strategy).

### [PROJECT 1](https://github.com/jpskycak/reinforcement_learning/blob/master/project1_tictactoe_experiments.ipynb): program this for tic-tac-toe

* improvement: instead of \alpha, use \alpha * (1-P(win)). This way, when win probability is low, agent learns with high rate; when win probability is high, agent learns with low rate -- i.e. dynamic slowing/speeding of learning rate
* improvement: use recombining state tree to reduce dimensionality and yield faster learning (vs non-recombining state tree).
* improvement (not implemented): initialize values better so that training occurs more quickly 
