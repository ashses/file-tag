<template>
  <n-modal :show="activeModal">
    <template #default>
      <div id="modal">
        <div id="inputGroup">
          <div id="dragSection" v-if="!editMode">
            <n-upload
              abstract
              multiple
              directory
              directory-dnd
              :default-upload="false"
              v-model:file-list="fileList"
            >
              <n-upload-trigger #="{ handleClick, handleDrop }" abstract>
                <n-button-group
                  ><n-button @click="handleClick" @drag="handleDrop" :loading="loading"
                    >点击批量添加</n-button
                  >
                  <n-button @click="handleClear" :loading="loading">清空</n-button></n-button-group
                >
              </n-upload-trigger>
              <n-card style="margin-top: 10px" title="文件列表">
                <n-upload-file-list id="fileListShow" />
              </n-card>
            </n-upload>
          </div>
          <div v-else></div>
          <div id="inputSection">
            <n-form :ref="formRef" :model="fileTagForm" :rules="rules">
              <n-form-item path="file_name" label="文件名">
                <n-input
                  v-model:value="fileTagForm.file_name"
                  :disabled="fileList.length !== 0"
                  placeholder="请输入文件名"
                  @keydown.enter.prevent
                ></n-input>
              </n-form-item>
              <n-form-item path="abs_path" label="绝对路径">
                <n-input
                  v-model:value="fileTagForm.abs_path"
                  @keydown.enter.prevent
                  placeholder="请输入文件或文件夹的绝对路径"
                  :disabled="fileList.length !== 0 || editMode"
                ></n-input>
              </n-form-item>
              <n-form-item path="extra" label="备注">
                <n-input
                  type="textarea"
                  placeholder="请输入备注"
                  v-model:value="fileTagForm.extra"
                  @keydown.enter.prevent
                ></n-input>
              </n-form-item>
            </n-form>
          </div>
          <div id="tagSelector">
            <n-card title="可选标签" id="tagSelectorCard">
              <n-tree
                id="tagSelectorTree"
                virtual-scroll
                :data="treeData"
                block-line
                expand-on-click
                checkable
                v-model:checked-keys="fileTagForm.tags"
              ></n-tree>
            </n-card>
          </div>
        </div>
        <div id="operationGroup">
          <div id="close">
            <n-button @click="closeModal(false)" :loading="loading">关闭</n-button>
          </div>
          <div id="submit" v-if="!editMode">
            <n-button @click="handleAddFile" :loading="loading">添加</n-button>
          </div>
          <div id="edit" v-else>
            <n-button @click="handleSaveFile" :loading="loading">保存</n-button>
          </div>
        </div>
      </div>
    </template>
  </n-modal>
</template>

<script lang="ts">
import { defineComponent, onMounted, ref, toRaw } from 'vue'
import type { UploadFileInfo } from 'naive-ui'
import { type FormInst } from 'naive-ui'
import { validateAddFileRule } from '@/utils/validate'
import { addFile, addFileBatch, saveFile } from '@/models/api/fileTag'

export default defineComponent({
  setup(props) {
    const fileTagForm = ref<TagFile.createFile>({
      file_name: '',
      abs_path: '',
      extra: '',
      tags: []
    })
    const editFileId = ref<number>(-1)
    const loading = ref<boolean>(false)
    const checkedTag = ref<number[]>([])

    onMounted(async () => {
      if (props.editMode) {
        if (props.file) {
          editFileId.value = props.file.id
          fileTagForm.value.abs_path = props.file.abs_path
          fileTagForm.value.file_name = props.file.file_name
          fileTagForm.value.extra = props.file.extra
          for (let t of props.file.tags) {
            fileTagForm.value.tags.push(t.id)
          }
        }
      } else {
        fileTagForm.value.abs_path = ''
        fileTagForm.value.file_name = ''
        fileTagForm.value.extra = ''
        fileTagForm.value.tags = []
      }
    })

    const formRef = ref<FormInst | null>(null)

    const fileList = ref<UploadFileInfo[]>([])

    return {
      fileTagForm: fileTagForm,
      fileList: fileList,
      rules: validateAddFileRule,
      formRef: formRef,
      checkedTag: checkedTag,
      loading: loading,
      editFileId: editFileId
    }
  },
  props: {
    activeModal: Boolean,
    treeData: Object,
    editMode: Boolean,
    file: Object
  },
  methods: {
    handleClear() {
      this.fileList = []
    },
    closeModal(v: boolean) {
      this.fileTagForm.abs_path = ''
      this.fileTagForm.file_name = ''
      this.fileTagForm.extra = ''
      this.fileTagForm.tags = []
      this.fileList = []
      this.$emit('update:activeModal', v)
    },
    async handleSaveFile() {
      this.loading = true
      console.log(
        this.editFileId,
        this.fileTagForm.file_name,
        this.fileTagForm.extra,
        toRaw(this.fileTagForm.tags)
      )
      const data = await saveFile(
        this.editFileId,
        this.fileTagForm.file_name,
        this.fileTagForm.extra,
        toRaw(this.fileTagForm.tags)
      )
      if (!data.error) {
        window.$message.success('成功')
        this.closeModal(false)
      }
      this.loading = false
    },
    async handleAddFile() {
      this.loading = true
      if (this.fileList.length > 0) {
        // 批量添加
        const filePathList: any[] = []
        this.fileList.forEach((item) => {
          filePathList.push(item.file?.path)
        })
        const data = await addFileBatch(
          filePathList,
          this.fileTagForm.extra,
          toRaw(this.fileTagForm.tags)
        )
        if (!data.error) {
          window.$message.success('添加成功')
        }
      } else {
        // 单个添加
        if (this.fileTagForm.file_name == '' || this.fileTagForm.abs_path == '') {
          window.$message.error('请输入文件名和路径')
          return
        }
        const data = await addFile(
          this.fileTagForm.file_name,
          this.fileTagForm.abs_path,
          this.fileTagForm.extra,
          toRaw(this.fileTagForm.tags)
        )
        if (!data.error) {
          window.$message.success('添加成功')
        }
      }
      this.loading = false
    }
  }
})
</script>

<style src="../assets/addFileModal.css"></style>

<style scoped></style>
