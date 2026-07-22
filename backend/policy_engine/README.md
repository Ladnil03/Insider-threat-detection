# Policy Engine

Defines policy rules (e.g. "file copy > 100MB in an hour") and evaluates activity streams against them. Logs simulated automated actions (no real enforcement — just audit trail for analyst review).

**Inputs:** Activity records + rule definitions
**Outputs:** Policy violation events with severity and suggested action
