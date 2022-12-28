## What is a "QB stat"?

Surely passing yards is a QB stat. Likewise, completion percentage, sack rates, and touchdowns must be QB stats too, right? 

The main argument against wins being a QB stat is that wins are a team effort. However, so is every other stat. You can't complete a pass without someone being there to catch it. 

In a way, every stat recorded in a game exists on a spectrum. On one end, you can imagine a hypothetical "perfect QB stat", which fully isolates good vs. bad QB play. On the other end, you have pure "team stats", where QB play is irrelevant (e.g., a team's sack rate). In this project, I tried to map out this spectrum, and find how win percentage stacks up against other stats in differentiating good vs. bad QB play. 

To identify what is the most "QB Stat" of all stats, I examined how a team's performance changes when a starting QB goes down and a backup QB must play. Specifically, I looked at the past decade of NFL data, and found seasons where teams had their starting QB go down midway due to injury. I examined how the QB switch impacted the team's performances in subsequent games. This analysis allows me to roughly measure a starting QB's contributions, while holding their surrounding team quality constant.

## Statistical details

Statistically, I looked at standard deviations. Doing so creates a "common currency" on which to compare different stats. For example, suppose I want to compare the impacts of starting QB play on *passing yards per attempt* (Y/A) vs. *completion percentage*. The average starting QB in my dataset has 6.31 Y/A and 57.4% completion percentage, whereas the average backup has 5.60 Y/A and 55.4% completion percentage. 

To assess whether the difference in Y/A (6.31 vs. 5.60) is larger than the difference in completion percentage (57.4% vs. 55.4%), I standardize the statistics based on their means and typical typical degree of variability. For example, if a typical QB varied wildly in their Y/A, often swinging from very high (10.0) and very low (1.0), this would mean that a difference of 0.71 is not worth much and could be due to chance. On the other hand, if Y/A varies little, swinging from only 6.0 to 5.5, a gain in 0.71 would be a major improvement. 

Formally, we use this standardization principle to calculate a [Cohen's d effect size](https://en.wikipedia.org/wiki/Effect_size#Cohen's_d), which can be measured for every statistic to examine how much the statistic changes between starting vs. backup QBs. For example, we may find that a starting QB is 0.5 standard deviations better (d = 0.5) than a backup QB in Y/A.

## Results

Wins faired pretty well at being a QB stat. Starting QBs win 12.6% more games than backups (d = 0.45), and standardized, this difference is bigger than what is seen many other stats people traditionally agree to be QB stats. For example, *win percentage* is a better QB stat than number of *passing touchdowns per game* (starting QBs score 0.3 more TDs, d = 0.43), *completion percentage* (starting QBs are 2.2% higher, d = 0.37), *sack rate* (starting QBs get sacked 0.8% less, d = -0.25), and *interception rate* (starting QBs get picked 0.3% less, d = -0.22).

Now this is not to say that wins are the best QB stat. *Yards per play* is the best common statistic in differentiating starting vs. backup QBs, with starting QBs achieving 3.7 more yards per play (d = 0.61). Interestingly, this is plain yards per play, which includes outcomes of plays where the QB just hands off the ball to the running back. The standardized difference is even slightly larger than for *passing yards per play*, where starting QBs achieve 0.71 more yards/play than backups (d = 0.59). First down rate too is a good QB stat, with starting QBs getting firsts downs 2.8% more often (d = 0.50). 

## Conclusion

Wins actually are a QB stat. Wins differentiate good vs. bad QBs better than passing touchdowns, completion percentage, sack rate, and interception rate. Wins are not the best QB stat, yards per play and first down rate are better. Nonetheless, wins are a solid QB stat and should be considered when evaluating a quarterback.

For original writeup see this [Reddit post](https://www.reddit.com/r/nfl/comments/jeratd/are_wins_a_qb_stat_statistical_analyses_on_the/)
