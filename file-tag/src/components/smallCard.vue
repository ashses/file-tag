<!-- card组件：传入参数(标题,html or VNode渲染成html) -->
<template>
  <div id="cardContainer">
    <div id="cardTitle">
      <div id="titleFont">{{ title }}</div>
    </div>
    <div id="cardBody">
      <div v-if="tableData">
        <verticalTable :data="tableData"></verticalTable>
      </div>
      <div v-else v-html="html"></div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import verticalTable from './verticalTable.vue'
import { verticalTableInstance } from '@/typing/class'

export default defineComponent({
  setup() {
    return {}
  },
  components: {
    verticalTable: verticalTable
  },
  props: {
    title: String,
    html: String,
    tableData: verticalTableInstance
  }
})
</script>

<style scoped>
#cardContainer {
  width: 90%;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  background-color: #f5f5f5;
  margin: 10px auto;
  height: min-content;
  border-radius: 10px 10px 10px 10px;
  overflow: hidden;
}

#cardTitle {
  width: 100%;
  background-color: #c8c8c8;
  border-bottom: 1px solid #ccc;
  padding: 10px;
  font-weight: bold;
  color: #333;
}

#titleFont {
  color: #333;
  font-weight: bold;
}

#cardBody {
  padding: 10px;
}
</style>
