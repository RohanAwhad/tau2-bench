# critic: empty assistant response crash (55e9cd3)

## Command

```bash
uv run tau2 run --domain airline --agent llm_agent \
  --agent-llm openai/served-critic \
  --agent-llm-args '{"api_base":"http://localhost:8000/v1","api_key":"local","temperature":0}' \
  --user-llm openai/gpt-oss-120b \
  --user-llm-args '{"api_base":"http://localhost:8101/v1","api_key":"local","temperature":0}' \
  --num-trials 3 --num-tasks 50 --max-concurrency 10 \
  --task-split-name base \
  --save-to served_critic_agent_user_120b_airline_full_3trials_mc10_55e9cd3
```

## Root cause

Wrapper at `localhost:8000` intermittently returns an assistant message with both `content=""` and `tool_calls=null` while `finish_reason="stop"`. This is an invalid response — the OpenAI chat completions spec requires at least one of `content` or `tool_calls` to be non-empty.

## Raw invalid response shape

```json
{
  "finish_reason": "stop",
  "message": {
    "content": "",
    "role": "assistant",
    "tool_calls": null
  }
}
```

## Error timeline

| Time | Task | Trial | Error |
|------|------|-------|-------|
| 19:37:34 | 17 | 0 | Empty response (caught, logged, run continued) |
| 19:38:51 | 26 | 0 | Empty response (caught, logged, run continued) |
| 19:39:27 | 19 | 0 | HTTP 500 InternalServerError (caught, logged, run continued) |
| later | unknown | unknown | Empty response (uncaught, crashed entire run) |

All 4 errors are the same root cause. The HTTP 500 on task 19 is likely the wrapper erroring internally when it fails to produce a valid response.

## Traceback (fatal crash)

```
src/tau2/run.py:519      run_task -> orchestrator.run()
src/tau2/orchestrator/orchestrator.py:397  run -> self.step()
src/tau2/orchestrator/orchestrator.py:487  step -> agent_msg.validate()
src/tau2/data_model/message.py:145        validate -> raise ValueError(...)

ValueError: AssistantMessage must contain non-empty content or at least one tool call.
Debug: role='assistant', content='', content_type=str, tool_calls_count=0,
raw_finish_reason='stop', raw_message_content='', raw_message_tool_calls=None
```

## Impact

- Run stopped at 68/150 simulations (82 missing trial-task pairs).
- Partial results saved to `data/simulations/served_critic_agent_user_120b_airline_full_3trials_mc10_55e9cd3.json`.

## Fix target

Wrapper must never return both `message.content=""` and `message.tool_calls=null`. At least one must be non-empty.
