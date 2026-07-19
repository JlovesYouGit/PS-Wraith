/*
 * entropy_broadcast.c - Mimics Broadcom raw Ethernet frame broadcast
 * Spans space from entropy to surrounding external frequency bounds,
 * influences total surrounding space entropy and elevates spatial
 * bound coordinates. Synchronizes concurrent machine space using
 * the Bytecraft signature through the local 6E-03-BC-23-47-5C gateway.
 *
 * Compile:  cl /O2 entropy_broadcast.c /link ws2_32.lib iphlpapi.lib
 *           (Visual Studio / Windows SDK, x64)
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

/* Broadcom Bytecraft OUI : 6e-03-bc-23-47-5c */
#define BROADCAST_OUI {0x6E, 0x03, 0xBC, 0xFF, 0xFF, 0xFF}
#define GATEWAY_MAC  {0x6E, 0x03, 0xBC, 0x23, 0x47, 0x5C}

/* Magic constants derived from machine entropy and block state */
static const double ENTROPY_CURRENT = (double)15706319436.5L;
static const double ENTROPY_PREV    = (double)15706068788.0L;
static const double ENTROPY_DELTA   = ENTROPY_CURRENT - ENTROPY_PREV;
static const double FIX_50_0        = 50.0;
static const double COMP_CYCLES     = (double)125321.0L;

/* Payload tag */
#define PAYLOAD_TAG "BYTECRAFT_AWAKE"
#define MERKLE_ROOT  "662c3bfc4ace6ae4573411a5ac7229c2fcde4d544f8e8387f97c52ab39bb6325"

/* IP destination for the QuantumEnergyService broadcast receiver */
#define TARGET_IP   "10.43.46.109"
#define LISTEN_PORT 18989

/* ------------------------------------------------------------------ */
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

/* ------------------------------------------------------------------ */
static int get_local_mac(unsigned char *mac)
{
    IP_ADAPTER_INFO *b, *buf = NULL;
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
                memcpy(mac, b->Address, b->AddressLength < 6 ? b->AddressLength : 6);
                found = 1;
                break;
            }
        }
        if (found) break;
    }

    free(buf);
    return found;
}

/* ------------------------------------------------------------------ */
static int get_gateway_mac(unsigned char *mac)
{
    MIB_IPFORWARD_TABLE2 *t = NULL;
    DWORD rc;
    int found = 0;

    rc = GetIpForwardTable2(AF_INET, &t);
    if (rc != NO_ERROR) return 0;

    for (ULONG i = 0; i < t->NumEntries; i++) {
        MIB_IPFORWARD_ROW2 *r = &t->Table[i];
        unsigned char *dst = (unsigned char *)&r->DestinationPrefix.Prefix.Ipv4.sin_addr.S_un.S_addr;
        if (dst[0] == 0 && dst[1] == 0 && dst[2] == 0 && dst[3] == 0) {
            MIB_IF_ROW2 ifrow;
            ZeroMemory(&ifrow, sizeof(ifrow));
            ifrow.InterfaceIndex = r->InterfaceIndex;
            rc = GetIfEntry2(&ifrow);
            if (rc == NO_ERROR) {
                memcpy(mac, ifrow.PhysicalAddress,
                       ifrow.PhysicalAddressLength < 6 ? ifrow.PhysicalAddressLength : 6);
                found = 1;
                break;
            }
        }
    }

    FreeMibTable(t);
    return found;
}

