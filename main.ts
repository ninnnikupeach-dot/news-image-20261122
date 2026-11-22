/**
 * Place the entry.png that lives beside this program into the competition
 * output directory as entry.png, creating that directory when it is missing.
 */
import { copyFileSync, mkdirSync, statSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const sourceImage = join(here, 'entry.png');
const outputDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
const outputImage = join(outputDir, 'entry.png');

mkdirSync(outputDir, { recursive: true });
copyFileSync(sourceImage, outputImage);

const copiedBytes = statSync(outputImage).size;
console.log(`Wrote ${outputImage} (${copiedBytes} bytes)`);
