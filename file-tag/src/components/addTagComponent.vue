<template>
  <n-modal :show="addTagModalActive">
    <template #default>
      <div id="addTagContainer">
        <div id="rootInfo">
          <span
            >当前标签父标签: <span>{{ tagForm.parent_name.value }}</span></span
          >
        </div>
        <div id="inputSection">
          <div id="inputGroup">
            <n-form :ref="formRef">
              <n-form-item path="tag_name" label="标签名">
                <n-input
                  v-model:value="tagForm.tag_name.value"
                  placeholder="请输入标签名"
                  @keydown.enter.prevent
                ></n-input>
              </n-form-item>
              <n-form-item path="extra" label="备注">
                <n-input
                  type="textarea"
                  placeholder="请输入备注"
                  v-model:value="tagForm.extra.value"
                  @keydown.enter.prevent
                ></n-input>
              </n-form-item>
            </n-form>
          </div>
          <div id="buttonGroup">
            <div id="cancel">
              <n-button @click="closeModal(false)" :loading="loading">取消</n-button>
            </div>
            <div id="append" v-if="editMod">
              <n-button :loading="loading" @click="handleUpdateTag">修改</n-button>
            </div>
            <div id="tagEdit" v-else>
              <n-button :loading="loading" @click="handleCreateTag">添加</n-button>
            </div>
          </div>
        </div>
        <div></div>
      </div>
    </template>
  </n-modal>
</template>

<script lang="ts">
import { defineComponent, onMounted, ref } from 'vue'
import { type FormInst } from 'naive-ui'
import { addTag, getTagById, updateTag } from '@/models/api/fileTag'
export default defineComponent({
  setup(props) {
    const formRef = ref<FormInst | null>(null)
    const loading = ref<boolean>(false)
    const tagForm = {
      id: ref<number>(-1),
      tag_name: ref<string>(''),
      extra: ref<string>(''),
      parent_id: ref<number>(-1),
      parent_name: ref<string>('根标签')
    }

    const handleCreateTag = async () => {
      if (tagForm.tag_name.value !== '') {
        loading.value = true
        const data = await addTag(
          tagForm.tag_name.value,
          tagForm.parent_id.value,
          tagForm.extra.value
        )
        if (!data.error) {
          window.$message.success('创建成功')
        }
        loading.value = false
      }
    }

    onMounted(async () => {
      if (props.tag && props.editMod && props.tag.id !== -1) {
        // 编辑模式
        const data = await getTagById(props.tag.id)
        if (data.data) {
          tagForm.id.value = props.tag.id
          tagForm.tag_name.value = data.data.tag_name
          tagForm.extra.value = data.data.extra
          tagForm.parent_id.value = data.data.parent_id
          tagForm.parent_name.value = data.data.parent_tag_name
        } else {
          window.$message.error('tag对象不存在')
        }
      } else {
        if (props.tag && props.tag.parent_id !== -1) {
          const data = await getTagById(props.tag.parent_id)
          if (data.data) {
            tagForm.parent_name.value = data.data.tag_name
            tagForm.parent_id.value = props.tag.parent_id
          } else {
            tagForm.parent_name.value = '根标签'
            tagForm.parent_id.value = -1
          }
          tagForm.id.value = -1
          tagForm.tag_name.value = ''
          tagForm.extra.value = ''
        }
      }
    })
    return {
      loading: loading,
      formRef: formRef,
      tagForm: tagForm,
      handleCreateTag: handleCreateTag
    }
  },
  props: {
    addTagModalActive: Boolean,
    editMod: Boolean,
    tag: Object
  },
  methods: {
    closeModal(v: boolean) {
      this.tagForm.id.value = -1
      this.tagForm.tag_name.value = ''
      this.tagForm.extra.value = ''
      this.tagForm.parent_id.value = -1
      this.tagForm.parent_name.value = '根标签'
      this.$emit('update:addTagModalActive', v)
    },
    async handleUpdateTag() {
      if (this.tagForm.tag_name.value !== '') {
        this.loading = true
        const data = await updateTag(
          this.tagForm.id.value,
          this.tagForm.parent_id.value,
          this.tagForm.extra.value,
          this.tagForm.tag_name.value
        )
        if (!data.error) {
          window.$message.success('修改成功')
          this.closeModal(false)
        }
      }
    }
  }
})
</script>

<style src="../assets/addTagModal.css"></style>

<style scoped></style>
