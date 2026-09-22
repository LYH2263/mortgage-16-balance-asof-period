<script setup>
import { ref } from 'vue'
import { postJSON } from '../api'
const principal = ref(800000)
const annual_rate = ref(4.2)
const months = ref(360)
const targetPeriod = ref(120)
const out = ref(null)
const asof = ref(null)
const asofErr = ref('')
const pinAsof = ref(false)
const run = async () => { out.value = await postJSON('/api/schedule', { principal: principal.value, annual_rate: annual_rate.value, months: months.value, persist: true }) }
const queryAsof = async () => {
  asofErr.value = ''
  try {
    asof.value = await postJSON('/api/balance-asof', {
      principal: principal.value, annual_rate: annual_rate.value, months: months.value,
      target_period: Number(targetPeriod.value), persist: pinAsof.value,
    })
  } catch (e) { asofErr.value = '目标期须在 1 到总期数之间'; asof.value = null }
}
</script>
<template><div class="page"><h1>等额本息试算</h1>
<label>本金 <input v-model.number="principal" /></label>
<label>年利率% <input v-model.number="annual_rate" /></label>
<label>月数 <input v-model.number="months" /></label>
<button @click="run">计算</button>
<p v-if="out">月供 {{ out.monthly_payment }} · 利息合计 {{ out.total_interest }}</p>
<div class="asof-bar">
  <label>目标期 <input v-model.number="targetPeriod" min="1" :max="months" /></label>
  <label class="pin"><input type="checkbox" v-model="pinAsof" /> 钉选到记录</label>
  <button @click="queryAsof">查剩余本金</button>
  <span v-if="asofErr" class="err">{{ asofErr }}</span>
</div>
<div v-if="asof" class="asof-card">
  第{{ asof.period }}期期末余额 <b>{{ asof.balance }}</b>
  · 该期本金 {{ asof.principal }} · 该期利息 {{ asof.interest }}
  · 已还本金合计 {{ asof.principal_paid }}
  <span v-if="asof.run_id" class="tag">已钉选 #{{ asof.run_id }}</span>
</div>
</div></template>
