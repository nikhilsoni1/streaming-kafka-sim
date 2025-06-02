import { uniqueNamesGenerator, animals } from 'unique-names-generator';

export function generateRunId(upper = false) {
  const base = uniqueNamesGenerator({
    dictionaries: [animals],
    style: upper ? 'upperCase' : 'lowerCase',
  });

  const suffix = Math.random().toString(36).substring(2, 6);
  return `${base}-${upper ? suffix.toUpperCase() : suffix}`;
}
