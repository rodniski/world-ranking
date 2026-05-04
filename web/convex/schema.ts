import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

// Camada de observabilidade do pipeline ETL Python.
//
// `runs`     — manifest de cada execucao de coletor (1 linha por run).
// `scrapes`  — snapshot historico bruto: 1 linha por (run, iso3, indicator).
//
// `data/raw/` em CSV continua sendo a fonte canonica versionada em git;
// Convex acumula historico que CSV nao tem (ex: comparar BRA na GII em
// jan vs mai).  Convex nao bloqueia o pipeline — falhar upload so loga warn.
export default defineSchema({
  runs: defineTable({
    source_id: v.string(),
    started_at: v.number(),
    finished_at: v.number(),
    status: v.union(v.literal("ok"), v.literal("failed")),
    error: v.optional(v.string()),
    n_rows: v.number(),
    n_countries: v.number(),
  })
    .index("by_source", ["source_id"])
    .index("by_started_at", ["started_at"]),

  scrapes: defineTable({
    run_id: v.id("runs"),
    source_id: v.string(),
    iso3: v.string(),
    indicator_id: v.string(),
    value: v.number(),
    year: v.number(),
  })
    .index("by_run", ["run_id"])
    .index("by_source_indicator", ["source_id", "indicator_id"])
    .index("by_iso3_indicator", ["iso3", "indicator_id"]),
});
