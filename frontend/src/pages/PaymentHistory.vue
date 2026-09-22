<script setup>
import { onMounted, ref } from 'vue'
import { getJSON } from '../api'
const items = ref([])
const open = ref(null)
const summary = (h) => {
  const r = JSON.parse(h.result_json)
  if (h.kind === 'balance_asof') return `第${r.period}期 剩余本金 ${r.balance}(当时快照)`
  if (h.kind === 'schedule') return `月供 ${r.monthly_payment}`
  return h.kind
}
const toggle = (h) => {
  if (open.value === h.id) { open.value = null; return }
  open.value = h.id
  h._in = JSON.parse(h.input_json); h._out = JSON.parse(h.result_json)
}
onMounted(async () => { items.value = (await getJSON('/api/history')).items })
</script>
<template><div class="page"><h1>试算记录</h1><table>
<tr><th>#</th><th>类型</th><th>摘要</th><th>时间</th></tr>
<template v-for="h in items" :key="h.id">
<tr @click="toggle(h)" class="row"><td>#{{ h.id }}</td><td>{{ h.kind }}</td><td>{{ summary(h) }}</td><td>{{ h.created_at }}</td></tr>
<tr v-if="open === h.id"><td colspan="4">
<p v-if="h.kind === 'balance_asof'">第{{ h._out.period }}期期末余额 <span class="hero-num">{{ h._out.balance }}</span>
 · 当期本金 {{ h._out.principal }} · 当期利息 {{ h._out.interest }} · 已还本金合计 {{ h._out.principal_paid }}</p>
<p>入参:本金 {{ h._in.principal }} · 年利率 {{ h._in.annual_rate }}% · {{ h._in.months }}期<template v-if="h._in.period"> · 目标期 {{ h._in.period }}</template></p>
</td></tr>
</template>
</table></div></template>
<style scoped>
.row { cursor: pointer; }
</style>
