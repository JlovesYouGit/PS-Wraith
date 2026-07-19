using System.Text;

namespace SeedKernel;

// Base36 alphanumeric key derivation from a binary block. First 8 bytes of
// the block are read big-endian as an unsigned 64-bit integer and encoded
// in base36. Padded to `minLen` characters. Kept byte-for-byte compatible
// with python/seed_sampler/kernel_stub.py so both engines yield the same
// key for the same input.
internal static class KeyDerivation
{
    private const string Alphabet = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ";

    public static string DeriveBase36(ReadOnlySpan<byte> block, int minLen)
    {
        if (block.Length < 8)
        {
            // Zero-pad on the left of the block to reach 8 bytes.
            Span<byte> padded = stackalloc byte[8];
            block.CopyTo(padded.Slice(8 - block.Length));
            return EncodeBase36(BigEndianToUInt64(padded), minLen);
        }
        return EncodeBase36(BigEndianToUInt64(block.Slice(0, 8)), minLen);
    }

    private static ulong BigEndianToUInt64(ReadOnlySpan<byte> b)
    {
        ulong v = 0;
        for (int i = 0; i < 8; i++)
        {
            v = (v << 8) | b[i];
        }
        return v;
    }

    private static string EncodeBase36(ulong n, int minLen)
    {
        if (n == 0)
        {
            return new string('0', minLen);
        }
        var sb = new StringBuilder(16);
        while (n > 0)
        {
            var r = (int)(n % 36UL);
            sb.Append(Alphabet[r]);
            n /= 36UL;
        }
        // Reverse in place.
        var chars = new char[sb.Length];
        for (int i = 0; i < sb.Length; i++) chars[i] = sb[sb.Length - 1 - i];
        var s = new string(chars);
        return s.Length >= minLen ? s : s.PadLeft(minLen, '0');
    }
}
