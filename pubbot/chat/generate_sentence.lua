--[[
# Copyright 2014 the original author or authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
--]]

local random_grouping = redis.call("SRANDMEMBER", "T_" .. ARGV[1])
if not random_grouping then
    return "[]"
end
random_grouping = string.sub(random_grouping, 3)

local base_chain = {}
for token in string.gmatch(random_grouping, '([^_]+)') do
    table.insert(base_chain, token)
end

local starts_chain = (random_grouping[1] == '_')
local ends_chain = (random_grouping[#random_grouping] == '_')

local base_score = 0
if #base_chain >= 3 then
    base_score = tonumber(redis.call("GET", "G_" .. base_chain[1] .. "_" .. base_chain[2] .."_" .. base_chain[3]))
end

local results = {}

for i = 1, tonumber(ARGV[2]) do
    local chain = {}
    for key, token in pairs(base_chain) do
        chain[key] = token
    end
    local score = base_score or 0
    local val = nil

    if not starts_chain then
        while true do
            val = redis.call("SRANDMEMBER", "B_" .. chain[2] .. "_" .. chain[1])
            if not val or val=='' then break end
            table.insert(chain, 1, val)
            score = score + tonumber(redis.call("GET", "G_" .. chain[1] .. "_" .. chain[2] .. "_" .. chain[3]) or 0)
        end
    end
    if not ends_chain then
        while true do
            val = redis.call("SRANDMEMBER", "F_" .. chain[#chain - 1] .. "_" .. chain[#chain])
            if not val or val=='' then break end
            table.insert(chain, val)
            score = score + tonumber(redis.call("GET", "G_" .. chain[1] .. "_" .. chain[2] .. "_" .. chain[3]) or 0)
        end
    end

    table.insert(results, {score=score / #chain, chain=chain})
end

return cjson.encode(results)
