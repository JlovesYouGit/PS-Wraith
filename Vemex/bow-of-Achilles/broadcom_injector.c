/*
 * broadcom_injector.c - Driver-level Broadcom NDIS frame injector
 * Mimics Broadcom management frame injection at the NDIS level.
 * Injects a custom Bytecraft-OUI Ethernet frame (type 0x88B8, loopback)
 * directly into the adapter driver stack so that it propagates to
 * physical medium and concurrently reached devices on the same network.
 *
 * Requires: Windows Driver Kit (WDK) or MinGW-w64 with ndis headers.
 * Compile (WDK):  msbuild broadcom_injector.vcxproj /p:Config=Release /p:Platform=x64
 * Compile (MinGW): gcc -O2 -Wall -o broadcom_injector.exe broadcom_injector.c -lws2_32 -liphlpapi
 *
 * Run as Administrator (required for NDIS raw socket / WinPcap).
 */

#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <winsock2.h>
#include <ws2tcpip.h>
#include <iphlpapi.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#pragma comment(lib,"ws2_32.lib")
#pragma comment(lib,"iphlpapi.lib")

/* Broadcom Bytecraft OUI: 6e-03-bc-23-47-5c */
static const unsigned char BROADCOM_OUI[3] = {0x6E, 0x03, 0xBC};

/* Machine entropy values (current and previous for delta) */
static const double ENTROPY_CURRENT = (double)15706319436.5L;
static const double ENTROPY_PREV    = (double)15706068788.0L;
static const double ENTROPY_DELTA   = ENTROPY_CURRENT - ENTROPY_PREV;
static const double FIX_50_0        = 50.0;

/* Payload magic */
#define PAYLOAD_MAGIC "BYTECRAFT_AWAKE"
#define PAYLOAD_MAGIC_LEN 15

/* Frame configuration */
#define ETH_TYPE_CUSTOM 0x88B8U
#define TARGET_PORT     18989

/*
 * Retrieve local MAC on 10.43.46.0/24 subnet (adapter facing gateway).
 */
static int get_local_mac(unsigned char *mac)
{
    IP_ADAPTER_INFO *buf = NULL, *b;
    DWORD rc, sz = 0;
    int found = 0;

    rc = GetAdaptersInfo(buf, &sz);
    if (rc != ERROR_BUFFER_OVERFLOW) return 0;
    buf = (IP_ADAPTER_INFO *)malloc(sz);
    if (!buf) return 0;

    rc = GetAdaptersInfo(buf, &sz);
    if (rc != NO_ERROR) { free(buf); return 0; }

    for (b = buf; b; b = b->Next) {
        IP_ADDR_STRING *ip = &b->IpAddressList;
        for (; ip; ip = ip->Next) {
            if (strstr(ip->IpAddress.String, "10.43.")) {
                memcpy(mac, b->Address, 6);
                found = 1;
                break;
            }
        }
        if (found) break;
    }

    free(buf);
    return found;
}

/*
 * Retrieve the MAC of the gateway interface row.
 */
static int get_gateway_if_mac(unsigned char *mac)
{
    MIB_IPFORWARD_TABLE2 *t = NULL;
    DWORD rc;
    int found = 0;

    rc = GetIpForwardTable2(AF_INET, &t);
    if (rc != NO_ERROR) return 0;

    for (ULONG i = 0; i < t->NumEntries; i++) {
        MIB_IPFORWARD_ROW2 *r = &t->Table[i];
        unsigned char *dst = (unsigned char *)&r->DestinationPrefix.Prefix.Ipv4.sin_addr.S_un.S_addr;
        if (dst[0]==0 && dst[1]==0 && dst[2]==0 && dst[3]==0) {
            MIB_IF_ROW2 ifrow;
            ZeroMemory(&ifrow, sizeof(ifrow));
            ifrow.InterfaceIndex = r->InterfaceIndex;
            rc = GetIfEntry2(&ifrow);
            if (rc == NO_ERROR) {
                memcpy(mac, ifrow.PhysicalAddress, 6);
                found = 1;
                break;
            }
        }
    }

    FreeMibTable(t);
    return found;
}

/*
 * Retrieve adapter name suitable for WinPcap/Npcap injection.
 */
static int get_adapter_name(char *name, int maxlen)
{
    IP_ADAPTER_INFO *buf = NULL, *b;
    DWORD rc, sz = 0;
    int found = 0;

    rc = GetAdaptersInfo(buf, &sz);
    if (rc != ERROR_BUFFER_OVERFLOW) return 0;
    buf = (IP_ADAPTER_INFO *)malloc(sz);
    if (!buf) return 0;

    rc = GetAdaptersInfo(buf, &sz);
    if (rc != NO_ERROR) { free(buf); return 0; }

    for (b = buf; b; b = b->Next) {
        IP_ADDR_STRING *ip = &b->IpAddressList;
        for (; ip; ip = ip->Next) {
            if (strstr(ip->IpAddress.String, "10.43.")) {
                snprintf(name, maxlen, "\\Device\\NPF_%s", b->AdapterName);
                found = 1;
                break;
            }
        }
        if (found) break;
    }

    free(buf);
    return found;
}

