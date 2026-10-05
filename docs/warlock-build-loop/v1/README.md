# Warlock GUI loop startup

The user cleared the old hosted goal. `get_goal` confirmed no goal, then `create_goal` created the new Warlock GUI completion goal. A subsequent readback confirmed **active**. The reset did not mark the unfinished project complete.

Repository `AGENTS.md` now directs future work to [INSTRUCTIONS.md](INSTRUCTIONS.md), including the current brand, consensus research/OpenSpec/EARS adoption and complete GUI release gates. Native QA still uses the original protected launcher and shared coordinator lock. Earlier blocked-goal records are historical evidence.

- [Active goal record](new-hosted-goal.json)
- [Reset receipt](reset-receipt.json)
- [Reusable startup command](START-GOAL.txt)

If starting in a new thread, use the startup command there. It is not a shell command. Current runtime status comes from the host goal controls, not this historical record. The repository coordinator does not itself start AI turns.

Official lifecycle reference: [Using Goals in Codex](https://developers.openai.com/cookbook/examples/codex/using_goals_in_codex).
