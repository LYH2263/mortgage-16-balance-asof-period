<script setup>
import { ref } from 'vue'
import { postJSON } from '../api'
const principal = ref(800000)
const annual_rate = ref(4.2)
const months = ref(360)
const period = ref(60)
const persist = ref(false)
const out = ref(null)
const asof = ref(null)
const err = ref('')
const run = async () => {
  err.value = ''
  out.value = await postJSON('/api/schedule', { principal: principal.value, annual_rate: annual_rate.value, months: months.value, persist: true })
}
const query = async () => {
  err.value = ''; asof.value = null
  try {
    asof.value = await postJSON('/api/schedule/balance-asof', {
      principal: principal.value, annual_rate: annual_rate.value, months: months.value,
      period: period.value, persist: persist.value,
    })
  } catch (e) { err.value = `第 ${period.value} 期超出范围(1..${months.value}),未写入记录` }
}
</script>
<template><div class="page"><h1>等额本息试算</h1>
<label>本金 <input v-model.number="principal" /></label>
<label>年利率% <input v-model.number="annual_rate" /></label>
<label>月数 <input v-model.number="months" /></label>
<button @click="run">计算</button>
<p v-if="out">月供 {{ out.monthly_payment }} · 利息合计 {{ out.total_interest }}</p>
<h2>指定期剩余本金</h2>
<label>目标期 <input v-model.number="period" type="number" min="1" :max="months" /></label>
<label><input v-model="persist" type="checkbox" /> 写入记录</label>
<button @click="query">查余额</button>
<p v-if="err" class="err">{{ err }}</p>
<template v-if="asof">
<p>第{{ asof.period }}期期末余额 <span class="hero-num">{{ asof.balance }}</span>
 · 当期本金 {{ asof.principal }} · 当期利息 {{ asof.interest }} · 已还本金合计 {{ asof.principal_paid }}<template v-if="asof.run_id"> · 记录#{{ asof.run_id }}</template></p>
</template>
<table v-if="out"><tr><th>期</th><th>月供</th><th>本金</th><th>利息</th><th>期末余额</th></tr>
<tr v-for="r in out.preview" :key="r.period" :class="{ hit: asof && r.period === asof.period }">
<td>{{ r.period }}</td><td>{{ r.payment }}</td><td>{{ r.principal }}</td><td>{{ r.interest }}</td><td>{{ r.balance }}</td></tr></table>
</div></template>
<style scoped>
.err { color: #a33; }
tr.hit td { background: #f3e2c7; font-weight: 700; }
h2 { font-size: 1rem; }
</style>