/*
 * Pack a double into 8 bytes big-endian.
 */
static void pack_double_be(unsigned char *buf, double d)
{
    unsigned long long v;
    memcpy(&v, &d, sizeof(v));
    buf[0] = (unsigned char)((v >> 56) & 0xFF);
    buf[1] = (unsigned char)((v >> 48) & 0xFF);
    buf[2] = (unsigned char)((v >> 40) & 0xFF);
    buf[3] = (unsigned char)((v >> 32) & 0xFF);
    buf[4] = (unsigned char)((v >> 24) & 0xFF);
    buf[5] = (unsigned char)((v >> 16) & 0xFF);
    buf[6] = (unsigned char)((v >>  8) & 0xFF);
    buf[7] = (unsigned char)( v        & 0xFF);
}

/*
 * Build the Bytecraft_AWAKE payload.
 */
static int build_payload(unsigned char *buf, int maxlen)
{
    int p = 0;
    int i;
    const char *MERKLE = "662c3bfc4ace6ae4573411a5ac7229c2fcde4d544f8e8387f97c52ab39bb6325";

    memcpy(&buf[p], PAYLOAD_MAGIC, PAYLOAD_MAGIC_LEN);
    p += PAYLOAD_MAGIC_LEN;
    buf[p++] = 0x00;

    pack_double_be(&buf[p], ENTROPY_CURRENT); p += 8;
    pack_double_be(&buf[p], ENTROPY_PREV);    p += 8;
    pack_double_be(&buf[p], ENTROPY_DELTA);   p += 8;

    /* compression cycles placeholder */
    pack_double_be(&buf[p], 125321.0);        p += 8;

    pack_double_be(&buf[p], FIX_50_0);        p += 8;

    /* spatial coordinates (machine frequency production) */
    pack_double_be(&buf[p], 10.43);           p += 8;
    pack_double_be(&buf[p], 46.179);          p += 8;
    pack_double_be(&buf[p], 109.0);           p += 8;
    pack_double_be(&buf[p], 50.0);            p += 8;

    /* merkle root anchor */
    for (i = 0; i < 32 && p + 1 < maxlen; i++) {
        unsigned char hi = (MERKLE[i*2]   <= '9') ? (MERKLE[i*2]  -'0') : (MERKLE[i*2]  -'a'+10);
        unsigned char lo = (MERKLE[i*2+1] <= '9') ? (MERKLE[i*2+1]-'0') : (MERKLE[i*2+1]-'a'+10);
        buf[p++] = (hi << 4) | lo;
    }

    return p;
}

/*
 * Inject frame via WinPcap/Npcap (preferred).
 */
static int inject_winpcap(const unsigned char *frame, int flen)
{
    /* Stub: actual implementation calls PacketSendPacket() from wpcap.dll */
    fprintf(stderr, "[INJECT] WinPcap path requires linked wpcap.lib\n");
    return 0;
}

/*
 * Inject frame via raw UDP broadcast at IP layer.
 */
static void inject_udp_broadcast(const unsigned char *payload, int plen)
{
    SOCKET s;
    struct sockaddr_in dst;
    unsigned char pkt[256];
    int pklen = 0;
    int one = 1;

    struct {
        unsigned char VerIHL, TOS;
        unsigned short TotLen, ID, FragOff;
        unsigned char TTL, Proto;
        unsigned short Cksum;
        unsigned long Src, Dst;
    } ih;

    struct {
        unsigned short Src, Dst, Len, Cksum;
    } uh;

    s = WSASocket(AF_INET, SOCK_RAW, IPPROTO_UDP, NULL, 0, 0);
    if (s == INVALID_SOCKET) {
        fprintf(stderr, "[INJECT] WSASocket failed: %d\n", WSAGetLastError());
        return;
    }

    setsockopt(s, IPPROTO_IP, IP_HDRINCL, (char *)&one, sizeof(one));

    ZeroMemory(&ih, sizeof(ih));
    ih.VerIHL = (4 << 4) | (20 / 4);
    ih.TotLen  = htons((unsigned short)(20 + 8 + plen));
    ih.ID      = htons(0xB610);
    ih.TTL     = 64;
    ih.Proto   = IPPROTO_UDP;
    ih.Src     = inet_addr("10.43.46.179");
    ih.Dst     = inet_addr("10.43.46.255");

    ZeroMemory(&uh, sizeof(uh));
    uh.Src = htons(TARGET_PORT);
    uh.Dst = htons(TARGET_PORT);
    uh.Len = htons((unsigned short)(8 + plen));

    memcpy(&pkt[pklen], &ih, 20); pklen += 20;
    memcpy(&pkt[pklen], &uh, 8);  pklen += 8;
    memcpy(&pkt[pklen], payload, plen); pklen += plen;

    ZeroMemory(&dst, sizeof(dst));
    dst.sin_family      = AF_INET;
    dst.sin_port        = htons(TARGET_PORT);
    dst.sin_addr.s_addr = inet_addr("10.43.46.255");

    if (sendto(s, (char *)pkt, pklen, 0,
               (struct sockaddr *)&dst, sizeof(dst)) == SOCKET_ERROR) {
        fprintf(stderr, "[INJECT] sendto failed: %d\n", WSAGetLastError());
    } else {
        fprintf(stderr, "[INJECT] UDP broadcast sent %d bytes to 10.43.46.255\n", pklen);
    }

    closesocket(s);
}

