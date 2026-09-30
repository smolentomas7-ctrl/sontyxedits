--[[
	REALM BREACH — ArenaBuilder
	Script Type : ModuleScript
	Location    : ServerScriptService > EnemySpawner > ArenaBuilder  (child of the EnemySpawner Script)
	Builds the world by code so you don't have to: dark lighting, the lobby
	portal, and the dungeon arena with glowing neon cracks. Each floor gets
	new crack colors and a new pillar layout.
	Depends on : ReplicatedStorage > GameConfig
	Used by    : ServerScriptService > EnemySpawner
]]

local Lighting = game:GetService("Lighting")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local GameConfig = require(ReplicatedStorage:WaitForChild("GameConfig"))
local DungeonConfig, Theme = GameConfig.Dungeon, GameConfig.Theme

local ArenaBuilder = {}
local random = Random.new()
local crackParts = {}   -- every neon crack, recolored each floor
local arenaLamps = {}   -- ceiling lamps, recolored each floor
local pillarFolder = nil

--[[ Helpers ]]
-- Creates an anchored part, applies properties, then parents it (parent last = faster)
local function makePart(parent, properties)
	local part = Instance.new("Part")
	part.Anchored = true
	part.TopSurface = Enum.SurfaceType.Smooth
	part.BottomSurface = Enum.SurfaceType.Smooth
	for propertyName, value in pairs(properties) do
		part[propertyName] = value
	end
	part.Parent = parent
	return part
end

-- A glowing strip that never blocks movement or clicks
local function makeCrack(parent, size, cframe)
	local crack = makePart(parent, {
		Name = "Crack", Size = size, CFrame = cframe, Material = Enum.Material.Neon,
		Color = Theme.CrackColors[1], CanCollide = false, CanQuery = false, CanTouch = false,
	})
	table.insert(crackParts, crack)
	return crack
end

local function findOrCreate(parent, className, childName)
	local child = parent:FindFirstChild(childName) or Instance.new(className)
	child.Name = childName
	child.Parent = parent
	return child
end

--[[ Lighting ]]
-- Dark, foggy night with bloom so neon cracks really glow
function ArenaBuilder.SetupLighting()
	Lighting.ClockTime = 0
	Lighting.Brightness = 1
	Lighting.Ambient = Color3.fromRGB(25, 20, 30)
	Lighting.OutdoorAmbient = Color3.fromRGB(40, 34, 50)
	Lighting.EnvironmentDiffuseScale = 0.2
	Lighting.EnvironmentSpecularScale = 0.5

	local atmosphere = findOrCreate(Lighting, "Atmosphere", "Atmosphere")
	atmosphere.Density = 0.4
	atmosphere.Haze = 2
	atmosphere.Glare = 0
	atmosphere.Color = Color3.fromRGB(30, 22, 40)
	atmosphere.Decay = Color3.fromRGB(10, 8, 14)

	local bloom = findOrCreate(Lighting, "BloomEffect", "RealmBloom")
	bloom.Intensity = 1.2
	bloom.Size = 30
	bloom.Threshold = 0.9

	local colorCorrection = findOrCreate(Lighting, "ColorCorrectionEffect", "RealmGrade")
	colorCorrection.Contrast = 0.15
	colorCorrection.Saturation = -0.1
	colorCorrection.TintColor = Color3.fromRGB(235, 225, 255)
end

--[[ Lobby ]]
-- Makes sure the lobby has ground and a SpawnLocation (for places without a Baseplate)
function ArenaBuilder.EnsureLobby()
	for _, descendant in ipairs(workspace:GetDescendants()) do
		if descendant:IsA("SpawnLocation") then
			return
		end
	end
	makePart(workspace, { Name = "LobbyFloor", Size = Vector3.new(160, 2, 160), Position = Vector3.new(0, -1, 0), Material = Enum.Material.Slate, Color = Theme.FloorColor })
	local spawnLocation = Instance.new("SpawnLocation")
	spawnLocation.Anchored = true
	spawnLocation.Size = Vector3.new(12, 1, 12)
	spawnLocation.Position = Vector3.new(0, 0.5, 0)
	spawnLocation.Neutral = true
	spawnLocation.Parent = workspace
