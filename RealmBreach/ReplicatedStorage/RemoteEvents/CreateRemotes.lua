--[[
	============================================================
	REALM BREACH — CreateRemotes (one-time setup helper)
	Script Type : Command Bar snippet (NOT a script in the game)
	Where       : Roblox Studio > View tab > Command Bar
	------------------------------------------------------------
	Paste this whole block into the Command Bar and press Enter.
	It builds ReplicatedStorage > RemoteEvents with every remote
	the game needs. Safe to run more than once: it only creates
	what is missing and never deletes anything.
	============================================================
]]

local ReplicatedStorage = game:GetService("ReplicatedStorage")

--[[ Folder ]]
local remoteFolder = ReplicatedStorage:FindFirstChild("RemoteEvents")
if not remoteFolder then
	remoteFolder = Instance.new("Folder")
	remoteFolder.Name = "RemoteEvents"
	remoteFolder.Parent = ReplicatedStorage
end

--[[ RemoteEvents ]]
local remoteEventNames = {
	"DealDamage",
	"PlayerDied",
	"LootDropped",
	"UpdateStats",
	"UseAbility",
	"UnlockSkill",
	"Notify",
}
for _, remoteName in ipairs(remoteEventNames) do
	if not remoteFolder:FindFirstChild(remoteName) then
		local remoteEvent = Instance.new("RemoteEvent")
		remoteEvent.Name = remoteName
		remoteEvent.Parent = remoteFolder
	end
end

--[[ RemoteFunctions ]]
if not remoteFolder:FindFirstChild("GetPlayerData") then
	local remoteFunction = Instance.new("RemoteFunction")
	remoteFunction.Name = "GetPlayerData"
	remoteFunction.Parent = remoteFolder
end

print("REALM BREACH: RemoteEvents folder ready with " .. #remoteFolder:GetChildren() .. " remotes")
