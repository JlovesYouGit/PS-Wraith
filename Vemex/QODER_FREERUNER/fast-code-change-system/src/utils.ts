/**
 * Validates if a string is a well-formed SHA-256 hash.
 * @param hash The string to validate.
 * @returns True if the hash is a valid SHA-256 hash, false otherwise.
 */
export function isValidSha256(hash: string): boolean {
  if (typeof hash !== 'string' || hash.length !== 64) {
    return false;
  }
  const hexRegex = /^[a-f0-9]{64}$/;
  return hexRegex.test(hash);
}
