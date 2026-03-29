# Conceptual Flow

```mermaid
flowchart LR
  A["Platform Operations"]

  A --> B["Authentication"]
  A --> C["User Management"]
  A --> D["User Self-Service"]
  A --> E["Oversight"]
  A --> F["Platform Control"]

  B --> B1["Register"]
  B --> B2["Login"]
  B --> B3["Google Sign-In"]
  B --> B4["Email Verification"]
  B --> B5["Password Reset"]
  B --> B6["Login lockout"]

  C --> C1["Accounts"]
  C1 --> C1a["Create Account"]
  C1 --> C1b["Internal Creation"]
  C1 --> C1c["Self Registration"]
  C1 --> C1d["Update Account"]
  C1 --> C1e["Activate / Suspend Account"]
  C1 --> C1f["Delete Account"]

  C --> C2["Access Model"]
  C2 --> C2a["Role"]
  C2 --> C2b["Role permissions"]
  C2 --> C2c["Feature gating"]

  D --> D1["Profile Management"]
  D1 --> D1a["Update Personal Details"]
  D1 --> D1b["Manage Preferences"]

  D --> D2["Notifications"]
  D2 --> D2a["View Notifications"]
  D2 --> D2b["Mark as Read"]

  E --> E1["Audit Logging"]
  E1 --> E1a["Track User Actions"]
  E1 --> E1b["Review Activity History"]

  F --> F1["Platform Settings"]
  F1 --> F1a["Security policy"]
  F1 --> F1b["Feature flags"]
  F1 --> F1c["Role permission mappings"]
```
