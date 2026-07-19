#!/usr/bin/env lua
-- magi-zone bootstrap for Android
-- Formula-based privilege escalation runtime

local magi = {}
magi.zone = "android_root"
magi.formula = {}
magi.access_level = 0
magi.chain_log = {}
magi.device_serial = os.getenv("DEVICE_SERIAL") or ""

function magi.log(msg)
    io.write("[magi-zone] " .. tostring(msg) .. "\n")
    io.flush()
end

function magi.exec(cmd)
    magi.log("EXEC: " .. cmd)
    local handle = io.popen(cmd .. " 2>&1")
    local output = handle:read("*a")
    handle:close()
    magi.chain_log[#magi.chain_log+1] = {cmd=cmd, output=output}
    return output
}

function magi.adb(cmd)
    local serial_prefix = ""
    if magi.device_serial ~= "" then
        serial_prefix = "-s " .. magi.device_serial .. " "
    end
    return magi.exec("adb " .. serial_prefix .. cmd)
end

function magi.adb_shell(cmd, as_root)
    if as_root then
        return magi.adb("shell su -c '" .. cmd:gsub("'", "'\\''") .. "'")
    else
        return magi.adb("shell '" .. cmd:gsub("'", "'\\''") .. "'")
    end
end

function magi.fastboot(cmd)
    return magi.exec("fastboot " .. cmd)
end

function magi.elevate(formula)
    magi.log("Elevating via formula: " .. formula.name)
    magi.log("Target access level: " .. formula.target_level)
    
    for i, step in ipairs(formula.chain) do
        magi.log("Step " .. i .. ": " .. step.name)
        local ok = magi.run_step(step)
        if not ok and step.required ~= false then
            magi.log("STEP FAILED: " .. step.name)
            return false
        end
        if step.sleep then
            os.execute("sleep " .. step.sleep)
        end
    end
    
    magi.access_level = formula.target_level
    magi.log("Elevation complete. Access level: " .. magi.access_level)
    return true
end

function magi.run_step(step)
    if step.type == "adb" then
        local out = magi.adb(step.cmd)
        if step.check then
            return out:find(step.check) ~= nil
        end
        return true
    elseif step.type == "shell" then
        local out = magi.adb_shell(step.cmd, step.root == true)
        if step.check then
            return out:find(step.check) ~= nil
        end
        return true
    elseif step.type == "fastboot" then
        local out = magi.fastboot(step.cmd)
        if step.check then
            return out:find(step.check) ~= nil
        end
        return true
    elseif step.type == "lua" then
        return dofile(step.path)
    elseif step.type == "sleep" then
        os.execute("sleep " .. (step.duration or 1))
        return true
    end
    return false
end

function magi.get_access_level()
    -- Check current root status
    local id_output = magi.adb_shell("id", false)
    if id_output:find("uid=0") then
        return 3 -- root
    end
    
    local root_output = magi.adb_shell("id", true)
    if root_output:find("uid=0") then
        return 3 -- root via su
    end
    
    -- Check if bootloader unlocked
    local fb_vars = magi.fastboot("getvar all")
    if fb_vars:find("unlocked") or fb_vars:find("unlock") then
        return 2 -- bootloader unlocked
    end
    
    -- Check if adb root available
    local adb_root = magi.adb("root")
    if adb_root:find("restarting") or adb_root:find("adbd") then
        return 2 -- adb root
    end
    
    return 0 -- no special access
end

function magi.status()
    return {
        zone = magi.zone,
        access_level = magi.access_level,
        current_level = magi.get_access_level(),
        device_serial = magi.device_serial,
        chain_log = magi.chain_log
    }
end

return magi
