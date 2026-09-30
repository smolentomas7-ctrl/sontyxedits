--[[
	REALM BREACH — EnemyFactory
	Script Type : ModuleScript
	Location    : ServerScriptService > EnemySpawner > EnemyFactory  (child of the EnemySpawner Script)
	Builds an enemy model from code: a Humanoid rig with dark stone limbs,
	glowing neon eyes and a chest crack, a floating health bar, and all the
	attributes other scripts read (Damage, XPReward, IsBoss...).
	Depends on : ReplicatedStorage > GameConfig
	Used by    : ServerScriptService > EnemySpawner
]]

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local TweenService = game:GetService("TweenService")
local CollectionService = game:GetService("CollectionService")

local GameConfig = require(ReplicatedStorage:WaitForChild("GameConfig"))
local DungeonConfig, UI = GameConfig.Dungeon, GameConfig.UI

local EnemyFactory = {}

--[[ Body Parts ]]
-- Adds a part positioned relative to the root part and welded to it
local function addBodyPart(model, rootPart, partName, size, offset, color, material)
	local part = Instance.new("Part")
	part.Name = partName
	part.Size = size
	part.Color = color
	part.Material = material or Enum.Material.Slate
	part.CanCollide = false
	part.Massless = true
	part.CFrame = rootPart.CFrame * offset
	part.Parent = model
	local weld = Instance.new("WeldConstraint")
	weld.Part0 = rootPart
	weld.Part1 = part
	weld.Parent = part
	return part
end

--[[ Health Bar ]]
-- Floating name + health bar above the head. The bar tweens down when hit.
local function addHealthBar(head, humanoid, enemyType, isBoss)
	local billboard = Instance.new("BillboardGui")
	billboard.Name = "HealthBar"
	billboard.Size = isBoss and UDim2.fromOffset(240, 44) or UDim2.fromOffset(120, 30)
	billboard.StudsOffset = Vector3.new(0, head.Size.Y + 0.6, 0)
	billboard.AlwaysOnTop = true
	billboard.MaxDistance = isBoss and 200 or 90
	billboard.Parent = head

	local nameLabel = Instance.new("TextLabel")
	nameLabel.Size = UDim2.fromScale(1, 0.5)
	nameLabel.BackgroundTransparency = 1
	nameLabel.Text = enemyType.DisplayName
	nameLabel.TextColor3 = isBoss and enemyType.GlowColor or UI.TextColor
	nameLabel.TextStrokeTransparency = 0.4
	nameLabel.Font = UI.Font
	nameLabel.TextScaled = true
	nameLabel.Parent = billboard

	local barBackground = Instance.new("Frame")
	barBackground.Position = UDim2.fromScale(0, 0.58)
	barBackground.Size = UDim2.fromScale(1, 0.32)
	barBackground.BackgroundColor3 = UI.BackgroundColor
	barBackground.BorderSizePixel = 0
	barBackground.Parent = billboard
	Instance.new("UICorner").Parent = barBackground

	local barFill = Instance.new("Frame")
	barFill.Size = UDim2.fromScale(1, 1)
	barFill.BackgroundColor3 = isBoss and enemyType.GlowColor or UI.HealthColor
	barFill.BorderSizePixel = 0
	barFill.Parent = barBackground
	Instance.new("UICorner").Parent = barFill

	humanoid.HealthChanged:Connect(function(health)
		local ratio = math.clamp(health / math.max(humanoid.MaxHealth, 1), 0, 1)
		TweenService:Create(barFill, TweenInfo.new(UI.TweenTime), { Size = UDim2.fromScale(ratio, 1) }):Play()
	end)
end