end

-- Builds the glowing gateway in the lobby. Returns the rift part players touch to enter.
function ArenaBuilder.BuildLobbyPortal()
	local portalModel = Instance.new("Model")
	portalModel.Name = "BreachPortal"
	portalModel.ModelStreamingMode = Enum.ModelStreamingMode.Persistent
	local base = DungeonConfig.LobbyPortalPosition
	local glowColor = Theme.CrackColors[1]
	local stone = { Material = Enum.Material.Slate, Color = Theme.WallColor }

	-- Stone frame: two posts and a lintel
	for _, side in ipairs({ -1, 1 }) do
		makePart(portalModel, { Name = "Post", Size = Vector3.new(2, 16, 2), Position = base + Vector3.new(side * 7, 4, 0), Material = stone.Material, Color = stone.Color })
	end
	makePart(portalModel, { Name = "Lintel", Size = Vector3.new(16, 2, 2), Position = base + Vector3.new(0, 13, 0), Material = stone.Material, Color = stone.Color })

	-- The glowing rift itself (touching it starts a run)
	local rift = makePart(portalModel, {
		Name = "Rift", Size = Vector3.new(12, 12, 2), Position = base + Vector3.new(0, 4, 0),
		Material = Enum.Material.Neon, Color = glowColor, Transparency = 0.25, CanCollide = false,
	})
	local light = Instance.new("PointLight")
	light.Color = glowColor
	light.Range = 30
	light.Brightness = 3
	light.Parent = rift

	-- Floating label above the portal
	local billboard = Instance.new("BillboardGui")
	billboard.Size = UDim2.fromOffset(300, 60)
	billboard.StudsOffset = Vector3.new(0, 10, 0)
	billboard.MaxDistance = 150
	billboard.Parent = rift
	local label = Instance.new("TextLabel")
	label.Size = UDim2.fromScale(1, 1)
	label.BackgroundTransparency = 1
	label.Text = "ENTER THE BREACH"
	label.TextColor3 = glowColor
	label.TextStrokeTransparency = 0.3
	label.Font = GameConfig.UI.Font
	label.TextScaled = true
	label.Parent = billboard

	portalModel.Parent = workspace
	return rift
end