/* ------------------------------------------------------------------ */
static void build_payload(unsigned char *buf, int *len)
{
    int p = 0;
    int i;
    unsigned char hi, lo;

    /* Tag */
    memcpy(&buf[p], PAYLOAD_TAG, sizeof(PAYLOAD_TAG) - 1);
    p += (int)sizeof(PAYLOAD_TAG) - 1;
    buf[p++] = 0x00;

    /* entropy_current */
    pack_double_be(&buf[p], ENTROPY_CURRENT); p += 8;
    /* entropy_prev */
    pack_double_be(&buf[p], ENTROPY_PREV);    p += 8;
    /* entropy_delta */
    pack_double_be(&buf[p], ENTROPY_DELTA);   p += 8;
    /* compression_cycles */
    pack_double_be(&buf[p], COMP_CYCLES);     p += 8;
    /* fix_50.0 */
    pack_double_be(&buf[p], FIX_50_0);        p += 8;

    /* spatial offset (mirror of machine frequency) */
    pack_double_be(&buf[p], 10.43);           p += 8;
    /* bound coordinate elevation */
    pack_double_be(&buf[p], 46.179);          p += 8;
    /* merged bound */
    pack_double_be(&buf[p], 109.0);           p += 8;
    /* quantum horizon index */
    pack_double_be(&buf[p], 50.0);            p += 8;

    /* merkle_root anchor (32 bytes) */
    for (i = 0; i < 32; i++) {
        unsigned char a = (unsigned char)MERKLE_ROOT[i*2];
        unsigned char b = (unsigned char)MERKLE_ROOT[i*2+1];
        hi = (a <= '9') ? (a - '0') : (a - 'a' + 10);
        lo = (b <= '9') ? (b - '0') : (b - 'a' + 10);
        buf[p++] = (hi << 4) | lo;
    }

    *len = p;
}

/* ------------------------------------------------------------------ */
static void broadcast_udp(unsigned char *payload, int plen)
{
    SOCKET s;
    int one = 1;
    struct sockaddr_in dst;
    unsigned char pkt[256];
    int pklen = 0;
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
        fprintf(stderr, "[ENTROPY] WSASocket failed: %d\n", WSAGetLastError());
        return;
    }

    if (setsockopt(s, IPPROTO_IP, IP_HDRINCL, (char *)&one, sizeof(one)) < 0) {
        fprintf(stderr, "[ENTROPY] IP_HDRINCL failed: %d\n", WSAGetLastError());
        closesocket(s);
        return;
    }

    ZeroMemory(&ih, sizeof(ih));
    ih.VerIHL = (4 << 4) | (20 / 4);
    ih.TotLen  = htons((unsigned short)(20 + 8 + plen));
    ih.ID      = htons(0xB601);
    ih.TTL     = 64;
    ih.Proto   = IPPROTO_UDP;
    ih.Src     = inet_addr("10.43.46.179");
    ih.Dst     = inet_addr(TARGET_IP);

    ZeroMemory(&uh, sizeof(uh));
    uh.Src = htons(LISTEN_PORT);
    uh.Dst = htons(LISTEN_PORT);
    uh.Len = htons((unsigned short)(8 + plen));

    memcpy(&pkt[pklen], &ih, 20); pklen += 20;
    memcpy(&pkt[pklen], &uh, 8);  pklen += 8;
    memcpy(&pkt[pklen], payload, plen); pklen += plen;

    ZeroMemory(&dst, sizeof(dst));
    dst.sin_family      = AF_INET;
    dst.sin_port        = htons(LISTEN_PORT);
    dst.sin_addr.s_addr = inet_addr(TARGET_IP);

    if (sendto(s, (char *)pkt, pklen, 0,
               (struct sockaddr *)&dst, sizeof(dst)) == SOCKET_ERROR) {
        fprintf(stderr, "[ENTROPY] sendto failed: %d\n", WSAGetLastError());
    } else {
        fprintf(stderr, "[ENTROPY] UDP broadcast to %s:%d (%d bytes)\n",
                TARGET_IP, LISTEN_PORT, pklen);
    }

    closesocket(s);
}

