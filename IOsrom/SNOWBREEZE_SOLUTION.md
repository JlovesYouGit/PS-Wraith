# sn0wbreeze Solution

## Why This Will Work

You have **IBFL: 0x03** (NAND bypass) = Device will boot ANY unsigned code permanently

## Steps

1. **Download sn0wbreeze 2.9.6** (supports iPad1,1 iOS 4.3.3)
   - Get from: https://www.iphonehacks.com/download-sn0wbreeze

2. **Create Custom IPSW**
   - Run sn0wbreeze.exe
   - Select iPad1,1_4.3.3_8J3_Restore.ipsw
   - Choose "Simple Mode"
   - Enable: Install Cydia, Install SSH
   - Build custom IPSW

3. **Restore with iTunes**
   - Open iTunes
   - Hold SHIFT + click "Restore iPad"
   - Select the custom IPSW from sn0wbreeze
   - iTunes will restore (ignores TSS errors because NAND bypass active)

4. **Result**
   - Device will boot to iOS 4.3.3
   - Jailbroken with Cydia
   - SSH enabled
   - NAND bypass still active (IBFL: 0x03 is permanent)

## Why iTunes Works Now

- sn0wbreeze patches iBSS/iBEC to skip signature checks
- Custom IPSW has patched kernel that boots without TSS
- NAND bypass (IBFL: 0x03) allows unsigned boot
- iTunes can restore because it doesn't need Apple's server

## Alternative: redsn0w "Just Boot"

If sn0wbreeze fails:
1. Use redsn0w "Extras" -> "Just boot"
2. Point to iPad1,1_4.3.3_8J3_Restore.ipsw
3. Device boots tethered to iOS
4. Use Cydia to install filesystem tools
5. Manually write filesystem with dd
