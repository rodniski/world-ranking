import { query } from "./_generated/server";
import { v } from "convex/values";

/** Todos os scrapes de um run especifico. */
export const byRun = query({
  args: { run_id: v.id("runs") },
  handler: async (ctx, { run_id }) => {
    return await ctx.db
      .query("scrapes")
      .withIndex("by_run", (q) => q.eq("run_id", run_id))
      .collect();
  },
});

/**
 * Snapshot mais recente de um indicador para um pais.  Usa `_creationTime`
 * implicito da tabela: inserts sao ordenados, entao `order("desc").first()`
 * devolve o ultimo valor coletado.
 */
export const latest = query({
  args: { iso3: v.string(), indicator_id: v.string() },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("scrapes")
      .withIndex("by_iso3_indicator", (q) =>
        q.eq("iso3", args.iso3).eq("indicator_id", args.indicator_id),
      )
      .order("desc")
      .first();
  },
});

/** Historico de um indicador para um pais especifico (mais novo primeiro). */
export const history = query({
  args: {
    iso3: v.string(),
    indicator_id: v.string(),
    limit: v.optional(v.number()),
  },
  handler: async (ctx, args) => {
    const limit = args.limit ?? 50;
    return await ctx.db
      .query("scrapes")
      .withIndex("by_iso3_indicator", (q) =>
        q.eq("iso3", args.iso3).eq("indicator_id", args.indicator_id),
      )
      .order("desc")
      .take(limit);
  },
});
