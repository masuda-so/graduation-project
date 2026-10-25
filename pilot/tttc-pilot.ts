/** Research runner: official analysis steps, local JSON persistence, no web services.
 * This is NOT the complete TttC application/pipeline orchestrator.
 */
import { readFile, mkdir, writeFile } from "node:fs/promises";
import { createHash } from "node:crypto";
import {
  defaultSystemPrompt, defaultClusteringPrompt, defaultExtractionPrompt,
  defaultDedupPrompt, defaultSummariesPrompt,
} from "../vendor/tttc-light-js/common/prompts/index.ts";
import { commentsToTree } from "../vendor/tttc-light-js/pipeline-worker/src/pipeline-steps/clustering/index.ts";
import { extractClaims } from "../vendor/tttc-light-js/pipeline-worker/src/pipeline-steps/claims/index.ts";
import { sortAndDeduplicateClaims } from "../vendor/tttc-light-js/pipeline-worker/src/pipeline-steps/sort-and-deduplicate/index.ts";
import { generateTopicSummaries } from "../vendor/tttc-light-js/pipeline-worker/src/pipeline-steps/summaries/index.ts";
import type { Comment } from "../vendor/tttc-light-js/pipeline-worker/src/pipeline-steps/types.ts";

const [inputPath, out] = process.argv.slice(2);
if (!inputPath || !out) throw new Error("input.json と出力先が必要です。");
const raw = await readFile(inputPath);
const comments: Comment[] = JSON.parse(raw.toString("utf8"));
if (!Array.isArray(comments) || comments.length < 15 || comments.length > 30 ||
    new Set(comments.map(c => c.id)).size !== comments.length ||
    comments.some(c => !c.id || !c.speaker || !c.text)) {
  throw new Error("入力は一意なid・speaker・textを持つ15〜30件が必要です。");
}
if (process.argv.includes("--check-input")) {
  console.log("公式ステップのimportと入力検証が完了。API呼び出しなし。");
  process.exit(0);
}
if (!process.env.OPENAI_API_KEY) throw new Error("OPENAI_API_KEY が必要です。");
await mkdir(out, {recursive: true});
const model = process.env.PILOT_MODEL || "gpt-4o-mini";
const config = (prompt: string) => ({
  model_name: model,
  system_prompt: defaultSystemPrompt + "\nWrite all generated labels, claims, and summaries in Japanese. Keep source quotes in their original language.",
  user_prompt: prompt,
});
const configs = {
  clustering: config(defaultClusteringPrompt), claims: config(defaultExtractionPrompt),
  deduplication: config(defaultDedupPrompt), summaries: config(defaultSummariesPrompt),
};
await writeFile(`${out}/prompts.json`, JSON.stringify(configs, null, 2));
await writeFile(`${out}/run.json`, JSON.stringify({
  model, input_sha256: createHash("sha256").update(raw).digest("hex"),
  sort: "numPeople", enableWeave: false,
  scope: "official step functions; no cruxes, bridging, web UI, queue, Redis, or GCS",
  prompt_change: "Japanese output instruction appended to defaultSystemPrompt",
}, null, 2));
const options = { reportId: `graduation-${Date.now()}`, userId: "synthetic-pilot", enableWeave: false, enableWandB: false };
const metrics: object[] = [];
type StepValue = { data: unknown; usage: unknown; cost: number };
type StepResult<T> = { tag: "success"; value: T } | { tag: "failure"; error: Error };
async function step<T extends StepValue>(name: string, call: () => Promise<StepResult<T>>): Promise<T> {
  const start = Date.now();
  console.log(`START ${name}`);
  try {
    const result = await call();
    if (result.tag === "failure") throw result.error;
    await writeFile(`${out}/${name}.json`, JSON.stringify(result.value, null, 2));
    metrics.push({name, seconds: (Date.now()-start)/1000, usage: result.value.usage,
      upstream_cost_estimate_usd: result.value.cost, status: "success"});
    return result.value;
  } catch (error) {
    metrics.push({name, seconds: (Date.now()-start)/1000, status: "failed"});
    await writeFile(`${out}/${name}.error.txt`, String(error));
    throw error;
  } finally {
    await writeFile(`${out}/metrics.json`, JSON.stringify(metrics, null, 2));
  }
}
const key = process.env.OPENAI_API_KEY;
const topics = await step("01-taxonomy", () => commentsToTree(comments, configs.clustering, key, undefined, options));
const claims = await step("02-claims", () => extractClaims(comments, topics.data, configs.claims, key, undefined, options));
const grouped = await step("03-grouped-claims", () => sortAndDeduplicateClaims({tree: claims.data, llm: configs.deduplication, sort: "numPeople"}, key, undefined, options));
const summaries = await step("04-topic-summaries", () => generateTopicSummaries({tree: grouped.data, llm: configs.summaries}, key, undefined, options));
await writeFile(`${out}/summaries.txt`, summaries.data.map(x => `${x.topicName}\n${x.summary}`).join("\n\n"));

// Structural trace only: presence of an ID is NOT proof of semantic preservation.
function ids(value: unknown, found = new Set<string>()): Set<string> {
  if (Array.isArray(value)) for (const x of value) ids(x, found);
  else if (value && typeof value === "object") {
    const v = value as Record<string, unknown>;
    if (typeof v.commentId === "string") found.add(v.commentId);
    for (const x of Object.values(v)) ids(x, found);
  }
  return found;
}
const extracted = ids(claims.data), deduped = ids(grouped.data);
await writeFile(`${out}/id-trace.csv`, "id,in_claims,in_grouped_including_duplicates\n" +
  comments.map(c => `${c.id},${extracted.has(c.id)},${deduped.has(c.id)}`).join("\n") + "\n");
console.log(`保存完了: ${out}`);
