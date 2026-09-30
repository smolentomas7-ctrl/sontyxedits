--[[
	REALM BREACH — PlayerData
	Script Type : Script
	Location    : ServerScriptService > PlayerData
	Owns every player's profile: saved data, lives, run state and final stats.
	Publishes stats as Player attributes (read by other server scripts) and
	through the UpdateStats remote (read by the GUI).
	Depends on : ReplicatedStorage > GameConfig, ReplicatedStorage > RemoteEvents,
	             PlayerData > SaveManager, PlayerData > StatCalculator
	Listens to : EnemyKilled, AwardXP, AwardShards, AwardItem, FloorCleared, StartRun
	Fires      : RunEnded, UpdateStats, PlayerDied, LootDropped, Notify
]]

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Debris = game:GetService("Debris")

local GameConfig = require(ReplicatedStorage:WaitForChild("GameConfig"))
local SaveManager = require(script:WaitForChild("SaveManager"))
local StatCalculator = require(script:WaitForChild("StatCalculator"))
local PlayerConfig, UI = GameConfig.Player, GameConfig.UI

--[[ Remotes & Server Signals ]]
local Remotes, Signals = {}, {}
for key, remoteName in pairs(GameConfig.Remotes) do
	Remotes[key] = GameConfig.GetRemote(remoteName)
end
for key, signalName in pairs(GameConfig.ServerSignals) do
	Signals[key] = GameConfig.GetServerSignal(signalName)
end

--[[ State ]]
local profiles = {}    -- [player] = { Data, Stats, CanSave, Lives, InDungeon, Dead }
local requestLog = {}  -- [player] = { [remoteName] = { WindowStart, Count } }
local random = Random.new()
Players.RespawnTime = PlayerConfig.RespawnDelay

--[[ Helpers ]]
local function notify(player, message, color)
	Remotes.Notify:FireClient(player, message, color or UI.TextColor)
end

local function getHumanoid(player)
	return player.Character and player.Character:FindFirstChildOfClass("Humanoid")
end

-- Returns true if this player is spamming a remote (more than the allowed rate per second)
local function isRateLimited(player, remoteName)
	local log = requestLog[player]
	if not log then
		return true
	end
	local now = os.clock()
	local entry = log[remoteName]
	if not entry or now - entry.WindowStart >= 1 then
		entry = { WindowStart = now, Count = 0 }
		log[remoteName] = entry
	end
	entry.Count += 1
	return entry.Count > GameConfig.Security.MaxRequestsPerSecond
end

local function savePlayer(player)
	local profile = profiles[player]
	-- Never save if loading failed, or a blank file would overwrite real progress
	if profile and profile.CanSave then
		SaveManager.Save(player, profile.Data)
	end
end

--[[ Stats Publishing ]]
-- Recalculates stats, writes them to attributes + the character, and tells the client
local function refreshPlayer(player)
	local profile = profiles[player]
	if not profile then
		return
	end
	local stats = StatCalculator.Calculate(profile.Data)
	profile.Stats = stats
	-- Attributes are readable by every server script (CombatServer, LootSystem...)
	for statName, value in pairs(stats) do
		player:SetAttribute(statName, value)
	end
	player:SetAttribute("Level", profile.Data.Level)
	player:SetAttribute("Lives", profile.Lives)
	player:SetAttribute("InDungeon", profile.InDungeon)
	-- Apply to the living character, keeping the same health percentage
	local humanoid = getHumanoid(player)
	if humanoid and humanoid.Health > 0 then
		local healthRatio = humanoid.Health / math.max(humanoid.MaxHealth, 1)
		humanoid.MaxHealth = stats.MaxHealth
		humanoid.Health = math.clamp(stats.MaxHealth * healthRatio, 1, stats.MaxHealth)
		humanoid.WalkSpeed = stats.WalkSpeed
	end
	Remotes.UpdateStats:FireClient(player, StatCalculator.BuildSnapshot(profile))
end

