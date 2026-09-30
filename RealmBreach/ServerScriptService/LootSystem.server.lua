--[[
	REALM BREACH — LootSystem
	Script Type : Script
	Location    : ServerScriptService > LootSystem
	Rolls gear when enemies die, spawns glowing loot orbs that fly to their owner,
	and runs the 30-second "Breach Cache" reward pulse for everyone in the dungeon.
	Depends on : ReplicatedStorage > GameConfig, ReplicatedStorage > RemoteEvents,
	             ServerScriptService > PlayerData (receives AwardItem / AwardXP / AwardShards)
	Listens to : EnemyKilled, RunEnded
	Fires      : AwardItem, AwardXP, AwardShards, Notify
]]

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")
local HttpService = game:GetService("HttpService")
local CollectionService = game:GetService("CollectionService")

local GameConfig = require(ReplicatedStorage:WaitForChild("GameConfig"))
local LootConfig, RewardConfig = GameConfig.Loot, GameConfig.Rewards

--[[ Remotes & Server Signals ]]
local NotifyRemote = GameConfig.GetRemote(GameConfig.Remotes.Notify)
local Signals = {}
for key, signalName in pairs(GameConfig.ServerSignals) do
	Signals[key] = GameConfig.GetServerSignal(signalName)
end

--[[ State ]]
local random = Random.new()
local activeDrops = {} -- [dropPart] = { Owner, Item, SpawnTime, BasePosition, Speed }
local nextPulseAt = {} -- [player] = server time of their next reward pulse

-- All loot orbs live in one folder so the Explorer stays tidy
local dropFolder = workspace:FindFirstChild("LootDrops") or Instance.new("Folder")
dropFolder.Name = "LootDrops"
dropFolder.Parent = workspace

--[[ Helpers ]]
local function getCurrentFloor()
	return workspace:GetAttribute("CurrentFloor") or 1
end

-- Player luck from the Fortune skill + a bonus for going deeper
local function getLuck(player, floorNumber)
	return (player:GetAttribute("LootLuck") or 0) + floorNumber * LootConfig.LuckPerFloor
end

local function getRootPart(player)
	return player.Character and player.Character:FindFirstChild("HumanoidRootPart")
end

-- Crit chance keeps 3 decimals, every other stat is a whole number
local function roundStat(statName, value)
	if statName == "CritChance" then
		return math.floor(value * 1000 + 0.5) / 1000
	end
	return math.max(1, math.floor(value + 0.5))
end

