// [PROTOTYP] Auto-Claude: Spielzeug-Baum für einen Board-Lauf. Nur Gerüst.
//
//   Plan ──► Slice A ─┐
//        └─► Slice B ─┴─► Review
//
// Aufruf in einer Session (Workflow-Tool, nur nach ausdrücklicher Freigabe durch den Menschen):
//   Workflow({ name: 'auto-claude', args: { board: 12 } })
//   Workflow({ name: 'auto-claude', args: { spec: 'docs/specs/0002-items-by-id.md', dryRun: true } })
//
// args:
//   board   Nummer des Board-Issues (optional; sonst spec)
//   spec    Pfad zur Spec (Standard: docs/specs/0002-items-by-id.md)
//   dryRun  true (Standard): Slices nur planen und beschreiben, nichts ändern.
//           false: Slices in eigenen Worktrees umsetzen, Branch feature/<slug>, PR gegen main.
//
// Grenzen: maximal 2 Slices, nie mergen, nie force-pushen (CLAUDE.md). Siehe docs/auto-claude.md.

export const meta = {
  name: 'auto-claude',
  description: '[PROTOTYP] Board/Spec planen, zwei Slices parallel umsetzen, gemeinsam reviewen',
  whenToUse: 'Spielzeug-Lauf des Bravo-Ablaufs: Plan -> 2 parallele Slices -> Review',
  phases: [
    { title: 'Plan', detail: 'Spec lesen, in genau zwei Slices schneiden' },
    { title: 'Slices', detail: 'zwei Slices parallel, je eigener Worktree' },
    { title: 'Review', detail: 'Diff beider Slices gegen Spec und CLAUDE.md prüfen' },
  ],
}

const input = args || {}
const dryRun = input.dryRun !== false
const spec = input.spec || 'docs/specs/0002-items-by-id.md'
const source = input.board ? `Board-Issue #${input.board} (inkl. Spec und Sub-Issues)` : spec

const PLAN_SCHEMA = {
  type: 'object',
  properties: {
    ziel: { type: 'string' },
    slices: {
      type: 'array',
      minItems: 2,
      maxItems: 2,
      items: {
        type: 'object',
        properties: {
          slug: { type: 'string', description: 'kebab-case, wird zu feature/<slug>' },
          titel: { type: 'string' },
          aufgabe: { type: 'string' },
          akzeptanz: { type: 'array', items: { type: 'string' } },
          dateien: { type: 'array', items: { type: 'string' } },
        },
        required: ['slug', 'titel', 'aufgabe', 'akzeptanz'],
      },
    },
  },
  required: ['ziel', 'slices'],
}

const SLICE_SCHEMA = {
  type: 'object',
  properties: {
    slug: { type: 'string' },
    status: { type: 'string', enum: ['geplant', 'umgesetzt', 'blockiert'] },
    branch: { type: 'string' },
    pr: { type: 'string', description: 'PR-URL oder leer' },
    verify: { type: 'string', enum: ['grün', 'rot', 'nicht gelaufen'] },
    zusammenfassung: { type: 'string' },
    annahmen: { type: 'array', items: { type: 'string' } },
  },
  required: ['slug', 'status', 'verify', 'zusammenfassung'],
}

const REVIEW_SCHEMA = {
  type: 'object',
  properties: {
    urteil: { type: 'string', enum: ['ok', 'nacharbeit'] },
    befunde: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          slug: { type: 'string' },
          schwere: { type: 'string', enum: ['blocker', 'hinweis'] },
          text: { type: 'string' },
        },
        required: ['slug', 'schwere', 'text'],
      },
    },
  },
  required: ['urteil', 'befunde'],
}

// 1. Plan: genau zwei vertikale Slices (Skill plan-to-issues als Maßstab).
phase('Plan')
const plan = await agent(
  `Lies ${source} und schneide die Arbeit nach dem Skill .claude/skills/plan-to-issues in GENAU ` +
    'zwei vertikale Slices, die unabhängig voneinander umsetzbar sind (keine gemeinsamen ' +
    'Dateien außer Tests/Doku, falls vermeidbar). Ändere nichts.',
  { label: 'plan', schema: PLAN_SCHEMA },
)
if (!plan) {
  return { status: 'abgebrochen', grund: 'Plan fehlgeschlagen' }
}
log(`Plan: ${plan.slices.map((s) => s.slug).join(', ')}`)

// 2. Slices: parallel, im dryRun nur beschreiben, sonst je Worktree umsetzen.
const slicePrompt = (s) =>
  dryRun
    ? `DRY RUN, ändere nichts. Beschreibe, wie du den Slice "${s.titel}" umsetzen würdest: ` +
      `Dateien, Tests, Risiken. Aufgabe: ${s.aufgabe}. Akzeptanz: ${s.akzeptanz.join('; ')}.`
    : `Setze den Slice "${s.titel}" um. Aufgabe: ${s.aufgabe}. ` +
      `Akzeptanz (je ein Test): ${s.akzeptanz.join('; ')}. ` +
      `Branch feature/${s.slug} ab main, make verify muss grün sein, Annahmen in ` +
      'docs/ASSUMPTIONS.md, PR gegen main mit Beschreibung ab [PROTOTYP]. Nicht mergen.'

const slices = await parallel(
  plan.slices.map((s) => () =>
    agent(slicePrompt(s), {
      label: `slice:${s.slug}`,
      phase: 'Slices',
      schema: SLICE_SCHEMA,
      ...(dryRun ? {} : { isolation: 'worktree' }),
    }),
  ),
)
const done = slices.filter(Boolean)
if (done.length < plan.slices.length) {
  log(`${plan.slices.length - done.length} Slice(s) ohne Ergebnis, Review nur über den Rest`)
}

// 3. Review: Barriere bewusst, weil der Reviewer beide Slices gemeinsam sehen soll
//    (Überschneidungen, widersprüchliche Annahmen).
phase('Review')
const review = await agent(
  'Prüfe beide Slices gemeinsam gegen die Spec ' +
    `(${spec}) und CLAUDE.md: Akzeptanzkriterien abgedeckt, Tests vorhanden, keine Konflikte ` +
    'zwischen den Slices, keine Secrets, keine KI-Hinweise in Commits. ' +
    (dryRun ? 'DRY RUN: bewerte die Pläne. ' : 'Lies die PR-Diffs. Kommentiere nichts. ') +
    `Ergebnisse: ${JSON.stringify(done)}`,
  { label: 'review', schema: REVIEW_SCHEMA },
)

return { dryRun, ziel: plan.ziel, slices: done, review }
