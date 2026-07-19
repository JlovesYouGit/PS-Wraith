using System.Text.Json;

namespace SeedKernel;

// Long-running kernel: reads JSONL events from stdin, writes JSONL results
// to stdout. Runs until stdin is closed. No sockets, no P/Invoke, no I/O
// beyond stdin/stdout/stderr.
internal static class Program
{
    private static readonly JsonSerializerOptions JsonOpts = new()
    {
        WriteIndented = false,
        PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
    };

    private static async Task<int> Main(string[] args)
    {
        // Unbuffered stdout so the Python driver sees each line immediately.
        var stdout = new StreamWriter(Console.OpenStandardOutput()) { AutoFlush = true };
        var stdin = new StreamReader(Console.OpenStandardInput());

        var kernel = new Kernel();

        string? line;
        while ((line = await stdin.ReadLineAsync().ConfigureAwait(false)) != null)
        {
            line = line.Trim();
            if (line.Length == 0) continue;

            SeedEvent? evt;
            try
            {
                evt = JsonSerializer.Deserialize<SeedEvent>(line, JsonOpts);
            }
            catch (JsonException ex)
            {
                await stdout.WriteLineAsync(
                    JsonSerializer.Serialize(new { error = "bad_json", detail = ex.Message },
                                             JsonOpts)).ConfigureAwait(false);
                continue;
            }

            if (evt is null)
            {
                await stdout.WriteLineAsync(
                    JsonSerializer.Serialize(new { error = "null_event" }, JsonOpts))
                    .ConfigureAwait(false);
                continue;
            }

            var result = await kernel.ProcessAsync(evt).ConfigureAwait(false);
            await stdout.WriteLineAsync(JsonSerializer.Serialize(result, JsonOpts))
                .ConfigureAwait(false);
        }

        return 0;
    }
}

// Matches the JSON emitted by python/seed_sampler/runner.py::_build_events.
internal sealed record SeedEvent(
    int Id,
    string? Value,
    string? ValueSha256,
    string? Kind,
    string? Address
);

// Matches the JSON expected by the Python driver.
internal sealed record SeedResult(
    int Id,
    string Key,
    int BlockSize,
    string BlockSha256,
    string Engine
);
