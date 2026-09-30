--[[
	REALM BREACH — EnemyAI
	Script Type : ModuleScript
	Location    : ServerScriptService > EnemySpawner > EnemyAI  (child of the EnemySpawner Script)
	Brain for every enemy: finds the nearest player in the dungeon, walks to
	them with PathfindingService, and attacks with a short glowing wind-up
	so players can dodge. Bosses hit everyone around them (ground slam).
	Depends on : ReplicatedStorage > GameConfig, ReplicatedStorage > RemoteEvents
	Used by    : ServerScriptService > EnemySpawner
]]

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local PathfindingService = game:GetService("PathfindingService")

local GameConfig = require(ReplicatedStorage:WaitForChild("GameConfig"))
local AIConfig = GameConfig.EnemyAI
local DealDamageRemote = GameConfig.GetRemote(GameConfig.Remotes.DealDamage)

local EnemyAI = {}
local WIND_UP_TIME = 0.25 -- seconds the enemy glows before its hit lands

--[[ Targeting ]]
-- Returns a living player's character parts, or nil
local function getLivingCharacter(player)
	local character = player.Character
	local humanoid = character and character:FindFirstChildOfClass("Humanoid")
	local rootPart = character and character:FindFirstChild("HumanoidRootPart")
	if humanoid and rootPart and humanoid.Health > 0 then
		return character, humanoid, rootPart
	end
	return nil
end

-- Nearest living player inside the dungeon and within aggro range
local function findNearestTarget(fromPosition)
	local nearestRoot, nearestDistance = nil, AIConfig.AggroRange
	for _, player in ipairs(Players:GetPlayers()) do
		if player:GetAttribute("InDungeon") then
			local _, _, rootPart = getLivingCharacter(player)
			if rootPart then
				local distance = (rootPart.Position - fromPosition).Magnitude
				if distance < nearestDistance then
					nearestRoot, nearestDistance = rootPart, distance
				end
			end
		end
	end
	return nearestRoot, nearestDistance
end

--[[ Attacking ]]
-- Damages one player (ForceField spawn shield blocks it) and shows a red damage number
local function damagePlayer(player, amount)
	local character, humanoid, rootPart = getLivingCharacter(player)
	if not character or character:FindFirstChildOfClass("ForceField") then
		return
	end
	humanoid:TakeDamage(amount)
	-- Args: world position, amount, isCrit, isIncoming (true = damage the player took)
	DealDamageRemote:FireClient(player, rootPart.Position, amount, false, true)
end

local function performAttack(enemyModel, rootPart, humanoid, targetRoot)
	local damage = enemyModel:GetAttribute("Damage") or 5
	local attackRange = enemyModel:GetAttribute("AttackRange") or 5
	local isBoss = enemyModel:GetAttribute("IsBoss") == true

	-- Face the target
	local flatTarget = Vector3.new(targetRoot.Position.X, rootPart.Position.Y, targetRoot.Position.Z)
	if (flatTarget - rootPart.Position).Magnitude > 0.1 then
		rootPart.CFrame = CFrame.lookAt(rootPart.Position, flatTarget)
	end

	-- Wind-up: the enemy's glow flares so players can see the hit coming
	local glow = rootPart:FindFirstChild("Glow")
	if glow then
		glow.Brightness = 6
	end
	task.wait(WIND_UP_TIME)
	if glow then
		glow.Brightness = 1.5
	end
	if humanoid.Health <= 0 or not enemyModel.Parent then
		return
	end

	-- Hit lands: bosses slam everyone nearby, normal enemies hit only if still in reach
	for _, player in ipairs(Players:GetPlayers()) do
		local _, _, playerRoot = getLivingCharacter(player)
		if playerRoot and player:GetAttribute("InDungeon") then
			local distance = (playerRoot.Position - rootPart.Position).Magnitude
			local isTarget = playerRoot == targetRoot
			if isBoss and distance <= attackRange * 1.3 then
				damagePlayer(player, damage)
			elseif isTarget and distance <= attackRange + 1.5 then
				damagePlayer(player, damage)
			end
		end
	end
end

--[[ Movement ]]
-- Walks along a computed path until the refresh interval runs out
local function followPath(humanoid, rootPart, path, destination)
	local computed = pcall(path.ComputeAsync, path, rootPart.Position, destination)
	if not computed or path.Status ~= Enum.PathStatus.Success then
		-- No path found: walk straight at the target instead
		humanoid:MoveTo(destination)
		task.wait(AIConfig.PathRefreshInterval)
		return
	end
	local deadline = os.clock() + AIConfig.PathRefreshInterval
	local waypoints = path:GetWaypoints()
	for index = 2, #waypoints do
		local waypointPosition = waypoints[index].Position
		humanoid:MoveTo(waypointPosition)
		while os.clock() < deadline and humanoid.Health > 0 do
			local flatOffset = (waypointPosition - rootPart.Position) * Vector3.new(1, 0, 1)
			if flatOffset.Magnitude < 3 then
				break
			end
			task.wait(0.05)
		end
		if os.clock() >= deadline or humanoid.Health <= 0 then
			return
		end
	end
end

--[[ Public API ]]
-- Starts the AI loop for one enemy. It stops by itself when the enemy dies or is removed.
function EnemyAI.Start(enemyModel)
	local humanoid = enemyModel:FindFirstChildOfClass("Humanoid")
	local rootPart = enemyModel.PrimaryPart
	if not humanoid or not rootPart then
		return
	end
	local scale = enemyModel:GetAttribute("Scale") or 1
	local path = PathfindingService:CreatePath({
		AgentRadius = 1.5 * scale,
		AgentHeight = 5 * scale,
		AgentCanJump = false,
		WaypointSpacing = 6,
	})

	task.spawn(function()
		local lastAttackTime = 0
		while enemyModel.Parent and humanoid.Health > 0 do
			local targetRoot, distance = findNearestTarget(rootPart.Position)
			local attackRange = enemyModel:GetAttribute("AttackRange") or 5
			local attackCooldown = enemyModel:GetAttribute("AttackCooldown") or 1

			if not targetRoot then
				-- Nobody to chase: stand still
				humanoid:MoveTo(rootPart.Position)
				task.wait(0.5)
			elseif distance <= attackRange then
				-- In reach: stop and attack when the cooldown is ready
				humanoid:MoveTo(rootPart.Position)
				if os.clock() - lastAttackTime >= attackCooldown then
					lastAttackTime = os.clock()
					performAttack(enemyModel, rootPart, humanoid, targetRoot)
				end
				task.wait(0.1)
			elseif distance <= AIConfig.DirectChaseDistance then
				-- Close: run straight at the player
				humanoid:MoveTo(targetRoot.Position)
				task.wait(0.15)
			else
				-- Far: use pathfinding around pillars
				followPath(humanoid, rootPart, path, targetRoot.Position)
			end
		end
		path:Destroy()
	end)
end

return EnemyAI
