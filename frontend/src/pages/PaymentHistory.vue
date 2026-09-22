<script setup>
import { onMounted, ref } from 'vue'
import { getJSON } from '../api'
const items = ref([])
const parse = (s) => { try { return JSON.parse(s) } catch { return null } }
onMounted(async () => { items.value = (await getJSON('/api/history')).items })
</script>
<template><div class="page"><h1>试算记录</h1><table>
<tr><th>#</th><th>类型</th><th>时间</th><th>内容</th></tr>
<tr v-for="h in items" :key="h.id">
  <td>#{{ h.id }}</td>
  <td>{{ h.kind }}</td>
  <td>{{ h.created_at }}</td>
  <td>
    <template v-if="h.kind === 'balance_asof'">
      第{{ parse(h.result_json)?.period ?? parse(h.input_json)?.target_period }}期期末余额
      <b>{{ parse(h.result_json)?.balance }}</b>
      <span class="muted">（钉选时利率 {{ parse(h.input_json)?.annual_rate }}%）</span>
    </template>
    <template v-else-if="h.kind === 'schedule'">
      月供 {{ parse(h.result_json)?.monthly_payment }}
    </template>
  </td>
</tr>
</table></div></template>
