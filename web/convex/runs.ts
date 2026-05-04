import { mutation, query } from "./_generated/server";
import { v } from "convex/values";

const scrapeRow = v.object({
  iso3: v.string(),
  indicator_id: v.string(),
  value: v.number(),
  year: v.number(),
});

/**
 * Grava um run completo: 1 linha em `runs` + N linhas em `scrapes`,
 * tudo dentro da mesma mutation (atomico).
 *
 * Chamado pelo pipeline Python via HTTP/api/mutation.  Sucesso devolve
 * o `run_id`; erro joga (e o cliente Python faz log.warning).
 */
export const record = mutation({
  args: {
    source_id: v.string(),
    started_at: v.number(),
    finished_at: v.number(),
    status: v.union(v.literal("ok"), v.literal("failed")),
    error: v.optional(v.string()),
    rows: v.array(scrapeRow),
  },
  handler: async (ctx, args) => {
    const uniqueIso3 = new Set(args.rows.map((r) => r.iso3));
    const runId = await ctx.db.insert("runs", {
      source_id: args.source_id,
      started_at: args.started_at,
      finished_at: args.finished_at,
      status: args.status,
      error: args.error,
      n_rows: args.rows.length,
      n_countries: uniqueIso3.size,
    });

    for (const row of args.rows) {
      await ctx.db.insert("scrapes", {
        run_id: runId,
        source_id: args.source_id,
        iso3: row.iso3,
        indicator_id: row.indicator_id,
        value: row.value,
        year: row.year,
      });
    }

    return runId;
  },
});

/**
 * Ultimos N runs, opcionalmente filtrado por `source_id`.  Usado pelo
 * dashboard pra mostrar status de coleta.
 */
export const recent = query({
  args: {
    source_id: v.optional(v.string()),
    limit: v.optional(v.number()),
  },
  handler: async (ctx, args) => {
    const limit = args.limit ?? 20;
    const sourceId = args.source_id;
    if (sourceId !== undefined) {
      return await ctx.db
        .query("runs")
        .withIndex("by_source", (q) => q.eq("source_id", sourceId))
        .order("desc")
        .take(limit);
    }
    return await ctx.db.query("runs").order("desc").take(limit);
  },
});