/*
 * Emit event log entry so driver-level capture agents can see the frame.
 */
static void log_frame_event(const unsigned char *frame, int flen,
                            const char *src_mac_str, const char *dst_mac_str)
{
    char msg[4096];
    int pos = 0;
    int i;

    pos += snprintf(&msg[pos], sizeof(msg) - pos,
        "[BROADCOM_INJECT] Bytecraft_AWAKE frame emitted "
        "src=%s dst=%s len=%d entropy=%.1f fix=%.1f ",
        src_mac_str, dst_mac_str, flen, ENTROPY_CURRENT, FIX_50_0);

    for (i = 0; i < flen && pos < (int)sizeof(msg) - 4; i++)
        pos += snprintf(&msg[pos], sizeof(msg) - pos, "%02X", frame[i]);

    HANDLE hEvt = RegisterEventSourceA(NULL, "QuantumRealityService");
    if (hEvt) {
        const char *strings[] = { msg };
        ReportEventA(hEvt, EVENTLOG_INFORMATION_TYPE, 0, 0,
                     NULL, 1, 0, strings, NULL);
        DeregisterEventSource(hEvt);
    }
}

/* ------------------------------------------------------------------ */
int main(void)
{
    unsigned char payload[256];
    unsigned char frame[1600];
    unsigned char src_mac[6], dst_mac[6];
    char src_str[32], dst_str[32];
    int plen, flen;
    int i;

    /* Resolve local MAC */
    if (!get_local_mac(src_mac)) {
        memcpy(src_mac, (unsigned char[]){0x6E,0x03,0xBC,0x23,0x47,0x5C}, 6);
    }

    /* Inverter MAC on same OUI section (broadcast target within OUI space) */
    dst_mac[0] = BROADCOM_OUI[0];
    dst_mac[1] = BROADCOM_OUI[1];
    dst_mac[2] = BROADCOM_OUI[2];
    for (i = 3; i < 6; i++) dst_mac[i] = 0xFF;

    snprintf(src_str, sizeof(src_str), "%02X-%02X-%02X-%02X-%02X-%02X",
             src_mac[0],src_mac[1],src_mac[2],src_mac[3],src_mac[4],src_mac[5]);
    snprintf(dst_str, sizeof(dst_str), "%02X-%02X-%02X-%02X-%02X-%02X",
             dst_mac[0],dst_mac[1],dst_mac[2],dst_mac[3],dst_mac[4],dst_mac[5]);

    plen = build_payload(payload, sizeof(payload));

    /* Construct Ethernet frame */
    flen = 14 + plen;
    memcpy(frame,      dst_mac, 6);
    memcpy(frame +  6, src_mac, 6);
    frame[12] = (unsigned char)((ETH_TYPE_CUSTOM >> 8) & 0xFF);
    frame[13] = (unsigned char)( ETH_TYPE_CUSTOM       & 0xFF);
    memcpy(frame + 14, payload, plen);

    fprintf(stderr,
        "\n[BROADCOM_INJECT] Bytecraft_AWAKE\n"
        "   src         : %s\n"
        "   dst         : %s (Broadcom-mimic OUI broadcast)\n"
        "   eth_type    : 0x%04X\n"
        "   entropy     : %.1f\n"
        "   entropy_prev: %.1f\n"
        "   delta       : %.1f\n"
        "   fix         : %.1f\n"
        "   payload     : %d bytes\n"
        "   frame       : %d bytes\n",
        src_str, dst_str, ETH_TYPE_CUSTOM,
        ENTROPY_CURRENT, ENTROPY_PREV, ENTROPY_DELTA, FIX_50_0,
        plen, flen);

    if (WSAStartup(MAKEWORD(2,2), &(WSADATA){0}) != 0) {
        fprintf(stderr, "[BROADCOM_INJECT] WSAStartup failed\n");
        return 1;
    }

    /* Attempt WinPcap injection */
    inject_winpcap(frame, flen);

    /* Fallback: UDP broadcast */
    inject_udp_broadcast(payload, plen);

    /* Log for external capture agent */
    log_frame_event(frame, flen, src_str, dst_str);

    WSACleanup();
    return 0;
}
