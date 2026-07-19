#!/usr/bin/env lua
-- ADB root escalation formula
-- Tries adb root, su injection, and remount

local formula = {
    name = "adb_root_escalation",
    target_level = 1,
    chain = {
        {
            name = "try_adb_root",
            type = "adb",
            cmd = "root",
            check = "restarting"
        },
        {
            name = "wait_for_root",
            type = "sleep",
            duration = 3
        },
        {
            name = "verify_root_id",
            type = "shell",
            cmd = "id",
            root = true,
            check = "uid=0"
        }
    }
}

return formula
