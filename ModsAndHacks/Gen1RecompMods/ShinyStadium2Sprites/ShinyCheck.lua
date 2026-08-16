local Stats = require("src.pokemon.Stats")

local ShinyCheck = {}

local function dvsOf(value)
	if type(value) ~= "table" then return nil end
	if type(value.dvs) == "table" then return value.dvs end
	if type(value.mon) == "table" and type(value.mon.dvs) == "table" then
		return value.mon.dvs
	end
	return value
end

function ShinyCheck.isShiny(value)
	return Stats.isShiny(dvsOf(value))
end

return ShinyCheck