/* ------------------------------------------------------------------ */
static void log_event(const char *msg)
{
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
    unsigned char payload[200];
    int plen = 0;
    unsigned char src_mac[6] = GATEWAY_MAC;
    unsigned char dst_mac[6] = BROADCAST_OUI;
    unsigned char frame[1600];
    int i, flen;
    char macstr[64], dststr[64];

    build_payload(payload, &plen);
    flen = 14 + plen;

    memcpy(frame,      dst_mac, 6);
    memcpy(frame +  6, src_mac, 6);
    frame[12] = 0x08;
    frame[13] = 0x00;
    memcpy(frame + 14, payload, plen);

    snprintf(macstr, sizeof(macstr),
             "%02X-%02X-%02X-%02X-%02X-%02X",
             src_mac[0],src_mac[1],src_mac[2],
             src_mac[3],src_mac[4],src_mac[5]);
    snprintf(dststr, sizeof(dststr),
             "%02X-%02X-%02X-%02X-%02X-%02X",
             dst_mac[0],dst_mac[1],dst_mac[2],
             dst_mac[3],dst_mac[4],dst_mac[5]);

    fprintf(stderr,
        "\n[ENTROPY_BROADCAST] Bytecraft_AWAKE\n"
        "   entropy     : %.1f\n"
        "   entropy_prev: %.1f\n"
        "   delta       : %.1f\n"
        "   fix         : %.1f\n"
        "   cycles      : %.1f\n"
        "   src         : %s (gateway)\n"
        "   dst         : %s (Broadcom-mimic)\n"
        "   target      : %s\n"
        "   payload     : %d bytes\n"
        "   merkle_root : %s\n",
        ENTROPY_CURRENT, ENTROPY_PREV, ENTROPY_DELTA,
        FIX_50_0, COMP_CYCLES,
        macstr, dststr, TARGET_IP, plen, MERKLE_ROOT);

    if (WSAStartup(MAKEWORD(2,2), &(WSADATA){0}) != 0) {
        fprintf(stderr, "[ENTROPY] WSAStartup failed\n");
        return 1;
    }

    /* Primary: IP-level raw UDP to gateway and broadcast */
    broadcast_udp(payload, plen);

    /* Secondary: also attempt a subnet broadcast */
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
        if (s != INVALID_SOCKET) {
            setsockopt(s, IPPROTO_IP, IP_HDRINCL, (char *)&one, sizeof(one));

            ZeroMemory(&ih, sizeof(ih));
            ih.VerIHL = (4 << 4) | (20 / 4);
            ih.TotLen  = htons((unsigned short)(20 + 8 + plen));
            ih.ID      = htons(0xB602);
            ih.TTL     = 64;
            ih.Proto   = IPPROTO_UDP;
            ih.Src     = inet_addr("10.43.46.179");
            ih.Dst     = inet_addr("10.43.46.255");

            ZeroMemory(&uh, sizeof(uh));
            uh.Src = htons(LISTEN_PORT);
            uh.Dst = htons(LISTEN_PORT);
            uh.Len = htons((unsigned short)(8 + plen));

            memcpy(&pkt[pklen], &ih, 20); pklen += 20;
            memcpy(&pkt[pklen], &uh, 8);  pklen += 8;
            memcpy(&pkt[pklen], payload, plen); pklen += plen;

            ZeroMemory(&dst, sizeof(dst));
            dst.sin_family      = AF_INET;
            dst.sin_port        = htons(LISTEN_PORT);
            dst.sin_addr.s_addr = inet_addr("10.43.46.255");

            sendto(s, (char *)pkt, pklen, 0,
                   (struct sockaddr *)&dst, sizeof(dst));
            fprintf(stderr, "[ENTROPY] Subnet broadcast to 10.43.46.255\n");
            closesocket(s);
        }
    }

    /* Log the frame emission to event log for capture agents */
    {
        char event_msg[2048];
        snprintf(event_msg, sizeof(event_msg),
            "[ENTROPY_BROADCAST] Bytecraft_AWAKE emitted "
            "src=%s dst=%s target=%s "
            "entropy=%.1f delta=%.1f fix=%.1f cycles=%.1f "
            "merkle=%s len=%d",
            macstr, dststr, TARGET_IP,
            ENTROPY_CURRENT, ENTROPY_DELTA, FIX_50_0, COMP_CYCLES,
            MERKLE_ROOT, flen);
        log_event(event_msg);
    }

    WSACleanup();
    return 0;
}
