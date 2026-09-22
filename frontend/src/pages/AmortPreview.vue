<script setup>
import { ref } from 'vue'
import { postJSON } from '../api'
const out = ref(null)
const targetPeriod = ref(12)
const asof = ref(null)
const asofErr = ref('')
const load = async (previewRows = 12) => { out.value = await postJSON('/api/schedule', { principal: 1000000, annual_rate: 3.5, months: 360, persist: false, preview_rows: previewRows }) }
load()
const queryAsof = async () => {
  asofErr.value = ''
  try {
    const p = Number(targetPeriod.value)
    asof.value = await postJSON('/api/balance-asof', { principal: 1000000, annual_rate: 3.5, months: 360, target_period: p, persist: false })
    if (!out.value || p > out.value.preview.length) await load(Math.max(12, p))
  } catch (e) { asofErr.value = '目标期须在 1 到总期数之间'; asof.value = null }
}
</script>
<template><div class="page"><h1>摊还表预览</h1>
<div class="asof-bar">
  <label>目标期 <input v-model.number="targetPeriod" min="1" max="360" /></label>
  <button @click="queryAsof">查剩余本金</button>
  <span v-if="asofErr" class="err">{{ asofErr }}</span>
</div>
<div v-if="asof" class="asof-card">
  第{{ asof.period }}期期末余额 <b>{{ asof.balance }}</b>
  · 该期本金 {{ asof.principal }} · 该期利息 {{ asof.interest }}
  · 已还本金合计 {{ asof.principal_paid }}
</div>
<table v-if="out"><tr v-for="r in out.preview" :key="r.period" :class="{ hl: asof && r.period === asof.period }"><td>第{{ r.period }}期</td><td>{{ r.payment }}</td><td>{{ r.balance }}</td></tr></table>
</div></template>
