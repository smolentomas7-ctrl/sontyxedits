--[[
	REALM BREACH — GameConfig
	Script Type : ModuleScript
	Location    : ReplicatedStorage > GameConfig
	Every tunable number in the game. Required by BOTH server and client.
	Change balance here, never inside the other scripts.
	Depends on : ReplicatedStorage > RemoteEvents (Folder)
	Used by    : PlayerData, LootSystem, EnemySpawner, CombatServer, CombatClient, GUI
]]

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")

local GameConfig = {}
local sharedRandom = Random.new()

--[[ Remote Names ]]
-- Every remote lives in ReplicatedStorage > RemoteEvents. C->S = client to server, S->C = server to client.
GameConfig.RemoteFolderName = "RemoteEvents"
GameConfig.Remotes = {
	DealDamage = "DealDamage",       -- RemoteEvent    | C->S basic attack    | S->C damage numbers
	PlayerDied = "PlayerDied",       -- RemoteEvent    | S->C death info + lives left
	LootDropped = "LootDropped",     -- RemoteEvent    | S->C loot popup data
	UpdateStats = "UpdateStats",     -- RemoteEvent    | S->C full stat snapshot
	UseAbility = "UseAbility",       -- RemoteEvent    | C->S Q/E/R pressed   | S->C cooldown started
	UnlockSkill = "UnlockSkill",     -- RemoteEvent    | C->S spend a skill point
	Notify = "Notify",               -- RemoteEvent    | S->C toast (level up, rewards, floors)
	GetPlayerData = "GetPlayerData", -- RemoteFunction | C->S ask for a stat snapshot
}

--[[ Server Signals ]]
-- Server-only BindableEvents so server Scripts can talk. Auto-created in ServerStorage > ServerSignals.
GameConfig.ServerSignalFolderName = "ServerSignals"
GameConfig.ServerSignals = {
	EnemyKilled = "EnemyKilled",   -- (enemyModel, killerPlayer)  CombatServer -> PlayerData, LootSystem, EnemySpawner
	AwardXP = "AwardXP",           -- (player, amount, reason)    any -> PlayerData
	AwardShards = "AwardShards",   -- (player, amount)            any -> PlayerData
	AwardItem = "AwardItem",       -- (player, itemTable)         LootSystem -> PlayerData
	FloorCleared = "FloorCleared", -- (floorNumber)               EnemySpawner -> PlayerData, LootSystem
	StartRun = "StartRun",         -- (player)                    EnemySpawner portal -> PlayerData
	RunEnded = "RunEnded",         -- (player, floorReached)      PlayerData -> EnemySpawner, LootSystem
}

--[[ CollectionService Tags ]]
GameConfig.Tags = { Enemy = "RealmEnemy", LootDrop = "RealmLoot" }

--[[ DataStore ]]
GameConfig.DataStore = {
	Name = "RealmBreach_PlayerData_v1", -- change the suffix to wipe everyone's saves
	AutosaveInterval = 120,             -- seconds between automatic saves
	MaxRetries = 3, RetryDelay = 2,     -- attempts per load/save, seconds between attempts
}

--[[ Player Base Stats ]]
GameConfig.Player = {
	StartingLives = 3,
	BaseMaxHealth = 100, HealthPerLevel = 12,
	BaseDamage = 10, DamagePerLevel = 2,
	BaseWalkSpeed = 16,
	RespawnDelay = 3, SpawnShieldTime = 3,  -- seconds to respawn, seconds of spawn invulnerability
	MaxInventory = 24, SkillPointsPerLevel = 1, -- past 24 items the oldest unequipped item is removed
}

--[[ Leveling ]]
-- BaseXP = XP needed for level 1 -> 2. Growth = each level needs 12% more than the last.
GameConfig.Leveling = { MaxLevel = 200, BaseXP = 60, Growth = 1.12 }

