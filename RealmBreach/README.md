# REALM BREACH

A dark dungeon crawler for Roblox with endless floors. Each file in this folder is copied into Roblox Studio at the Explorer path that matches its folder.

## Build progress

| # | Section | Files | Status |
|---|---------|-------|--------|
| 1 | ReplicatedStorage | `ReplicatedStorage/GameConfig.lua`, `ReplicatedStorage/RemoteEvents/CreateRemotes.lua` | Done |
| 2 | ServerScriptService > PlayerData | | Next |
| 3 | ServerScriptService > LootSystem | | |
| 4 | ServerScriptService > EnemySpawner | | |
| 5 | ServerScriptService > CombatServer | | |
| 6 | StarterPlayerScripts > CombatClient | | |
| 7 | StarterGui > MainGui | | |
| 8 | StarterPlayerScripts > GUI | | |

## Remotes (ReplicatedStorage > RemoteEvents)

| Name | Type | Direction | Purpose |
|------|------|-----------|---------|
| DealDamage | RemoteEvent | Client → Server, Server → Client | Basic attack request; damage numbers |
| PlayerDied | RemoteEvent | Server → Client | Death info and lives left |
| LootDropped | RemoteEvent | Server → Client | Loot popup data |
| UpdateStats | RemoteEvent | Server → Client | Full stat snapshot |
| UseAbility | RemoteEvent | Client → Server, Server → Client | Q/E/R press; cooldown started |
| UnlockSkill | RemoteEvent | Client → Server | Spend a skill point |
| Notify | RemoteEvent | Server → Client | Toast messages |
| GetPlayerData | RemoteFunction | Client → Server | Request a stat snapshot |

Server scripts talk to each other through BindableEvents. `GameConfig.GetServerSignal` creates them at runtime in `ServerStorage > ServerSignals`, so you don't make these by hand.