--[[ Item Generation ]]
-- Builds one random item. The item table format is what PlayerData expects.
local function generateItem(floorNumber, luck, minimumTier)
	local rarity = GameConfig.RollRarity(luck, minimumTier)
	local slotName = GameConfig.SlotOrder[random:NextInteger(1, #GameConfig.SlotOrder)]
	local slot = GameConfig.ItemSlots[slotName]
	local prefix = rarity.Prefixes[random:NextInteger(1, #rarity.Prefixes)]
	local baseName = slot.Names[random:NextInteger(1, #slot.Names)]
	local rawValue = (slot.BaseValue + slot.ValuePerFloor * floorNumber) * rarity.StatMultiplier * random:NextNumber(0.9, 1.1)
	return {
		Id = HttpService:GenerateGUID(false),
		Name = prefix .. " " .. baseName,
		Slot = slotName,
		Stat = slot.Stat,
		Value = roundStat(slot.Stat, rawValue),
		Rarity = rarity.Name,
		Tier = rarity.Tier,
		Floor = floorNumber,
	}
end

--[[ Loot Orbs ]]
-- Gives the item to its owner and removes the orb
local function collectDrop(dropPart)
	local dropInfo = activeDrops[dropPart]
	if not dropInfo then
		return
	end
	activeDrops[dropPart] = nil
	dropPart:Destroy()
	local owner, item = dropInfo.Owner, dropInfo.Item
	if owner.Parent ~= Players then
		return
	end
	Signals.AwardItem:Fire(owner, item)
	-- Epic and Legendary finds are announced to the whole server (bragging rights!)
	if item.Tier >= 4 then
		local rarity = GameConfig.GetRarity(item.Rarity)
		NotifyRemote:FireAllClients(owner.DisplayName .. " found " .. string.upper(item.Rarity) .. " " .. item.Name .. "!", rarity.Color)
	end
end

-- Creates a glowing orb with a light pillar in the rarity's color
local function spawnDrop(owner, item, position)
	local rarity = GameConfig.GetRarity(item.Rarity)
	local orbSize = 1.4 + (rarity.Tier - 1) * 0.25

	local dropPart = Instance.new("Part")
	dropPart.Name = "Loot_" .. item.Rarity
	dropPart.Shape = Enum.PartType.Ball
	dropPart.Size = Vector3.new(orbSize, orbSize, orbSize)
	dropPart.Material = Enum.Material.Neon
	dropPart.Color = rarity.Color
	dropPart.Anchored = true
	dropPart.CanCollide = false
	dropPart.CanTouch = false
	dropPart.CanQuery = false
	dropPart.CFrame = CFrame.new(position)

	-- Glow around the orb
	local light = Instance.new("PointLight")
	light.Color = rarity.Color
	light.Range = 8 + rarity.Tier * 3
	light.Brightness = 2
	light.Parent = dropPart

	-- Vertical light pillar: taller for better rarities so players spot them across the room
	local bottomAttachment = Instance.new("Attachment")
	bottomAttachment.Parent = dropPart
	local topAttachment = Instance.new("Attachment")
	topAttachment.Position = Vector3.new(0, 6 + rarity.Tier * 3, 0)
	topAttachment.Parent = dropPart
	local pillar = Instance.new("Beam")
	pillar.Attachment0 = bottomAttachment
	pillar.Attachment1 = topAttachment
	pillar.Color = ColorSequence.new(rarity.Color)
	pillar.Transparency = NumberSequence.new(0.2, 1)
	pillar.Width0 = 0.6 + rarity.Tier * 0.2
	pillar.Width1 = 0.1
	pillar.LightEmission = 1
	pillar.FaceCamera = true
	pillar.Parent = dropPart

	-- Sparkles for Epic and Legendary
	if rarity.Tier >= 4 then
		local sparkles = Instance.new("ParticleEmitter")
		sparkles.Color = ColorSequence.new(rarity.Color)
		sparkles.LightEmission = 1
		sparkles.Rate = 20
		sparkles.Lifetime = NumberRange.new(0.6, 1.2)
		sparkles.Speed = NumberRange.new(2, 5)
		sparkles.SpreadAngle = Vector2.new(180, 180)
		sparkles.Size = NumberSequence.new(0.3, 0)
		sparkles.Parent = dropPart
	end

	CollectionService:AddTag(dropPart, GameConfig.Tags.LootDrop)
	dropPart:SetAttribute("OwnerUserId", owner.UserId)
	dropPart.Parent = dropFolder
	activeDrops[dropPart] = { Owner = owner, Item = item, SpawnTime = os.clock(), BasePosition = position, Speed = 0 }
end

-- Every frame: orbs bob in place, then home in on their owner
RunService.Heartbeat:Connect(function(deltaTime)
	local now = os.clock()
	for dropPart, dropInfo in pairs(activeDrops) do
		local age = now - dropInfo.SpawnTime
		local owner = dropInfo.Owner
		local rootPart = getRootPart(owner)
		if owner.Parent ~= Players then
			-- Owner left the game
			activeDrops[dropPart] = nil
			dropPart:Destroy()
		elseif age >= LootConfig.DropLifetime or not owner:GetAttribute("InDungeon") then
			-- Never lose loot: if it times out or the run ended, just hand it over
			collectDrop(dropPart)
		elseif age < LootConfig.MagnetDelay or not rootPart then
			-- Idle: spin and bob where it dropped
			local bobOffset = Vector3.new(0, 1.5 + math.sin(age * 4) * 0.4, 0)
			dropPart.CFrame = CFrame.new(dropInfo.BasePosition + bobOffset) * CFrame.Angles(0, age * 3, 0)
		else
			-- Magnet: accelerate toward the owner and collect on arrival
			dropInfo.Speed = math.min(dropInfo.Speed + 120 * deltaTime, 90)
			local toOwner = rootPart.Position - dropPart.Position
			if toOwner.Magnitude <= 3 then
				collectDrop(dropPart)
			else
				local step = math.min(dropInfo.Speed * deltaTime, toOwner.Magnitude)
				dropPart.CFrame = CFrame.new(dropPart.Position + toOwner.Unit * step) * CFrame.Angles(0, age * 6, 0)
			end
		end
	end
end)

--[[ Enemy Drops ]]
-- Normal enemies: GearDropChance for one item. Bosses: several items, Rare or better.
Signals.EnemyKilled.Event:Connect(function(enemyModel, killer)
	if typeof(enemyModel) ~= "Instance" or typeof(killer) ~= "Instance" or not killer:IsA("Player") then
		return
	end
	local pivotOk, enemyPivot = pcall(enemyModel.GetPivot, enemyModel)
	if not pivotOk then
		return
	end
	local floorNumber = enemyModel:GetAttribute("Floor") or getCurrentFloor()
	local isBoss = enemyModel:GetAttribute("IsBoss") == true
	local dropCount, minimumTier = 0, 1
	if isBoss then
		dropCount, minimumTier = LootConfig.BossGearDrops, LootConfig.BossMinimumTier
	elseif random:NextNumber() < LootConfig.GearDropChance then
		dropCount = 1
	end
	local luck = getLuck(killer, floorNumber)
	for _ = 1, dropCount do
		local scatter = Vector3.new(random:NextNumber(-4, 4), 0, random:NextNumber(-4, 4))
		spawnDrop(killer, generateItem(floorNumber, luck, minimumTier), enemyPivot.Position + scatter)
	end
end)

--[[ Reward Pulse (the dopamine clock) ]]
-- Every PulseInterval seconds in the dungeon: either a gear drop or bonus XP + shards
local function giveRewardPulse(player)
	local floorNumber = getCurrentFloor()
	if random:NextNumber() < RewardConfig.PulseGearChance then
		local item = generateItem(floorNumber, getLuck(player, floorNumber), 1)
		local rootPart = getRootPart(player)
		if rootPart then
			spawnDrop(player, item, rootPart.Position + rootPart.CFrame.LookVector * 6)
		else
			Signals.AwardItem:Fire(player, item)
		end
		NotifyRemote:FireClient(player, "BREACH CACHE — " .. string.upper(item.Rarity) .. " gear!", GameConfig.GetRarity(item.Rarity).Color)
	else
		local level = player:GetAttribute("Level") or 1
		local xpAmount = math.floor(GameConfig.GetXPForLevel(level) * RewardConfig.PulseXPPercent)
		local shardAmount = RewardConfig.PulseShardsBase + RewardConfig.PulseShardsPerFloor * floorNumber
		Signals.AwardXP:Fire(player, xpAmount, "RewardPulse")
		Signals.AwardShards:Fire(player, shardAmount)
		NotifyRemote:FireClient(player, "BREACH CACHE — +" .. xpAmount .. " XP  +" .. shardAmount .. " Shards", GameConfig.UI.ShardColor)
	end
end

-- Schedules a player's next pulse. The NextRewardAt attribute lets the GUI show a countdown.
local function schedulePulse(player, serverTime)
	nextPulseAt[player] = serverTime and serverTime + RewardConfig.PulseInterval or nil
	player:SetAttribute("NextRewardAt", nextPulseAt[player])
end

task.spawn(function()
	while true do
		task.wait(0.5)
		local serverTime = workspace:GetServerTimeNow()
		for _, player in ipairs(Players:GetPlayers()) do
			if not player:GetAttribute("InDungeon") then
				if nextPulseAt[player] then
					schedulePulse(player, nil) -- left the dungeon: stop the clock
				end
			elseif not nextPulseAt[player] then
				schedulePulse(player, serverTime) -- run just started: start the clock
			elseif serverTime >= nextPulseAt[player] then
				schedulePulse(player, serverTime)
				giveRewardPulse(player)
			end
		end
	end
end)

--[[ Cleanup ]]
Signals.RunEnded.Event:Connect(function(player)
	if typeof(player) == "Instance" and player:IsA("Player") then
		schedulePulse(player, nil)
	end
end)

Players.PlayerRemoving:Connect(function(player)
	nextPulseAt[player] = nil
end)