--[[ Rewards ]]
local function awardXP(player, amount)
	local profile = profiles[player]
	if not profile or type(amount) ~= "number" or amount <= 0 then
		return
	end
	local oldLevel, newLevel = StatCalculator.ApplyXP(profile.Data, amount)
	refreshPlayer(player)
	if newLevel > oldLevel then
		-- Full heal on level up + announce any abilities that just unlocked
		local humanoid = getHumanoid(player)
		if humanoid and humanoid.Health > 0 then
			humanoid.Health = humanoid.MaxHealth
		end
		notify(player, "LEVEL UP! You are now level " .. newLevel .. "  (+skill point)", UI.XPColor)
		for _, unlock in ipairs(StatCalculator.GetNewAbilities(oldLevel, newLevel)) do
			notify(player, "NEW ABILITY: " .. unlock.Ability.DisplayName .. " [" .. unlock.Key .. "]", unlock.Ability.Color)
		end
	end
end

local function awardShards(player, amount)
	local profile = profiles[player]
	if profile and type(amount) == "number" and amount > 0 then
		profile.Data.Shards += math.floor(amount)
		refreshPlayer(player)
	end
end

local function awardItem(player, item)
	local profile = profiles[player]
	if profile and StatCalculator.IsValidItem(item) then
		local equipped = StatCalculator.AddItem(profile.Data, item)
		refreshPlayer(player)
		Remotes.LootDropped:FireClient(player, item, equipped)
	end
end

--[[ Death & Spawning ]]
local function onDied(player)
	local profile = profiles[player]
	if not profile or profile.Dead then
		return
	end
	profile.Dead = true
	if not profile.InDungeon then
		return -- dying in the lobby costs nothing
	end
	profile.Lives -= 1
	local floorReached = workspace:GetAttribute("CurrentFloor") or 1
	local livesLeft = math.max(profile.Lives, 0)
	local runOver = livesLeft == 0
	if runOver then
		-- Out of lives: respawn in the lobby with fresh lives for the next run
		profile.InDungeon = false
		profile.Lives = PlayerConfig.StartingLives
		Signals.RunEnded:Fire(player, floorReached)
		task.spawn(savePlayer, player)
	end
	Remotes.PlayerDied:FireClient(player, livesLeft, runOver, floorReached)
	refreshPlayer(player)
end

local function onCharacterAdded(player, character)
	local humanoid = character:WaitForChild("Humanoid")
	character:WaitForChild("HumanoidRootPart")
	local profile = profiles[player]
	if not profile then
		return
	end
	profile.Dead = false
	humanoid.MaxHealth = profile.Stats.MaxHealth
	humanoid.Health = profile.Stats.MaxHealth
	humanoid.WalkSpeed = profile.Stats.WalkSpeed
	humanoid.Died:Connect(function()
		onDied(player)
	end)
	if profile.InDungeon then
		task.wait() -- let Roblox finish placing the character at its SpawnLocation first
		local offset = Vector3.new(random:NextNumber(-20, 20), 5, random:NextNumber(-20, 20))
		character:PivotTo(CFrame.new(GameConfig.Dungeon.ArenaCenter + offset))
		-- Short spawn shield so players aren't killed the instant they land
		local shield = Instance.new("ForceField")
		shield.Parent = character
		Debris:AddItem(shield, PlayerConfig.SpawnShieldTime)
	end
end

--[[ Player Join / Leave ]]
local function onPlayerAdded(player)
	local loadedOk, data = SaveManager.Load(player)
	if not player.Parent then
		return -- left while we were loading
	end
	local profile = { Data = data, CanSave = loadedOk, Lives = PlayerConfig.StartingLives, InDungeon = false, Dead = false }
	profile.Stats = StatCalculator.Calculate(data)
	profiles[player] = profile
	requestLog[player] = {}
	player.CharacterAdded:Connect(function(character)
		onCharacterAdded(player, character)
	end)
	if player.Character then
		task.spawn(onCharacterAdded, player, player.Character)
	end
	refreshPlayer(player)
	if loadedOk then
		print("[PlayerData] Loaded " .. player.Name .. " — level " .. data.Level)
	else
		notify(player, "Save data unavailable — progress this session will NOT be saved.", UI.HealthColor)
	end