--[[ Combat ]]
GameConfig.Combat = {
	AttackCooldown = 0.45,   -- seconds between basic attacks
	AttackRange = 10, AttackArcDegrees = 110, -- basic attack cone: length in studs, width in degrees
	BaseCritChance = 0.05, MaxCritChance = 0.6, CritMultiplier = 2,
	DamageVariance = 0.15,   -- damage rolls between 85% and 115%
	RangeTolerance = 6,      -- extra studs the server allows for network lag
	MaxLifesteal = 0.25,
}

--[[ Abilities (Q / E / R) ]]
GameConfig.AbilityKeys = { "Q", "E", "R" }
GameConfig.Abilities = {
	-- Q: wide cone slash in front of the player
	Q = { Id = "RiftSlash", DisplayName = "Rift Slash", UnlockLevel = 1, Cooldown = 4, DamageMultiplier = 2.5,
		Range = 14, ArcDegrees = 160, Color = Color3.fromRGB(255, 50, 90) },
	-- E: dash forward, then damage everything around the landing spot
	E = { Id = "VoidDash", DisplayName = "Void Dash", UnlockLevel = 3, Cooldown = 8, DamageMultiplier = 1.8,
		DashDistance = 24, DashDuration = 0.25, Radius = 9, Color = Color3.fromRGB(150, 70, 255) },
	-- R: ultimate — huge shockwave around the player
	R = { Id = "RealmShatter", DisplayName = "Realm Shatter", UnlockLevel = 6, Cooldown = 22, DamageMultiplier = 6,
		Radius = 26, Color = Color3.fromRGB(0, 230, 255) },
}

--[[ Skill Tree ]]
-- Order here is the order shown in the GUI. PerRank is added once per rank bought.
GameConfig.SkillTree = {
	{ Id = "Vitality", DisplayName = "Vitality", Stat = "MaxHealthPercent", PerRank = 0.08, MaxRank = 10, Cost = 1, RequiredLevel = 1, Description = "+8% Max Health per rank" },
	{ Id = "Brutality", DisplayName = "Brutality", Stat = "DamagePercent", PerRank = 0.06, MaxRank = 10, Cost = 1, RequiredLevel = 1, Description = "+6% Damage per rank" },
	{ Id = "Swiftness", DisplayName = "Swiftness", Stat = "WalkSpeed", PerRank = 1, MaxRank = 8, Cost = 1, RequiredLevel = 2, Description = "+1 Walk Speed per rank" },
	{ Id = "Fortune", DisplayName = "Fortune", Stat = "LootLuck", PerRank = 0.05, MaxRank = 10, Cost = 1, RequiredLevel = 3, Description = "+5% Loot Luck per rank" },
	{ Id = "Bloodthirst", DisplayName = "Bloodthirst", Stat = "Lifesteal", PerRank = 0.02, MaxRank = 10, Cost = 1, RequiredLevel = 5, Description = "+2% Lifesteal per rank" },
	{ Id = "Precision", DisplayName = "Precision", Stat = "CritChance", PerRank = 0.02, MaxRank = 10, Cost = 1, RequiredLevel = 8, Description = "+2% Crit Chance per rank" },
	{ Id = "Haste", DisplayName = "Haste", Stat = "CooldownReduction", PerRank = 0.05, MaxRank = 8, Cost = 1, RequiredLevel = 10, Description = "-5% Ability Cooldowns per rank" },
}

