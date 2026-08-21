# DrunkIt — State Regulatory Matrix as Code (2026)

## Overview & Constitutional Grounding

In the Republic of India, the production, manufacture, possession, transport, purchase, and sale of intoxicating liquors is a state subject governed under **Entry 8, List II (State List), Seventh Schedule of the Constitution of India**.

Consequently, all commercial operations within DrunkIt (FACCP) execute against **Versioned Jurisdiction Rulesets**.

---

## 1. Authoritative State Regulatory Matrix

| Jurisdiction | State Code | Min Age | Online Discovery | Assisted Commerce | Digital Delivery | Statutory Retail Structure | Regulatory Authority & Baseline Policy | Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- | :---: |
| **West Bengal** | `IN-WB` | 21 | ✅ Allowed | ✅ Allowed | ✅ **Allowed** | Private Licensed Off-Shops | WBEIDC & State Excise Directorate (eRetail / eAbgari 2025-26) | 🟢 **Active Transactional** |
| **Maharashtra** | `IN-MH` | 21/25* | ✅ Allowed | ✅ Allowed | 🟡 Permit-Based | Private Licensed Retailers (FL-BR-II) | Maharashtra State Excise Dept (Bombay Prohibition Act 1949 & Rules) | 🟡 **Assisted Commerce** |
| **Karnataka** | `IN-KA` | 21 | ✅ Allowed | ✅ Allowed | 🟡 In Review | Private Retail (CL-2 / CL-9) & MSIL | Karnataka Excise Act 1965 & CL-2 Rules | 🟡 **Assisted Commerce** |
| **Delhi NCR** | `IN-DL` | 21 | ✅ Allowed | ✅ Allowed | 🟡 Conditional | 792 Government Retail Outlets (DSIIDC, DCCWS, DSCSC, DTTC) | Delhi Excise Dept (Delhi Excise Rules 2010; L-13 Framework) | 🟡 **Assisted Commerce** |
| **Telangana** | `IN-TG` | 21 | ✅ Allowed | ✅ Allowed | 🟡 In Review | Private Licensed A4 Retailers | Telangana Prohibition & Excise Dept (Telangana Excise Act 1968) | 🟡 **Assisted Commerce** |
| **Andhra Pradesh** | `IN-AP` | 21 | ✅ Allowed | ✅ Allowed | 🟡 In Review | State Licensed Retail Outlets | AP State Beverages Corp Ltd (APSBCL) & Excise Dept | 🟡 **Assisted Commerce** |
| **Madhya Pradesh**| `IN-MP` | 21 | ✅ Allowed | ✅ Allowed | ⚠️ Verified Only | Composite Retail Licensed Shops | MP Commercial Tax / Excise Dept (MP Excise Act 1915) | 🟡 **Assisted Commerce** |
| **Uttar Pradesh** | `IN-UP` | 21 | ✅ Allowed | ✅ Allowed | 🟡 In Review | Private Licensed Retail (FL-4 / FL-5) | UP Excise Dept (Barcoded Track-and-Trace eAbgari) | 🟡 **Assisted Discovery** |
| **Rajasthan** | `IN-RJ` | 21 | ✅ Allowed | ✅ Allowed | 🟡 In Review | Private Licensed Retail Shops (RSBCL) | Rajasthan State Ganganagar Sugar Mills / Excise Dept | 🟡 **Assisted Discovery** |
| **Punjab** | `IN-PB` | 21 | ✅ Allowed | ✅ Allowed | 🟡 In Review | Private L-2 Retail Licensed Vends | Punjab Excise & Taxation Dept (Punjab Excise Act 1914) | 🟡 **Assisted Discovery** |
| **Odisha** | `IN-OD` | 21 | ✅ Allowed | ✅ Allowed | 🔴 Restricted | Private "OFF" Shops | Odisha Excise Policy 2026-29 (Online delivery restrictions) | ⚠️ **Watchlist Only** |
| **Tamil Nadu** | `IN-TN` | 21 | ⚠️ Restricted| ⚠️ Restricted| 🔴 Prohibited | Exclusive State Monopoly (TASMAC) | TASMAC Monopoly Administration | 🔴 **Non-Transactional** |

*\*Note: In Maharashtra, minimum drinking age is 21 for mild beer/wine and 25 for hard spirits/IMFL.*

---

## 2. Statutory Verification Gate Definitions

For every checkout or reservation attempt, the platform evaluates:

1. **`STATUTORY_AGE`**: Consumer's verified birth date $\ge \text{Jurisdiction Minimum Age}$.
2. **`DRY_DAY_CHECK`**: Order timestamp does not intersect with gazetted election dry days, religious festival dry days, or national holidays.
3. **`OPERATING_HOURS`**: Order timestamp is within state-permitted retail operating hours (e.g., 10:00 AM to 10:00 PM local time).
4. **`RETAILER_LICENCE_VALIDITY`**: The merchant holding the inventory has an active, non-expired excise license validated by platform administration.
5. **`TRANSACTION_QUANTITY_CAP`**: Order volume complies with the maximum permissible individual possession limit per transaction (e.g., max 9 liters total spirits/beer in select states).
6. **`DELIVERY_ZONE_AUTHORIZATION`**: Consumer delivery address coordinates fall strictly within the licensed delivery radius (typically 5.0 km) of the fulfillment merchant.

---

## 3. Versioning Protocol

Rulesets are never hardcoded in application logic. They are maintained as data files with semantic versioning:
- Format: `[STATE_CODE]-[YEAR]-[MONTH]-[REVISION]` (e.g., `IN-WB-2026-08-v1`).
- Changes to state excise policies trigger new ruleset releases with automated unit and regression test suites.
