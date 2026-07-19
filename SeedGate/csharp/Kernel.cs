using System.Security.Cryptography;
using System.Text;

namespace SeedKernel;

// Deterministic seed processor: value → 32-byte binary block (SHA-256)
// → 13-char base36 alphanumeric key. Pure computation, no I/O.
internal sealed class Kernel
{
    private readonly SHA256 _sha = SHA256.Create();

    public Task<SeedResult> ProcessAsync(SeedEvent evt)
    {
        // Await a completed Task so we're on the async fast-path — the
        // signature is async-friendly for future extensions without paying
        // Thread.Yield() every event.
        var value = evt.Value ?? string.Empty;
        var block = BinaryBlock(value);
        var key = KeyDerivation.DeriveBase36(block, minLen: 13);
        var result = new SeedResult(
            Id: evt.Id,
            Key: key,
            BlockSize: block.Length,
            BlockSha256: Hex(block),
            Engine: "csharp-net8"
        );
        return Task.FromResult(result);
    }

    private byte[] BinaryBlock(string value)
    {
        // SHA-256 of UTF-8 bytes — matches the Python stub exactly, so
        // switching engines produces identical keys.
        var bytes = Encoding.UTF8.GetBytes(value);
        return _sha.ComputeHash(bytes);
    }

    private static string Hex(ReadOnlySpan<byte> bytes)
    {
        var sb = new StringBuilder(bytes.Length * 2);
        foreach (var b in bytes) sb.Append(b.ToString("x2"));
        return sb.ToString();
    }
}