--[[ Rarities ]]
-- Tier 1 = worst, Tier 5 = best. Weight = how common. StatMultiplier boosts gear stats.
GameConfig.Rarities = {
	{ Name = "Common", Tier = 1, Weight = 60, StatMultiplier = 1.0, Color = Color3.fromRGB(190, 190, 195), Prefixes = { "Rusted", "Cracked", "Worn" } },
	{ Name = "Uncommon", Tier = 2, Weight = 25, StatMultiplier = 1.3, Color = Color3.fromRGB(70, 230, 100), Prefixes = { "Tempered", "Grim", "Sturdy" } },
	{ Name = "Rare", Tier = 3, Weight = 10, StatMultiplier = 1.7, Color = Color3.fromRGB(50, 140, 255), Prefixes = { "Runed", "Voidtouched", "Ashen" } },
	{ Name = "Epic", Tier = 4, Weight = 4, StatMultiplier = 2.3, Color = Color3.fromRGB(175, 60, 255), Prefixes = { "Abyssal", "Soulbound", "Shattered" } },
	{ Name = "Legendary", Tier = 5, Weight = 1, StatMultiplier = 3.2, Color = Color3.fromRGB(255, 170, 30), Prefixes = { "Realmbreaker's", "Godslayer's", "Eternal" } },
}

--[[ Gear Slots ]]
-- Each slot boosts one stat. Value = (BaseValue + ValuePerFloor * floor) * rarity StatMultiplier
GameConfig.SlotOrder = { "Weapon", "Armor", "Trinket" }
GameConfig.ItemSlots = {
	Weapon = { Stat = "Damage", BaseValue = 3, ValuePerFloor = 0.6, Names = { "Blade", "Cleaver", "Scythe", "Warhammer", "Glaive" } },
	Armor = { Stat = "MaxHealth", BaseValue = 15, ValuePerFloor = 4, Names = { "Plate", "Hauberk", "Shroud", "Carapace", "Mantle" } },
	Trinket = { Stat = "CritChance", BaseValue = 0.02, ValuePerFloor = 0.002, Names = { "Sigil", "Relic", "Eye", "Shard", "Talisman" } },
}

--[[ Loot Drops ]]
GameConfig.Loot = {
	GearDropChance = 0.3,                    -- chance a normal enemy drops gear
	BossGearDrops = 3, BossMinimumTier = 3,  -- bosses always drop 3 items, all Rare or better
	LuckPerFloor = 0.02,   -- deeper floors roll better rarities
	MagnetDelay = 1.2,     -- seconds before a drop flies to its owner
	DropLifetime = 30,     -- seconds before an uncollected drop vanishes
}

--[[ Reward Pulse (the dopamine clock) ]]
GameConfig.Rewards = {
	PulseInterval = 30,        -- every 30 s in the dungeon the player gets SOMETHING
	PulseGearChance = 0.4,     -- chance the pulse is gear instead of XP + shards
	PulseXPPercent = 0.2,      -- bonus XP = 20% of what the current level needs
	PulseShardsBase = 5, PulseShardsPerFloor = 2,
	FloorClearXPPercent = 0.3, FloorClearShards = 15,
}

--[[ Auto-Party ]]
-- Players within ShareRadius of a kill get XPShareMultiplier of its XP (killer gets 100%).
GameConfig.Party = { ShareRadius = 80, XPShareMultiplier = 0.6 }

--[[ Dungeon & Floors ]]
GameConfig.Dungeon = {
	ArenaCenter = Vector3.new(0, 500, 0),         -- floating far above the lobby
	ArenaSize = 160, WallHeight = 40,             -- studs
	LobbyPortalPosition = Vector3.new(0, 4, -40), -- portal the lobby players walk into
	BaseEnemiesPerFloor = 4, ExtraEnemiesPerFloor = 0.75, MaxEnemiesPerFloor = 18,
	BossEveryFloors = 5,
	HealthScalingPerFloor = 0.2, DamageScalingPerFloor = 0.1, -- +20% enemy health, +10% damage per floor
	RewardScalingPerFloor = 0.15, -- +15% XP and shards per floor
	SpawnStagger = 0.4, NextFloorDelay = 4, -- seconds between enemy spawns / between floors
}

--[[ Enemy AI ]]
-- AggroRange: enemies ignore players farther away. PathRefreshInterval: seconds between path
-- recalculations. DirectChaseDistance: closer than this, walk straight at the target.
GameConfig.EnemyAI = { AggroRange = 120, PathRefreshInterval = 0.5, DirectChaseDistance = 14 }

