from stable_baselines3.common.callbacks import BaseCallback

class RollingAverageRewardCallback(BaseCallback):
    def __init__(self, rolling_window=100, verbose=0):
        super().__init__(verbose)
        self.rolling_window = rolling_window  # Number of episodes to consider in the rolling average
        self.episode_rewards = []
        self.count = 0;

    def _on_step(self) -> bool:
        # Get the infos dictionary that might have 'episode' key if an episode finished
        infos = self.locals.get("infos")
        if infos is not None:
            for info in infos:
                # When using monitor or AtariWrapper, info sometimes contains an "episode" key with summary stats.
                if "episode" in info.keys():
                    #print (f'here: {infos}')
                    # Grab the episodic reward (e.g., info["episode"]["r"])
                    episode_reward = info["episode"]["r"]
                    self.episode_rewards.append(episode_reward)
                    # Ensure the rolling window contains at most `rolling_window` entries
                    if len(self.episode_rewards) > self.rolling_window:
                        self.episode_rewards.pop(0)
                    # Compute the rolling average of the episode rewards
                    rolling_avg = sum(self.episode_rewards) / len(self.episode_rewards)
                    # Log the rolling average to TensorBoard under the tag 'roll_avg/episode_reward'
                    self.logger.record("episode/roll_avg_reward", rolling_avg)
                    self.logger.record("episode/reward", episode_reward)
                    if "score" in info.get("episode", {}):
                        self.logger.record("episode/score", info["episode"]["score"])
                    else:
                        # Optionally log an alternative value or warn about the missing key.
                        self.logger.record("episode/score", -2)

                    if "score" in info.get("episode", {}):
                        self.logger.record("episode/cf", info["episode"]["cf"])
                    else:
                        # Optionally log an alternative value or warn about the missing key.
                        self.logger.record("episode/cf", -2)
                    if "score" in info.get("episode", {}):
                        self.logger.record("episode/bf", info["episode"]["bf"])
                    else:
                        # Optionally log an alternative value or warn about the missing key.
                        self.logger.record("episode/bf", -2)
                    if "score" in info.get("episode", {}):
                        
                        self.logger.record("episode/pf", info["episode"]["pf"])
                    else:
                        # Optionally log an alternative value or warn about the missing key.
                        self.logger.record("episode/pf", -2)

#                        
#                    self.logger.record("episode/counter",  self.count)
                    self.count += 1
        return True