--[[ Public API ]]
-- Creates (but does not parent) an enemy scaled to the given floor
function EnemyFactory.Create(enemyType, floorNumber, isBoss)
	local scale = enemyType.Scale
	local bodyColor, glowColor = enemyType.BodyColor, enemyType.GlowColor

	local model = Instance.new("Model")
	model.Name = enemyType.DisplayName
	-- Atomic = the whole enemy streams in at once (never half a body)
	model.ModelStreamingMode = Enum.ModelStreamingMode.Atomic

	-- Root part: invisible collision box the Humanoid moves around
	local rootPart = Instance.new("Part")
	rootPart.Name = "HumanoidRootPart"
	rootPart.Size = Vector3.new(2, 2, 1) * scale
	rootPart.Transparency = 1
	rootPart.CanCollide = true
	rootPart.Parent = model
	model.PrimaryPart = rootPart

	-- Body (front of the enemy faces -Z, which is the root part's LookVector)
	addBodyPart(model, rootPart, "Torso", Vector3.new(2, 2, 1) * scale, CFrame.new(), bodyColor)
	local head = addBodyPart(model, rootPart, "Head", Vector3.new(1.2, 1.2, 1.2) * scale, CFrame.new(0, 1.6 * scale, 0), bodyColor)
	addBodyPart(model, rootPart, "LeftArm", Vector3.new(0.8, 2, 0.8) * scale, CFrame.new(-1.4 * scale, 0, 0), bodyColor)
	addBodyPart(model, rootPart, "RightArm", Vector3.new(0.8, 2, 0.8) * scale, CFrame.new(1.4 * scale, 0, 0), bodyColor)
	addBodyPart(model, rootPart, "LeftLeg", Vector3.new(0.9, 2, 0.9) * scale, CFrame.new(-0.5 * scale, -2 * scale, 0), bodyColor)
	addBodyPart(model, rootPart, "RightLeg", Vector3.new(0.9, 2, 0.9) * scale, CFrame.new(0.5 * scale, -2 * scale, 0), bodyColor)

	-- Glowing neon eyes and a jagged crack across the chest
	local neon = Enum.Material.Neon
	addBodyPart(model, rootPart, "LeftEye", Vector3.new(0.25, 0.15, 0.1) * scale, CFrame.new(-0.3 * scale, 1.7 * scale, -0.62 * scale), glowColor, neon)
	addBodyPart(model, rootPart, "RightEye", Vector3.new(0.25, 0.15, 0.1) * scale, CFrame.new(0.3 * scale, 1.7 * scale, -0.62 * scale), glowColor, neon)
	addBodyPart(model, rootPart, "ChestCrack", Vector3.new(0.2, 1.5, 0.1) * scale, CFrame.new(0, 0, -0.52 * scale) * CFrame.Angles(0, 0, 0.4), glowColor, neon)
	addBodyPart(model, rootPart, "ChestCrack2", Vector3.new(0.15, 0.8, 0.1) * scale, CFrame.new(0.3 * scale, -0.4 * scale, -0.52 * scale) * CFrame.Angles(0, 0, -0.7), glowColor, neon)
	local glow = Instance.new("PointLight")
	glow.Name = "Glow"
	glow.Color = glowColor
	glow.Range = 8 * scale
	glow.Brightness = 1.5
	glow.Parent = rootPart

	-- Humanoid: R15 mode so HipHeight is respected (legs are 2 studs * scale tall)
	local healthMultiplier = GameConfig.GetFloorMultiplier(floorNumber, DungeonConfig.HealthScalingPerFloor)
	local humanoid = Instance.new("Humanoid")
	humanoid.RigType = Enum.HumanoidRigType.R15
	humanoid.HipHeight = 2 * scale
	humanoid.MaxHealth = math.floor(enemyType.Health * healthMultiplier)
	humanoid.Health = humanoid.MaxHealth
	humanoid.WalkSpeed = enemyType.WalkSpeed
	humanoid.DisplayDistanceType = Enum.HumanoidDisplayDistanceType.None
	humanoid.HealthDisplayType = Enum.HumanoidHealthDisplayType.AlwaysOff
	humanoid.Parent = model
	addHealthBar(head, humanoid, enemyType, isBoss)

	-- Attributes read by EnemyAI, CombatServer, PlayerData and LootSystem
	local damageMultiplier = GameConfig.GetFloorMultiplier(floorNumber, DungeonConfig.DamageScalingPerFloor)
	local rewardMultiplier = GameConfig.GetFloorMultiplier(floorNumber, DungeonConfig.RewardScalingPerFloor)
	model:SetAttribute("EnemyId", enemyType.Id)
	model:SetAttribute("Damage", math.floor(enemyType.Damage * damageMultiplier))
	model:SetAttribute("AttackRange", enemyType.AttackRange)
	model:SetAttribute("AttackCooldown", enemyType.AttackCooldown)
	model:SetAttribute("XPReward", math.floor(enemyType.XP * rewardMultiplier))
	model:SetAttribute("ShardReward", math.floor(enemyType.Shards * rewardMultiplier))
	model:SetAttribute("IsBoss", isBoss == true)
	model:SetAttribute("Floor", floorNumber)
	model:SetAttribute("Scale", scale)
	CollectionService:AddTag(model, GameConfig.Tags.Enemy)

	return model
end

-- Height of the root part's center above the floor (legs + half the root box)
function EnemyFactory.GetStandingHeight(enemyType)
	return 3 * enemyType.Scale
end

return EnemyFactory
