# 📊 Post-Launch Monitoring

**First 30 days.** Track everything. Adjust nothing until day 14.

---

## 📊 DAILY METRICS (logged every morning)

| Metric | Today | Yesterday | 7d Avg |
|---|---|---|---|
| Workshop subscriptions | ___ | ___ | ___ |
| Workshop favorites | ___ | ___ | ___ |
| itch downloads | ___ | ___ | ___ |
| itch ratings | ___ | ___ | ___ |
| Discord members | ___ | ___ | ___ |
| Discord active (24h) | ___ | ___ | ___ |
| GitHub stars (new) | ___ | ___ | ___ |
| Twitter impressions | ___ | ___ | ___ |
| Landing page visitors | ___ | ___ | ___ |
| Crash reports | ___ | ___ | ___ |
| Critical issues | ___ | ___ | ___ |

Source:
- Plausible (landing page)
- GitHub API (stars, issues)
- itch.io dashboard
- Wallpaper Engine Workshop (manual check)
- Discord bot
- Twitter analytics

---

## 🔍 WEEKLY DEEP DIVE (Monday)

```text
WEEK OF [DATE]

Wins
  [Win 1]
  [Win 2]

Misses
  [Miss 1]
  [Miss 2]

Top feedback themes
  [Theme 1]: [#] mentions
  [Theme 2]: [#] mentions

Top bug reports
  [Bug 1]: [#] reports
  [Bug 2]: [#] reports

Top feature requests
  [Feature 1]: [#] votes
  [Feature 2]: [#] votes

Decision
  [What we're shipping next week]
```

---

## 🛠️ FEEDBACK COLLECTION

### Sources
- GitHub Issues (primary — structured)
- Discord #feedback channel
- itch.io comments
- Twitter DMs
- Reddit threads
- Direct emails

### Categorization
Every feedback item tagged:
- `bug` — something broken
- `crash` — app crashes
- `performance` — slow, laggy
- `ux` — confusing UI
- `feature` — new capability
- `content` — new biomes, themes
- `praise` — positive feedback (boost morale!)
- `question` — needs answer

### Response SLA
- Critical (crash, blocker): 24h
- Bug (reproducible): 3 days
- Feature request: acknowledge within 7 days
- Question: 24h

---

## 📈 GROWTH SIGNALS TO WATCH

### Green (healthy growth)
- ✅ Subscriptions growing week-over-week
- ✅ Discord active rate > 30%
- ✅ Positive comments on storefronts
- ✅ Organic shares on social
- ✅ GitHub stars from non-author accounts
- ✅ Return users (Workshop favorites)

### Yellow (needs attention)
- ⚠️ Subscriptions flat
- ⚠️ Crash rate > 1%
- ⚠️ Negative comments appearing
- ⚠️ No new contributors
- ⚠️ No organic shares

### Red (urgent action)
- 🚨 Crash rate > 5%
- 🚨 Sustained negative feedback
- 🚨 Steam/itch negative review trend
- 🚨 Major bug unfixed for >7 days
- 🚨 Community churn (people leaving Discord)

---

## 🎯 DECISION GATES

### Day 30 — Go/No-Go for v1.1
```text
GREEN: Continue with planned v1.1 features
  • More biomes (community requests)
  • Performance improvements
  • UX polish

YELLOW: Pivot
  • Focus on what users love
  • Fix top 3 reported bugs
  • Pause new features

RED: Stop and rethink
  • Do NOT add features
  • Understand why users aren't sticking
  • Talk to 10 active users
```

### Day 90 — Commercial decision
```text
If users > 1,000 and growing:
  → Consider paid tiers (DLC, Pro)
  → Plan Steam release

If users < 1,000 but retention is strong:
  → Improve organic reach
  → Build community
  → Wait

If users < 1,000 and retention is weak:
  → Investigate product-market fit
  → Major pivot or pause
```

---

## 📊 REPORTING CADENCE

| Frequency | Recipient | Content |
|---|---|---|
| Daily (self) | Sahil | Metrics log |
| Weekly (Monday) | Discord #general | Win/miss summary |
| Monthly (1st) | Patreon + newsletter | Detailed report |
| Quarterly | Patreon + investors (if any) | Strategic review |

---

## 🚨 INCIDENT RESPONSE

### Crash spike detected
1. Acknowledge on Discord + Twitter
2. Investigate (open GitHub issue)
3. Ship fix (within 4h critical, 24h non-critical)
4. Apologize + thank reporter
5. Post-mortem on Discord

### Negative review
1. Don't engage publicly with emotion
2. Reply professionally, offer help
3. Fix if legitimate
4. Don't argue

### Security issue
1. Email security@primordials.dev
2. Don't engage publicly
3. Patch + disclose responsibly
4. Update SECURITY.md

---

## 📞 KEY CHANNELS

- 📧 hello@primordials.dev (general)
- 📧 press@primordials.dev (press)
- 📧 security@primordials.dev (security)
- 💬 discord.gg/primordials
- 🐦 @PrimordialsGame
- 💻 github.com/SahilKhutey/Primodials
