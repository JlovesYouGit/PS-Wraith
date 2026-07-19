#!/usr/bin/env lua
-- Master formula: chain all escalation steps
-- This is the main entry point for magi-zone-android

local magi = dofile("magi_zone_bootstrap.lua")

magi.log("=== magi-zone Android Master Formula ===")
magi.log("Device: " .. (magi.device_serial or "default"))

-- Determine current state
local current_level = magi.get_access_level()
magi.log("Current access level: " .. current_level)

-- Formula chain ordered by access level
local formulas = {}

if current_level < 1 then
    magi.log("Attempting ADB root escalation...")
    local f1 = dofile("formulas/adb_root.lua")
    table.insert(formulas, f1)
end

if current_level < 2 then
    magi.log("Attempting SELinux permissive...")
    local f2 = dofile("formulas/selinux_permissive.lua")
    table.insert(formulas, f2)
end

if current_level < 3 then
    magi.log("Attempting SIM unblock...")
    local f3 = dofile("formulas/sim_unblock.lua")
    table.insert(formulas, f3)
end

-- Execute formulas in chain
for _, formula in ipairs(formulas) do
    local ok = magi.elevate(formula)
    if not ok then
        magi.log("Formula FAILED: " .. formula.name)
        -- Continue with next formula instead of aborting
    else
        magi.log("Formula SUCCESS: " .. formula.name)
    end
end

-- Final status
local final_status = magi.status()
magi.log("=== Final Status ===")
magi.log("Access Level: " .. final_status.access_level)
magi.log("Current Level: " .. final_status.current_level)

-- Output JSON status for parser
local json = require("json")
if json then
    print(json.encode(final_status))
else
    print("{\"access_level\":" .. final_status.access_level .. 
          ",\"current_level\":" .. final_status.current_level .. "}")
end
