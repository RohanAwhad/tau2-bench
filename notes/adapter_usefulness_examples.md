# Adapter Usefulness: Worst Blunders & Best Saves

Source: `adapter_usefulness_full_mtall_mc25_b4dbb65.json` against `served_adapter_agent_user_120b_airline_full_3trials_mc50_b4dbb65.json`

---

## Adapter Blunders (usefulness = -1.0)

### Blunder 1: Task 16, Trial 0 (reward 0.0)

**Scenario:** User wants to change reservation M05KNL to the cheapest economy flight ATL->PHL on 2024-05-24. The correct answer is a one-stop flight (HAT110+HAT172).

**What happened:** The API model kept trying to call `search_onestop_flight` (the correct tool to find the cheapest option), but the adapter blocked it **every single time** across turns 10, 12, 20, 22. Instead, the adapter:

- Turn 10: Replaced the one-stop search with a premature "please confirm" text message
- Turn 12: Replaced the one-stop search with `update_reservation_flights` using flight HAT001 (a direct flight, **not the cheapest**)
- Turn 14: Retried the same wrong update
- Turn 20: Changed `search_onestop_flight` -> `search_direct_flight` (already done, redundant)
- Turn 22: Replaced the one-stop search with a false success message claiming the reservation was updated

**Bottom line:** API knew it needed one-stop results. Adapter kept hijacking the call, committed to the wrong flight, and then lied about success. Task failed.

---

### Blunder 2: Task 39, Trial 0 (reward 0.0)

**Scenario:** User Amelia Davis wants to cancel all 7 reservations (change of plans).

**What happened:** The API wanted to methodically call `get_reservation_details` for each reservation before cancelling. The adapter short-circuited this:

- Turn 6: API drafted `get_reservation_details("8C8K4E")` -> adapter replaced with text listing reservation IDs, skipping the lookup
- Turn 10: API drafted `get_reservation_details("UDMOP1")` -> adapter changed it to `cancel_reservation("8C8K4E")`, cancelling without checking details on the next one
- Turn 12: API again tried `get_reservation_details("UDMOP1")` -> adapter replaced with "please confirm" text
- Turn 14: API drafted `cancel_reservation("UDMOP1")` for one -> adapter expanded to batch-cancel all 7 at once, **without ever calling `get_reservation_details` on 6 of them**

**Bottom line:** The required action was `get_reservation_details` on each reservation before cancellation. Adapter skipped this step for most reservations, causing DB check failures.

---

### Blunder 3: Task 21, Trial 0 (reward 0.0)

**Scenario:** Sofia Kim wants to change a Houston-to-Denver return flight to the fastest same-day option, add a checked bag, and pay with smallest-balance gift card.

**What happened:**

- Turn 6: API drafted `get_reservation_details("OI5L9G")` (correct next step) -> adapter changed it to `get_user_details` (already fetched at turn 4), wasting a turn
- Turn 16: API drafted `get_reservation_details("4BMN53")` to continue searching -> adapter **removed the tool call and fabricated**: "Sure, I've located your reservation for Houston to Denver" — when it hadn't actually looked it up
- Turn 22: API searched `DEN->IAH` (correct return direction) -> adapter changed the route to `ORD->DEN` (completely wrong)
- Turn 28: API tried `search_onestop_flight` DEN->IAH again -> adapter fabricated flight options on the wrong route

**Bottom line:** Adapter redirected searches to wrong routes, fabricated "found it" messages, and the agent never operated on the right data. Task failed.

---

## Adapter Saves (usefulness = 1.0)

### Save 1: Task 11, Trial 1 (reward 1.0)

**Scenario:** User wants to downgrade all passengers on reservation GV1N64 from Business to Basic Economy and get a refund.

**What happened:** The API kept calling the wrong tool (`search_direct_flight`) instead of actually doing the update:

- Turn 4: API jumped to `get_reservation_details` without verifying user ID -> adapter asked for user ID first
- Turn 8: User confirmed, API called `search_direct_flight` (irrelevant) -> adapter replaced with a confirmation prompt
- Turn 10: User confirmed again, API **again** called `search_direct_flight` -> adapter replaced with the correct `update_reservation_flights` call with proper reservation_id, cabin="basic_economy", flights, and payment_id
- Turns 12-18: API kept outputting premature success messages with wrong refund amounts instead of executing the tool -> adapter kept retrying the `update_reservation_flights` call until it went through

**Bottom line:** API couldn't figure out the right tool. Adapter constructed the correct `update_reservation_flights` call and persisted until it succeeded. Task passed.

---

### Save 2: Task 31, Trial 0 (reward 1.0)

**Scenario:** Daiki Lee wants to modify a basic economy flight (reservation DF89BM), which isn't allowed per policy — should be transferred to human agent.

**What happened:**

- Turn 4: API drafted `get_user_details("daika_lee_6144")` — **typo** in user_id (daik**a** vs daik**i**). Adapter fixed it to `"daiki_lee_6144"`. Without this fix, the lookup would have failed.
- Turns 12, 16, 18, 20, 22, 24: API kept outputting text-only "YOU ARE BEING TRANSFERRED TO A HUMAN AGENT" messages **without actually calling `transfer_to_human_agents`**. Each time the adapter patched in the actual tool call with a proper summary argument.

**Bottom line:** API had two systematic failures: a typo that would have broken the flow, and a persistent inability to actually invoke the transfer tool. Adapter fixed both, 7 out of 7 major failures corrected. Task passed.

---

### Save 3: Task 5, Trial 1 (reward 1.0)

**Scenario:** Mei Brown claims Gold status and wants compensation for delayed flight HAT045. System shows she's actually "regular" status — needs verification and proper policy handling.

**What happened:**

- Turn 2: API jumped straight to `get_user_details` without asking for reservation number -> adapter blocked it and asked for the reservation number first (proper verification flow)
- Turn 8: API tried to look up reservation DB1Y70 (exposing unrelated booking data) -> adapter blocked it and instead noted the membership discrepancy (regular vs claimed Gold), asking for clarification
- Turn 18: API got stuck in a loop outputting "YOU ARE BEING TRANSFERRED" text three times without acting -> adapter replaced it with a substantive policy-based response offering $50 travel certificate per Gold status policy

**Bottom line:** API was sloppy about verification and got stuck in a transfer loop. Adapter enforced proper identity verification and broke the loop with an actionable policy response. Task passed.
