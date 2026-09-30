--[[
	REALM BREACH — EnemySpawner
	Script Type : Script
	Location    : ServerScriptService > EnemySpawner
	Runs the endless dungeon: builds the world at startup, starts a run when a
	player touches the lobby portal, spawns each floor's enemies, detects when
	a floor is cleared, and moves everyone to the next (harder) floor. The
	dungeon is shared, so players who enter together fight as a party.
	Depends on : ReplicatedStorage > GameConfig, ReplicatedStorage > RemoteEvents,
	             EnemySpawner > ArenaBuilder, EnemySpawner > EnemyFactory, EnemySpawner > EnemyAI,
	             ServerScriptService > PlayerData (handles StartRun and FloorCleared)
	Fires      : StartRun, FloorCleared, Notify
	Sets       : workspace attribute "CurrentFloor"
]]

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Debris = game:GetService("Debris")

local GameConfig = require(ReplicatedStorage:WaitForChild("GameConfig"))
local ArenaBuilder = require(script:WaitForChild("ArenaBuilder"))
local EnemyFactory = require(script:WaitForChild("EnemyFactory"))
local EnemyAI = require(script:WaitForChild("EnemyAI"))
local DungeonConfig = GameConfig.Dungeon

--[[ Remotes & Server Signals ]]
local NotifyRemote = GameConfig.GetRemote(GameConfig.Remotes.Notify)
local StartRunSignal = GameConfig.GetServerSignal(GameConfig.ServerSignals.StartRun)
local FloorClearedSignal = GameConfig.GetServerSignal(GameConfig.ServerSignals.FloorCleared)

--[[ State ]]
local random = Random.new()
local aliveEnemies = {}     -- [enemyModel] = true
local currentFloor = 0      -- 0 = nobody is in the dungeon
local isSpawning = false    -- true while a floor's enemies are still arriving
local floorToken = 0        -- changes on every new floor/reset so old spawn loops stop
local portalCooldowns = {}  -- [player] = true for a few seconds after touching the portal

local enemyFolder = workspace:FindFirstChild("Enemies") or Instance.new("Folder")
enemyFolder.Name = "Enemies"
enemyFolder.Parent = workspace
workspace:SetAttribute("CurrentFloor", 1)

--[[ World Setup ]]
ArenaBuilder.SetupLighting()
ArenaBuilder.EnsureLobby()
local portalRift = ArenaBuilder.BuildLobbyPortal()
ArenaBuilder.BuildArena()
ArenaBuilder.PrepareFloor(1)

--[[ Helpers ]]
local function getDungeonPlayers()
	local dungeonPlayers = {}
	for _, player in ipairs(Players:GetPlayers()) do
		if player:GetAttribute("InDungeon") then
			table.insert(dungeonPlayers, player)
		end
	end
	return dungeonPlayers
end

local function notifyDungeon(message, color)
	for _, player in ipairs(getDungeonPlayers()) do
		NotifyRemote:FireClient(player, message, color)
	end
end

