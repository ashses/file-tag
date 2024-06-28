<template>
  <table>
    <tbody>
      <tr v-for="item in data?.data" :key="item.rowName">
        <th v-html="`<div>${item.rowName}</div>`"></th>
        <td v-html="`<div>${item.rowValue}</div>`"></td>
      </tr>
    </tbody>
  </table>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import { verticalTableInstance } from '@/typing/class'

export default defineComponent({
  setup() {
    return {}
  },
  props: {
    data: verticalTableInstance
  }
})
</script>

<style scoped>
table {
  width: 100%;
  border-collapse: collapse;
  margin: 10px 0;
}

th,
td {
  text-align: left;
  padding: 8px;
  border: 1px solid #ddd;
}

th {
  background-color: #f2f2f2;
  font-weight: bold;
  width: min-content;
}

tr:nth-child(even) {
  background-color: #f9f9f9;
}

tr:hover {
  background-color: #f1f1f1;
}
</style>