--[[ Enemy Types ]]
GameConfig.Enemies = {
	{ Id = "Husk", DisplayName = "Hollow Husk", MinFloor = 1, Weight = 50, Health = 40, Damage = 8, WalkSpeed = 12, AttackRange = 5, AttackCooldown = 1.2, XP = 12, Shards = 2, Scale = 1.0, BodyColor = Color3.fromRGB(45, 42, 50), GlowColor = Color3.fromRGB(255, 60, 60) },
	{ Id = "Ghoul", DisplayName = "Crackmaw Ghoul", MinFloor = 2, Weight = 35, Health = 30, Damage = 6, WalkSpeed = 18, AttackRange = 5, AttackCooldown = 0.8, XP = 14, Shards = 2, Scale = 0.9, BodyColor = Color3.fromRGB(35, 45, 40), GlowColor = Color3.fromRGB(80, 255, 120) },
	{ Id = "Brute", DisplayName = "Riftbound Brute", MinFloor = 4, Weight = 20, Health = 130, Damage = 18, WalkSpeed = 9, AttackRange = 7, AttackCooldown = 1.8, XP = 30, Shards = 5, Scale = 1.6, BodyColor = Color3.fromRGB(55, 35, 30), GlowColor = Color3.fromRGB(255, 140, 0) },
	{ Id = "Wraith", DisplayName = "Void Wraith", MinFloor = 7, Weight = 20, Health = 60, Damage = 14, WalkSpeed = 15, AttackRange = 6, AttackCooldown = 1.0, XP = 25, Shards = 4, Scale = 1.1, BodyColor = Color3.fromRGB(25, 20, 40), GlowColor = Color3.fromRGB(170, 70, 255) },
}

-- Boss spawns alone on every BossEveryFloors floor (5, 10, 15...)
GameConfig.Boss = { Id = "Warden", DisplayName = "Breach Warden", MinFloor = 1, Weight = 0, Health = 650, Damage = 25, WalkSpeed = 13, AttackRange = 9, AttackCooldown = 1.6, XP = 250, Shards = 50, Scale = 2.4, BodyColor = Color3.fromRGB(20, 18, 24), GlowColor = Color3.fromRGB(0, 230, 255) }

--[[ Visual Theme ]]
GameConfig.Theme = {
	FloorColor = Color3.fromRGB(22, 20, 26), WallColor = Color3.fromRGB(14, 12, 18),
	-- Neon crack colors cycle each floor so every floor feels new
	CrackColors = { Color3.fromRGB(255, 40, 80), Color3.fromRGB(150, 60, 255), Color3.fromRGB(0, 230, 255),
		Color3.fromRGB(255, 140, 0), Color3.fromRGB(60, 255, 120) },
}

--[[ GUI Style ]]
GameConfig.UI = {
	BackgroundColor = Color3.fromRGB(12, 10, 16), PanelColor = Color3.fromRGB(24, 20, 30),
	TextColor = Color3.fromRGB(235, 230, 240), HealthColor = Color3.fromRGB(220, 40, 60),
	XPColor = Color3.fromRGB(130, 70, 255), ShardColor = Color3.fromRGB(0, 230, 255),
	Font = Enum.Font.GothamBold,
	TweenTime = 0.25,           -- default GUI tween length
	LootPopupDuration = 3,      -- seconds a loot card stays on screen
	NotifyDuration = 2.5,       -- seconds a toast stays on screen
}

--[[ Security ]]
-- Per player, per remote. Requests above this rate are ignored by the server.
GameConfig.Security = { MaxRequestsPerSecond = 12 }

