--[[
	REALM BREACH — SaveManager
	Script Type : ModuleScript
	Location    : ServerScriptService > PlayerData > SaveManager  (child of the PlayerData Script)
	Loads and saves player data with DataStoreService. Every DataStore call is
	wrapped in pcall and retried. Never saves data that failed to load, so a
	DataStore outage can't wipe anyone's progress.
	Depends on : ReplicatedStorage > GameConfig
	Used by    : ServerScriptService > PlayerData
]]

local DataStoreService = game:GetService("DataStoreService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local GameConfig = require(ReplicatedStorage:WaitForChild("GameConfig"))
local StoreConfig = GameConfig.DataStore

local SaveManager = {}

--[[ Default Data ]]
-- What a brand-new player starts with. Everything in here is saved.
SaveManager.DefaultData = {
	Level = 1, XP = 0, Shards = 0, SkillPoints = 0,
	Skills = {},     -- [skillId] = rank
	Equipped = {},   -- [slotName] = item
	Inventory = {},  -- list of items, oldest first
	HighestFloor = 0, TotalKills = 0,
}

--[[ DataStore Setup ]]
-- GetDataStore errors in Studio if the place was never published, so guard it
local storeOk, playerStore = pcall(function()
	return DataStoreService:GetDataStore(StoreConfig.Name)
end)
if not storeOk then
	warn("[SaveManager] DataStore unavailable (publish the place + enable API access). Saving is OFF.")
	playerStore = nil
end

--[[ Helpers ]]
local function deepCopy(original)
	if type(original) ~= "table" then
		return original
	end
	local copy = {}
	for key, value in pairs(original) do
		copy[key] = deepCopy(value)
	end
	return copy
end

-- Fills in fields missing from old saves so new features never break old data
local function reconcile(data)
	for key, defaultValue in pairs(SaveManager.DefaultData) do
		if data[key] == nil then
			data[key] = deepCopy(defaultValue)
		end
	end
	return data
end

-- Runs a DataStore call inside pcall, retrying a few times before giving up
local function withRetries(callback)
	for attempt = 1, StoreConfig.MaxRetries do
		local success, result = pcall(callback)
		if success then
			return true, result
		end
		warn("[SaveManager] DataStore attempt " .. attempt .. " failed: " .. tostring(result))
		if attempt < StoreConfig.MaxRetries then
			task.wait(StoreConfig.RetryDelay)
		end
	end
	return false, nil
end

local function getKey(player)
	return "Player_" .. player.UserId
end

--[[ Public API ]]
-- Returns (loadedOk, data). data is always a valid table, even when loading failed.
function SaveManager.Load(player)
	if not playerStore then
		return false, reconcile({})
	end
	local success, storedData = withRetries(function()
		return playerStore:GetAsync(getKey(player))
	end)
	local data = type(storedData) == "table" and storedData or {}
	return success, reconcile(data)
end

-- Saves a player's data table. Returns true on success.
function SaveManager.Save(player, data)
	if not playerStore or type(data) ~= "table" then
		return false
	end
	local success = withRetries(function()
		return playerStore:UpdateAsync(getKey(player), function()
			return data
		end)
	end)
	if not success then
		warn("[SaveManager] Could not save data for " .. player.Name)
	end
	return success
end

-- Autosaves every AutosaveInterval and saves everyone on shutdown.
-- savePlayer(player) comes from PlayerData so it can skip profiles that failed to load.
function SaveManager.StartAutosave(savePlayer)
	-- Server shutting down: save everyone and wait until every save finishes
	game:BindToClose(function()
		local pendingSaves = 0
		for _, player in ipairs(Players:GetPlayers()) do
			pendingSaves += 1
			task.spawn(function()
				savePlayer(player)
				pendingSaves -= 1
			end)
		end
		while pendingSaves > 0 do
			task.wait(0.1)
		end
	end)
	-- Periodic autosave
	task.spawn(function()
		while true do
			task.wait(StoreConfig.AutosaveInterval)
			for _, player in ipairs(Players:GetPlayers()) do
				task.spawn(savePlayer, player)
			end
		end
	end)
end

return SaveManager