-- Weighted random enemy type among the ones allowed on this floor
local function pickEnemyType(floorNumber)
	local candidates, totalWeight = {}, 0
	for _, enemyType in ipairs(GameConfig.Enemies) do
		if enemyType.MinFloor <= floorNumber then
			table.insert(candidates, enemyType)
			totalWeight += enemyType.Weight
		end
	end
	local roll = random:NextNumber() * totalWeight
	for _, enemyType in ipairs(candidates) do
		roll -= enemyType.Weight
		if roll <= 0 then
			return enemyType
		end
	end
	return candidates[#candidates]
end

--[[ Spawning ]]
local function spawnEnemy(enemyType, floorNumber, isBoss)
	local enemyModel = EnemyFactory.Create(enemyType, floorNumber, isBoss)
	local groundPosition = ArenaBuilder.GetEnemySpawnPosition()
	local spawnPosition = groundPosition + Vector3.new(0, EnemyFactory.GetStandingHeight(enemyType) + 0.5, 0)
	local lookTarget = Vector3.new(DungeonConfig.ArenaCenter.X, spawnPosition.Y, DungeonConfig.ArenaCenter.Z)
	enemyModel:PivotTo(CFrame.lookAt(spawnPosition, lookTarget))
	enemyModel.Parent = enemyFolder
	-- Server controls enemy physics (players can't teleport enemies with exploits)
	enemyModel.PrimaryPart:SetNetworkOwner(nil)

	aliveEnemies[enemyModel] = true
	local humanoid = enemyModel:FindFirstChildOfClass("Humanoid")
	humanoid.Died:Connect(function()
		aliveEnemies[enemyModel] = nil
		-- Leave the body for a moment (LootSystem/PlayerData read it), then remove it
		Debris:AddItem(enemyModel, 1.5)
	end)
	EnemyAI.Start(enemyModel)
end

local function clearEnemies()
	for enemyModel in pairs(aliveEnemies) do
		enemyModel:Destroy()
	end
	aliveEnemies = {}
end

--[[ Floors ]]
local function startFloor(floorNumber)
	floorToken += 1
	local myToken = floorToken
	currentFloor = floorNumber
	isSpawning = true
	workspace:SetAttribute("CurrentFloor", floorNumber)
	ArenaBuilder.PrepareFloor(floorNumber)

	local isBossFloor = GameConfig.IsBossFloor(floorNumber)
	if isBossFloor then
		notifyDungeon("BOSS FLOOR " .. floorNumber .. " — " .. GameConfig.Boss.DisplayName .. " awakens!", GameConfig.Boss.GlowColor)
	else
		notifyDungeon("FLOOR " .. floorNumber, GameConfig.GetCrackColor(floorNumber))
	end

	task.spawn(function()
		-- Boss floors: the boss plus two minions. Normal floors: a wave that grows each floor.
		local enemyCount = GameConfig.GetEnemyCountForFloor(floorNumber)
		if isBossFloor then
			spawnEnemy(GameConfig.Boss, floorNumber, true)
			enemyCount = 2
		end
		for _ = 1, enemyCount do
			if floorToken ~= myToken then
				return -- the run was reset while we were spawning
			end
			spawnEnemy(pickEnemyType(floorNumber), floorNumber, false)
			task.wait(DungeonConfig.SpawnStagger)
		end
		if floorToken == myToken then
			isSpawning = false
		end
	end)
end

-- Everyone left or died: wipe the dungeon so the next run starts at floor 1
local function resetDungeon()
	floorToken += 1
	currentFloor = 0
	isSpawning = false
	clearEnemies()
	workspace:SetAttribute("CurrentFloor", 1)
	ArenaBuilder.PrepareFloor(1)
end

-- Kills enemies that fell out of the arena so a floor can never get stuck
local function removeLostEnemies()
	local lowestAllowedY = DungeonConfig.ArenaCenter.Y - 20
	for enemyModel in pairs(aliveEnemies) do
		local rootPart = enemyModel.PrimaryPart
		local humanoid = enemyModel:FindFirstChildOfClass("Humanoid")
		if not rootPart or not enemyModel.Parent or rootPart.Position.Y < lowestAllowedY then
			if humanoid then
				humanoid.Health = 0
			end
			aliveEnemies[enemyModel] = nil
		end
	end
end

--[[ Main Dungeon Loop ]]
task.spawn(function()
	while true do
		task.wait(0.5)
		removeLostEnemies()
		local hasPlayers = #getDungeonPlayers() > 0
		if not hasPlayers then
			if currentFloor ~= 0 then
				resetDungeon()
			end
		elseif currentFloor == 0 then
			startFloor(1)
		elseif not isSpawning and next(aliveEnemies) == nil then
			-- Floor cleared! Reward everyone, breathe, then go deeper
			local clearedFloor = currentFloor
			FloorClearedSignal:Fire(clearedFloor)
			task.wait(DungeonConfig.NextFloorDelay)
			if #getDungeonPlayers() > 0 and currentFloor == clearedFloor then
				startFloor(clearedFloor + 1)
			end
		end
	end
end)

--[[ Lobby Portal ]]
-- Touching the rift starts a run. Anyone entering joins the floor already in progress.
portalRift.Touched:Connect(function(hitPart)
	local player = Players:GetPlayerFromCharacter(hitPart.Parent)
	if not player or player:GetAttribute("InDungeon") or portalCooldowns[player] then
		return
	end
	portalCooldowns[player] = true
	StartRunSignal:Fire(player)
	task.delay(3, function()
		portalCooldowns[player] = nil
	end)
end)

Players.PlayerRemoving:Connect(function(player)
	portalCooldowns[player] = nil
end)