--[[ Arena ]]
-- Builds the enclosed dungeon room high above the lobby (once, at server start)
function ArenaBuilder.BuildArena()
	local dungeonModel = Instance.new("Model")
	dungeonModel.Name = "Dungeon"
	-- Persistent = always streamed to every player, so nobody lands on missing ground
	dungeonModel.ModelStreamingMode = Enum.ModelStreamingMode.Persistent
	local center, size, height = DungeonConfig.ArenaCenter, DungeonConfig.ArenaSize, DungeonConfig.WallHeight
	local half = size / 2

	-- Floor (its top surface sits exactly at ArenaCenter.Y) and ceiling
	makePart(dungeonModel, { Name = "Floor", Size = Vector3.new(size, 4, size), Position = center - Vector3.new(0, 2, 0), Material = Enum.Material.Slate, Color = Theme.FloorColor })
	makePart(dungeonModel, { Name = "Ceiling", Size = Vector3.new(size, 4, size), Position = center + Vector3.new(0, height + 2, 0), Material = Enum.Material.Slate, Color = Theme.WallColor })

	-- Four walls
	local walls = {
		{ Offset = Vector3.new(half + 2, 0, 0), Size = Vector3.new(4, height, size + 8) },
		{ Offset = Vector3.new(-half - 2, 0, 0), Size = Vector3.new(4, height, size + 8) },
		{ Offset = Vector3.new(0, 0, half + 2), Size = Vector3.new(size + 8, height, 4) },
		{ Offset = Vector3.new(0, 0, -half - 2), Size = Vector3.new(size + 8, height, 4) },
	}
	for _, wall in ipairs(walls) do
		makePart(dungeonModel, { Name = "Wall", Size = wall.Size, Position = center + wall.Offset + Vector3.new(0, height / 2, 0), Material = Enum.Material.Slate, Color = Theme.WallColor })
	end

	-- Floor cracks: thin neon strips at random angles
	for _ = 1, 45 do
		local position = center + Vector3.new(random:NextNumber(-half + 4, half - 4), 0.05, random:NextNumber(-half + 4, half - 4))
		local size3 = Vector3.new(random:NextNumber(0.2, 0.6), 0.1, random:NextNumber(6, 22))
		makeCrack(dungeonModel, size3, CFrame.new(position) * CFrame.Angles(0, random:NextNumber(0, math.pi * 2), 0))
	end

	-- Wall cracks: jagged vertical strips on the inside of each wall
	for _ = 1, 28 do
		local sign = random:NextInteger(0, 1) == 0 and -1 or 1
		local y = center.Y + random:NextNumber(2, height - 4)
		local along = random:NextNumber(-half + 4, half - 4)
		local length, tilt = random:NextNumber(4, 14), random:NextNumber(-0.6, 0.6)
		if random:NextInteger(0, 1) == 0 then
			makeCrack(dungeonModel, Vector3.new(0.1, length, 0.4), CFrame.new(center.X + sign * (half - 0.05), y, center.Z + along) * CFrame.Angles(tilt, 0, 0))
		else
			makeCrack(dungeonModel, Vector3.new(0.4, length, 0.1), CFrame.new(center.X + along, y, center.Z + sign * (half - 0.05)) * CFrame.Angles(0, 0, tilt))
		end
	end

	-- Ceiling lamps (tinted to the floor's crack color)
	for _, offset in ipairs({ Vector3.new(-40, 0, -40), Vector3.new(40, 0, -40), Vector3.new(-40, 0, 40), Vector3.new(40, 0, 40), Vector3.zero }) do
		local lamp = makePart(dungeonModel, {
			Name = "Lamp", Size = Vector3.new(4, 0.5, 4), Position = center + offset + Vector3.new(0, height - 0.25, 0),
			Material = Enum.Material.Neon, Color = Theme.CrackColors[1], CanCollide = false, CanQuery = false,
		})
		local light = Instance.new("PointLight")
		light.Range = 60
		light.Brightness = 1.5
		light.Color = lamp.Color
		light.Parent = lamp
		table.insert(arenaLamps, lamp)
	end

	pillarFolder = Instance.new("Folder")
	pillarFolder.Name = "Pillars"
	pillarFolder.Parent = dungeonModel
	dungeonModel.Parent = workspace
end

-- Recolors the arena and rebuilds the pillars so every floor looks different
function ArenaBuilder.PrepareFloor(floorNumber)
	local crackColor = GameConfig.GetCrackColor(floorNumber)
	for _, crack in ipairs(crackParts) do
		crack.Color = crackColor
	end
	for _, lamp in ipairs(arenaLamps) do
		lamp.Color = crackColor
		lamp:FindFirstChildOfClass("PointLight").Color = crackColor
	end

	pillarFolder:ClearAllChildren()
	local center, height = DungeonConfig.ArenaCenter, DungeonConfig.WallHeight
	for _ = 1, random:NextInteger(4, 8) do
		-- Pillars sit in a ring between the player spawn (center) and enemy spawns (edges)
		local angle, distance = random:NextNumber(0, math.pi * 2), random:NextNumber(28, 50)
		local width = random:NextNumber(5, 9)
		local position = center + Vector3.new(math.cos(angle) * distance, height / 2, math.sin(angle) * distance)
		makePart(pillarFolder, { Name = "Pillar", Size = Vector3.new(width, height, width), Position = position, Material = Enum.Material.Slate, Color = Theme.WallColor })
		makePart(pillarFolder, {
			Name = "PillarCrack", Size = Vector3.new(0.5, height * 0.7, width + 0.1), Position = position,
			Material = Enum.Material.Neon, Color = crackColor, CanCollide = false, CanQuery = false, CanTouch = false,
		})
	end
end

-- A random spot near the arena walls, far from where players land
function ArenaBuilder.GetEnemySpawnPosition()
	local angle = random:NextNumber(0, math.pi * 2)
	local distance = random:NextNumber(58, DungeonConfig.ArenaSize / 2 - 8)
	return DungeonConfig.ArenaCenter + Vector3.new(math.cos(angle) * distance, 0, math.sin(angle) * distance)
end

return ArenaBuilder
