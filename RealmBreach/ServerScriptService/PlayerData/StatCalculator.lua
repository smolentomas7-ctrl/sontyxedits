--[[
	REALM BREACH — StatCalculator
	Script Type : ModuleScript
	Location    : ServerScriptService > PlayerData > StatCalculator  (child of the PlayerData Script)
	Pure game-rule math on a player's data table: final stats, leveling,
	gear auto-equip and skill tree purchases. No DataStore, no remotes.
	Depends on : ReplicatedStorage > GameConfig
	Used by    : ServerScriptService > PlayerData
]]

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local GameConfig = require(ReplicatedStorage:WaitForChild("GameConfig"))
local PlayerConfig, CombatConfig = GameConfig.Player, GameConfig.Combat

local StatCalculator = {}

--[[ Final Stats ]]
-- Combines level, skill tree and equipped gear into the numbers the game uses
function StatCalculator.Calculate(data)
	local skillBonus, gearBonus = {}, {}
	for _, skill in ipairs(GameConfig.SkillTree) do
		local rank = data.Skills[skill.Id] or 0
		skillBonus[skill.Stat] = (skillBonus[skill.Stat] or 0) + rank * skill.PerRank
	end
	for _, item in pairs(data.Equipped) do
		gearBonus[item.Stat] = (gearBonus[item.Stat] or 0) + item.Value
	end

	local levelsGained = data.Level - 1
	local baseHealth = PlayerConfig.BaseMaxHealth + PlayerConfig.HealthPerLevel * levelsGained + (gearBonus.MaxHealth or 0)
	local baseDamage = PlayerConfig.BaseDamage + PlayerConfig.DamagePerLevel * levelsGained + (gearBonus.Damage or 0)
	local critChance = CombatConfig.BaseCritChance + (gearBonus.CritChance or 0) + (skillBonus.CritChance or 0)

	return {
		MaxHealth = math.floor(baseHealth * (1 + (skillBonus.MaxHealthPercent or 0))),
		Damage = math.floor(baseDamage * (1 + (skillBonus.DamagePercent or 0))),
		CritChance = math.min(critChance, CombatConfig.MaxCritChance),
		Lifesteal = math.min(skillBonus.Lifesteal or 0, CombatConfig.MaxLifesteal),
		LootLuck = skillBonus.LootLuck or 0,
		CooldownReduction = skillBonus.CooldownReduction or 0,
		WalkSpeed = PlayerConfig.BaseWalkSpeed + (skillBonus.WalkSpeed or 0),
	}
end

--[[ Leveling ]]
-- Adds XP and levels up as many times as it allows. Returns (oldLevel, newLevel).
function StatCalculator.ApplyXP(data, amount)
	local oldLevel = data.Level
	data.XP += math.floor(amount)
	while data.Level < GameConfig.Leveling.MaxLevel and data.XP >= GameConfig.GetXPForLevel(data.Level) do
		data.XP -= GameConfig.GetXPForLevel(data.Level)
		data.Level += 1
		data.SkillPoints += PlayerConfig.SkillPointsPerLevel
	end
	return oldLevel, data.Level
end

-- Abilities whose unlock level was passed between oldLevel and newLevel
function StatCalculator.GetNewAbilities(oldLevel, newLevel)
	local unlocked = {}
	for _, key in ipairs(GameConfig.AbilityKeys) do
		local ability = GameConfig.Abilities[key]
		if ability.UnlockLevel > oldLevel and ability.UnlockLevel <= newLevel then
			table.insert(unlocked, { Key = key, Ability = ability })
		end
	end
	return unlocked
end

--[[ Gear ]]
local function isEquipped(data, item)
	local equippedItem = data.Equipped[item.Slot]
	return equippedItem ~= nil and equippedItem.Id == item.Id
end

-- Checks an item table has every field the game relies on
function StatCalculator.IsValidItem(item)
	return type(item) == "table"
		and GameConfig.ItemSlots[item.Slot] ~= nil
		and type(item.Id) == "string"
		and type(item.Name) == "string"
		and type(item.Stat) == "string"
		and type(item.Value) == "number"
end

-- Stores an item and auto-equips it if it beats the current one. Returns true if equipped.
function StatCalculator.AddItem(data, item)
	local current = data.Equipped[item.Slot]
	local equipNow = current == nil or item.Value > current.Value
	if equipNow then
		data.Equipped[item.Slot] = item
	end
	table.insert(data.Inventory, item)

	-- Inventory full: remove the oldest item that is not equipped
	while #data.Inventory > PlayerConfig.MaxInventory do
		local removedOne = false
		for index, storedItem in ipairs(data.Inventory) do
			if not isEquipped(data, storedItem) then
				table.remove(data.Inventory, index)
				removedOne = true
				break
			end
		end
		if not removedOne then
			break
		end
	end
	return equipNow
end

--[[ Skill Tree ]]
-- Validates and buys one rank. Returns (success, message).
function StatCalculator.TryUnlockSkill(data, skillId)
	local skill = GameConfig.GetSkill(skillId)
	if not skill then
		return false, "Unknown skill"
	end
	local rank = data.Skills[skill.Id] or 0
	if rank >= skill.MaxRank then
		return false, skill.DisplayName .. " is already maxed"
	elseif data.Level < skill.RequiredLevel then
		return false, skill.DisplayName .. " requires level " .. skill.RequiredLevel
	elseif data.SkillPoints < skill.Cost then
		return false, "Not enough skill points"
	end
	data.SkillPoints -= skill.Cost
	data.Skills[skill.Id] = rank + 1
	return true, skill.DisplayName .. " upgraded to rank " .. (rank + 1)
end

--[[ Client Snapshot ]]
-- Everything the client needs to draw the GUI, built from a PlayerData profile
function StatCalculator.BuildSnapshot(profile)
	local data = profile.Data
	return {
		Level = data.Level, XP = data.XP, XPNeeded = GameConfig.GetXPForLevel(data.Level),
		Shards = data.Shards, SkillPoints = data.SkillPoints, Skills = data.Skills,
		Equipped = data.Equipped, InventoryCount = #data.Inventory,
		HighestFloor = data.HighestFloor, TotalKills = data.TotalKills,
		Lives = profile.Lives, InDungeon = profile.InDungeon,
		CurrentFloor = workspace:GetAttribute("CurrentFloor") or 1,
		Stats = profile.Stats,
	}
end

return StatCalculator
