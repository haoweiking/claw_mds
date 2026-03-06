# Errors Log

Command failures, exceptions, and unexpected behaviors.

---

## 2026-03-05

### Polymarket Markets Not Showing
- **Error**: `polymarket markets list --active true` returns no btc-updown markets
- **Type**: CLI Bug / Data Issue
- **Impact**: Could not find trading opportunities for 1+ hour
- **Root Cause**: CLI's list command doesn't filter btc-updown markets correctly
- **Workaround**: Generate slug manually using timestamp

### Cron Job Timeout
- **Error**: Job execution timed out after 180s
- **Type**: Timeout
- **Impact**: Missed trading opportunities
- **Root Cause**: Polymarket API calls taking too long
- **Fix**: Reduced complexity, increased timeout