end

Players.PlayerAdded:Connect(onPlayerAdded)
Players.PlayerRemoving:Connect(function(player)
	savePlayer(player)
	profiles[player] = nil
	requestLog[player] = nil
end)
for _, player in ipairs(Players:GetPlayers()) do
	task.spawn(onPlayerAdded, player)
end

SaveManager.StartAutosave(savePlayer)

--[[ Server Signal Listeners ]]
Signals.AwardXP.Event:Connect(awardXP)
Signals.AwardShards.Event:Connect(awardShards)
Signals.AwardItem.Event:Connect(awardItem)

-- Kill rewards: killer gets full XP + shards, nearby dungeon players get a party share
Signals.EnemyKilled.Event:Connect(function(enemyModel, killer)
	if typeof(enemyModel) ~= "Instance" then
		return
	end
	local xpReward = enemyModel:GetAttribute("XPReward") or 0
	local shardReward = enemyModel:GetAttribute("ShardReward") or 0
	if killer and profiles[killer] then
		profiles[killer].Data.TotalKills += 1
		profiles[killer].Data.Shards += math.floor(shardReward)
		awardXP(killer, xpReward)
	end
	local pivotOk, enemyPivot = pcall(enemyModel.GetPivot, enemyModel)
	if not pivotOk then
		return
	end
	for otherPlayer, profile in pairs(profiles) do
		local rootPart = otherPlayer.Character and otherPlayer.Character:FindFirstChild("HumanoidRootPart")
		local isNearby = rootPart and (rootPart.Position - enemyPivot.Position).Magnitude <= GameConfig.Party.ShareRadius
		if otherPlayer ~= killer and profile.InDungeon and isNearby then
			awardXP(otherPlayer, xpReward * GameConfig.Party.XPShareMultiplier)
		end
	end
end)

-- Floor cleared: bonus XP + shards for everyone in the dungeon
Signals.FloorCleared.Event:Connect(function(floorNumber)
	local shardBonus = GameConfig.Rewards.FloorClearShards * GameConfig.GetFloorMultiplier(floorNumber, GameConfig.Dungeon.RewardScalingPerFloor)
	for player, profile in pairs(profiles) do
		if profile.InDungeon then
			local data = profile.Data
			data.HighestFloor = math.max(data.HighestFloor, floorNumber)
			data.Shards += math.floor(shardBonus)
			notify(player, "FLOOR " .. floorNumber .. " CLEARED!", GameConfig.GetCrackColor(floorNumber))
			awardXP(player, GameConfig.GetXPForLevel(data.Level) * GameConfig.Rewards.FloorClearXPPercent)
		end
	end
end)

-- Lobby portal touched: start a new run with full lives
Signals.StartRun.Event:Connect(function(player)
	local profile = profiles[player]
	if not profile or profile.InDungeon then
		return
	end
	profile.Lives = PlayerConfig.StartingLives
	profile.InDungeon = true
	refreshPlayer(player)
	notify(player, "THE BREACH OPENS — " .. profile.Lives .. " lives. Survive.", UI.HealthColor)
	player:LoadCharacter()
end)

--[[ Client Remotes ]]
Remotes.GetPlayerData.OnServerInvoke = function(player)
	if isRateLimited(player, "GetPlayerData") or not profiles[player] then
		return nil
	end
	return StatCalculator.BuildSnapshot(profiles[player])
end

-- Skill tree: the client only asks, the server checks every rule
Remotes.UnlockSkill.OnServerEvent:Connect(function(player, skillId)
	local profile = profiles[player]
	if not profile or isRateLimited(player, "UnlockSkill") or type(skillId) ~= "string" then
		return
	end
	local success, message = StatCalculator.TryUnlockSkill(profile.Data, skillId)
	if success then
		refreshPlayer(player)
	end
	notify(player, message, success and UI.XPColor or UI.HealthColor)
end)