--[[ Helper Functions ]]
-- Returns a remote from ReplicatedStorage > RemoteEvents (works on server and client)
function GameConfig.GetRemote(remoteName)
	local remoteFolder = ReplicatedStorage:WaitForChild(GameConfig.RemoteFolderName, 10)
	assert(remoteFolder, "REALM BREACH: ReplicatedStorage > RemoteEvents folder is missing")
	local remote = remoteFolder:WaitForChild(remoteName, 10)
	assert(remote, "REALM BREACH: missing remote '" .. remoteName .. "' in RemoteEvents")
	return remote
end

-- Finds a child by name or creates it. Never yields, so two scripts can't create duplicates.
local function findOrCreate(parent, className, childName)
	local child = parent:FindFirstChild(childName)
	if not child then
		child = Instance.new(className)
		child.Name = childName
		child.Parent = parent
	end
	return child
end

-- Returns a server-only BindableEvent. Never call this from the client.
function GameConfig.GetServerSignal(signalName)
	assert(RunService:IsServer(), "REALM BREACH: server signals are server-only")
	local signalFolder = findOrCreate(game:GetService("ServerStorage"), "Folder", GameConfig.ServerSignalFolderName)
	return findOrCreate(signalFolder, "BindableEvent", signalName)
end

-- XP needed to go from `level` to `level + 1`
function GameConfig.GetXPForLevel(level)
	return math.floor(GameConfig.Leveling.BaseXP * GameConfig.Leveling.Growth ^ (level - 1))
end

-- Generic floor multiplier: floor 1 = 1.0, then +perFloor for each floor after
function GameConfig.GetFloorMultiplier(floorNumber, perFloor)
	return 1 + math.max(floorNumber - 1, 0) * perFloor
end

function GameConfig.IsBossFloor(floorNumber)
	return floorNumber % GameConfig.Dungeon.BossEveryFloors == 0
end

function GameConfig.GetEnemyCountForFloor(floorNumber)
	local dungeon = GameConfig.Dungeon
	local count = dungeon.BaseEnemiesPerFloor + math.floor((floorNumber - 1) * dungeon.ExtraEnemiesPerFloor)
	return math.min(count, dungeon.MaxEnemiesPerFloor)
end

-- Neon crack color for a floor (cycles through Theme.CrackColors)
function GameConfig.GetCrackColor(floorNumber)
	local colors = GameConfig.Theme.CrackColors
	return colors[((floorNumber - 1) % #colors) + 1]
end

-- Looks up a rarity by name; falls back to Common for unknown names
function GameConfig.GetRarity(rarityName)
	for _, rarity in ipairs(GameConfig.Rarities) do
		if rarity.Name == rarityName then
			return rarity
		end
	end
	return GameConfig.Rarities[1]
end

-- Looks up a skill tree entry by Id; returns nil for unknown ids
function GameConfig.GetSkill(skillId)
	for _, skill in ipairs(GameConfig.SkillTree) do
		if skill.Id == skillId then
			return skill
		end
	end
	return nil
end

-- Weighted rarity roll. Luck pushes weight toward higher tiers.
-- minimumTier removes every rarity below that tier (used for bosses).
function GameConfig.RollRarity(luckBonus, minimumTier)
	luckBonus = luckBonus or 0
	minimumTier = minimumTier or 1
	-- Build the luck-adjusted weight for every allowed rarity
	local adjustedWeights = {}
	local totalWeight = 0
	for index, rarity in ipairs(GameConfig.Rarities) do
		local weight = 0
		if rarity.Tier >= minimumTier then
			weight = rarity.Weight * (1 + luckBonus * (rarity.Tier - 1))
		end
		adjustedWeights[index] = weight
		totalWeight += weight
	end
	-- Walk the weights until the random roll is used up
	local roll = sharedRandom:NextNumber() * totalWeight
	for index, rarity in ipairs(GameConfig.Rarities) do
		if adjustedWeights[index] > 0 then
			roll -= adjustedWeights[index]
			if roll <= 0 then
				return rarity
			end
		end
	end
	return GameConfig.Rarities[#GameConfig.Rarities]
end

return GameConfig
