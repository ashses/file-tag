<script lang="ts">
import messageComponent from './components/messageComponent.vue'
import { NMessageProvider, NModalProvider, NSpace, NTag, type TreeDropInfo } from 'naive-ui'
import { ref, onMounted, h, toRaw, nextTick } from 'vue'
import {
  queryFile,
  deleteFileTag,
  getTags,
  updateTag,
  deleteFile,
  deleteTag,
  queryFiles
} from '@/models/api/fileTag'
import { type DataTableColumns, type TreeOption, type DropdownOption } from 'naive-ui'
import addFileTagModalComponent from './components/addFileTagModalComponent.vue'
import addTagComponent from './components/addTagComponent.vue'
import { clipboard, shell } from 'electron'
import path from 'path'
import { watch } from 'vue'

export default {
  setup() {
    const query = ref<string>('')
    const editMode = ref<boolean>(false)
    const openFileTagModalActive = ref<boolean>(false)
    const openTagModalActive = ref<boolean>(false)
    const tagEditMod = ref<boolean>(false)
    const tagFileList = ref<TagFile.tagFile[]>()
    const showIrrelevantNodes = ref<boolean>(false)
    const editTag = ref<{ id: number; parent_id: number }>({ id: -1, parent_id: -1 })
    const tagFileQueryData = {
      id: ref<number>(-1)
    }
    const pattern = ref<string>('')
    const tagListData = ref<treeOptions[] | undefined>([])
    // 文件列表右键菜单
    const getRowRef = ref<TagFile.tagFile>()
    const getNodeRef = ref<TreeOption>()
    const fileRightButtonOption: DropdownOption[] = [
      { label: '编辑', key: 'edit' },
      { label: () => h('span', { style: { color: 'red' } }, '删除'), key: 'delete' },
      { label: '打开文件所在位置', key: 'folder' }
    ]
    const TreeRightButtonOption: DropdownOption[] = [
      { label: '编辑', key: 'edit' },
      { label: '删除', key: 'delete' },
      { label: '添加子标签', key: 'append' }
    ]
    const showFileDropdownRef = ref(false)
    const showTreeDropdownRef = ref(false)
    const xFileRef = ref(0)
    const yFileRef = ref(0)
    const xNode = ref(0)
    const yNode = ref(0)
    //////
    const createFileListColumn = (): DataTableColumns<TagFile.tagFile> => {
      return [
        {
          title: '文件名',
          key: 'file_name',
          ellipsis: {
            tooltip: true
          },
          width: 100,
          render(row) {
            return h(
              'a',
              {
                onClick: () => {
                  shell.openPath(row.abs_path)
                }
              },
              {
                default: () => {
                  return row.file_name
                }
              }
            )
          }
        },
        {
          title: '文件绝对路径',
          key: 'abs_path',
          ellipsis: {
            tooltip: true
          },
          width: 100,
          render(row) {
            return h(
              'a',
              {
                onClick: () => {
                  clipboard.writeText(row.abs_path)
                  window.$message.success('已复制到剪切板')
                }
              },
              {
                default: () => {
                  return row.abs_path
                }
              }
            )
          }
        },
        {
          title: '文件大小',
          key: 'file_size',
          width: 100,
          render(row) {
            return h(
              'div',
              { style: 'padding:10px' },
              { default: () => `${Number(row.file_size).toFixed(2)}${row.file_size_unit}` }
            )
          }
        },
        {
          title: '文件类型',
          key: 'file_base_type',
          width: 50
        },
        { title: '创建时间', key: 'create_at', width: 150 },
        {
          title: '标签',
          key: 'tags',
          width: 200,
          render(row) {
            var VNodeList: any[] = []
            for (const tag of row.tags) {
              VNodeList.push(
                h(
                  NTag,
                  {
                    bordered: false,
                    type: 'success',
                    closable: true,
                    onClose: async () => {
                      await handleDeleteFileTag(row.id, tag.id)
                    }
                  },
                  {
                    default: () => `${tag.tag_name}`
                  }
                )
              )
            }
            return h(NSpace, { style: 'overflew-x:auto' }, VNodeList)
          }
        },
        { title: '备注', key: 'extra', width: 100, ellipsis: { tooltip: true } }
      ]
    }
    const createNodeProps = ({ option }: { option: TreeOption }) => {
      return {
        onClick: async () => {
          if (option.key) {
            tagFileQueryData.id.value = Number(option.key)
            tagFileList.value = await handleQueryFile(tagFileQueryData.id.value)
          } else {
            window.$message.error('对象不存在')
          }
        },
        oncontextmenu: async (e: MouseEvent) => {
          e.preventDefault()
          showTreeDropdownRef.value = false
          getNodeRef.value = option
          nextTick().then(() => {
            showTreeDropdownRef.value = true
            xNode.value = e.clientX
            yNode.value = e.clientY
          })
        }
      }
    }

    const openFileTagModal = () => {
      editMode.value = false
      openFileTagModalActive.value = true
    }

    const openTagModal = () => {
      editTag.value.parent_id = -1
      tagEditMod.value = false
      openTagModalActive.value = true
    }

    const createTree = (tags: TagFile.tags[]): treeOptions[] => {
      const tree = ref<treeOptions[]>([])
      for (var tag of tags) {
        tree.value.push({
          label: tag.tag_name,
          key: tag.id,
          children: createTree(tag.child_tags)
        })
      }
      return tree.value
    }

    function findSiblingsAndIndex(
      node: TreeOption,
      nodes?: TreeOption[],
      parent_id: number = -1
    ): [TreeOption[], number, number] | [null, null, null] {
      if (!nodes) return [null, null, null]
      for (let i = 0; i < nodes.length; ++i) {
        const siblingNode = nodes[i]
        if (siblingNode.key === node.key) return [nodes, i, parent_id]
        const [siblings, index, parent_id_key] = findSiblingsAndIndex(
          node,
          siblingNode.children,
          Number(siblingNode.key)
        )
        if (siblings && index !== null) return [siblings, index, parent_id_key]
      }
      return [null, null, null]
    }

    async function handleDeleteFileTag(file_id: number, tag_id: number) {
      const data = await deleteFileTag(file_id, [tag_id])
      if (!data.error) {
        tagFileList.value = await handleQueryFile(tagFileQueryData.id.value)
        window.$message.success('标签移除成功')
      }
    }

    async function handleQueryFile(tag: number) {
      const data = await queryFile(tag)
      if (data.data) {
        return data.data
      } else {
        return []
      }
    }

    async function handleGetTagsTree() {
      const data = await getTags()
      if (data.data) {
        return toRaw(createTree(data.data))
      } else {
        return []
      }
    }

    async function handleShowAll() {
      tagFileQueryData.id.value = -1
      tagFileList.value = await handleQueryFile(-1)
    }

    async function handleDrop({ node, dragNode, dropPosition }: TreeDropInfo) {
      const [dragNodeSiblings, dragNodeIndex] = findSiblingsAndIndex(dragNode, tagListData.value)
      if (dragNodeSiblings === null || dragNodeIndex === null) return
      dragNodeSiblings.splice(dragNodeIndex, 1)
      if (dropPosition === 'inside') {
        const data = await updateTag(Number(dragNode.key), Number(node.key))
        if (!data.error) {
          window.$message.success('修改成功')
          if (node.children) {
            node.children.unshift(dragNode)
          } else {
            node.children = [dragNode]
          }
        }
      } else if (dropPosition === 'before') {
        const [nodeSiblings, nodeIndex, parent_id] = findSiblingsAndIndex(node, tagListData.value)
        if (nodeSiblings === null || nodeIndex === null || parent_id === null) return
        const data = await updateTag(Number(dragNode.key), parent_id)
        if (!data.error) {
          window.$message.success('修改成功')
          nodeSiblings.splice(nodeIndex, 0, dragNode)
        }
      } else if (dropPosition === 'after') {
        const [nodeSiblings, nodeIndex, parent_id] = findSiblingsAndIndex(node, tagListData.value)
        if (nodeSiblings === null || nodeIndex === null || parent_id === null) return
        const data = await updateTag(Number(dragNode.key), parent_id)
        if (!data.error) {
          window.$message.success('修改成功')
          nodeSiblings.splice(nodeIndex + 1, 0, dragNode)
        }
      }
    }

    async function handleQuery() {
      const data = await queryFiles(query.value)
      if (data.data) {
        tagFileList.value = data.data
      }
    }

    // 文件列表下拉菜单
    const rowProps = (row: TagFile.tagFile) => {
      return {
        oncontextmenu: (e: MouseEvent) => {
          e.preventDefault()
          showFileDropdownRef.value = false
          getRowRef.value = row
          nextTick().then(() => {
            showFileDropdownRef.value = true
            xFileRef.value = e.clientX
            yFileRef.value = e.clientY
          })
        }
      }
    }

    async function handleFileDropDownSelect(key: string | number) {
      if (getRowRef.value) {
        switch (key) {
          case 'edit': {
            // 文件编辑视图
            openFileTagModalActive.value = true
            editMode.value = true
            showFileDropdownRef.value = false
            break
          }
          case 'delete': {
            const data = await deleteFile(getRowRef.value.id)
            if (!data.error) {
              tagFileList.value = await handleQueryFile(tagFileQueryData.id.value)
              window.$message.success('删除成功')
            }
            break
          }
          case 'folder': {
            if (getRowRef.value.file_base_type === '目录') {
              shell.openPath(getRowRef.value.abs_path)
            } else {
              const file_dir = path.dirname(getRowRef.value.abs_path)
              shell.openPath(file_dir)
            }
            break
          }
        }
      } else {
        window.$message.error('发生错误,对象不存在')
      }
      showFileDropdownRef.value = false
    }

    async function handleTreeDropDownSelect(key: string | number) {
      if (!getNodeRef.value) {
        window.$message.error('对象不存在')
        return
      }
      switch (key) {
        case 'edit': {
          // 打开编辑视图
          if (getNodeRef.value) {
            tagEditMod.value = true
            editTag.value.id = Number(getNodeRef.value.key)
            openTagModalActive.value = true
          } else {
            window.$message.error('对象不存在')
          }
          showTreeDropdownRef.value = false
          break
        }
        case 'delete': {
          const data = await deleteTag(Number(getNodeRef.value.key))
          if (!data.error) {
            window.$message.success('标签删除成功')
            tagListData.value = await handleGetTagsTree()
            tagFileList.value = await handleQueryFile(tagFileQueryData.id.value)
          }
          showTreeDropdownRef.value = false
          break
        }
        case 'append': {
          // 打开添加视图
          if (getNodeRef.value) {
            tagEditMod.value = false
            editTag.value.parent_id = Number(getNodeRef.value.key)
            openTagModalActive.value = true
          } else {
            window.$message.error('对象不存在')
          }
          showTreeDropdownRef.value = false
          break
        }
      }
    }

    function onClickOutside_Node() {
      showTreeDropdownRef.value = false
    }

    function onClickOutside() {
      showFileDropdownRef.value = false
    }
    ////

    // 监听器
    watch(openFileTagModalActive, async (newValue) => {
      if (!newValue) {
        tagFileList.value = await handleQueryFile(tagFileQueryData.id.value)
      }
    })

    watch(openTagModalActive, async (newValue) => {
      if (!newValue) {
        tagListData.value = await handleGetTagsTree()
        tagFileList.value = await handleQueryFile(tagFileQueryData.id.value)
      }
    })
    ///

    onMounted(async () => {
      tagFileList.value = await handleQueryFile(tagFileQueryData.id.value)
      tagListData.value = await handleGetTagsTree()
    })
    return {
      pagination: ref({ pageSize: 10 }),
      fileListColumn: createFileListColumn(),
      tagFileList: tagFileList,
      openFileTagModal: openFileTagModal,
      openFileTagModalActive: openFileTagModalActive,
      tagListData: tagListData,
      pattern: pattern,
      showIrrelevantNodes: showIrrelevantNodes,
      nodeProps: createNodeProps,
      handleShowAll: handleShowAll,
      handleDrop: handleDrop,
      fileRightButtonOption: fileRightButtonOption,
      showFileDropdownRef: showFileDropdownRef,
      xFileRef: xFileRef,
      yFileRef: yFileRef,
      handleFileDropDownSelect: handleFileDropDownSelect,
      onClickOutside: onClickOutside,
      rowProps: rowProps,
      handleTreeDropDownSelect: handleTreeDropDownSelect,
      onClickOutside_Node: onClickOutside_Node,
      TreeRightButtonOption: TreeRightButtonOption,
      showTreeDropdownRef: showTreeDropdownRef,
      xNode: xNode,
      yNode: yNode,
      editMode: editMode,
      getRowRef: getRowRef,
      openTagModalActive: openTagModalActive,
      tagEditMod: tagEditMod,
      openTagModal: openTagModal,
      editTag: editTag,
      query: query,
      handleQuery: handleQuery
    }
  },
  components: {
    messageComponent: messageComponent,
    NMessageProvider: NMessageProvider,
    NModalProvider: NModalProvider,
    NDialogProvider: NModalProvider,
    addFileTagModalComponent: addFileTagModalComponent,
    addTagComponent: addTagComponent
  },
  methods: {}
}
</script>

<template>
  <NMessageProvider>
    <messageComponent></messageComponent>
  </NMessageProvider>
  <NModalProvider>
    <addFileTagModalComponent
      v-model:activeModal="openFileTagModalActive"
      :treeData="tagListData"
      :editMode="editMode"
      v-model:file="getRowRef"
      :key="Number(openFileTagModalActive)"
    ></addFileTagModalComponent>
    <addTagComponent
      v-model:addTagModalActive="openTagModalActive"
      :editMod="tagEditMod"
      v-model:tag="editTag"
      :key="Number(openTagModalActive)"
    ></addTagComponent>
  </NModalProvider>
  <NDialogProvider></NDialogProvider>
  <div class="container">
    <div id="mainView">
      <div id="mainViewContent">
        <div id="operationBar">
          <div class="operationItem">
            <n-button strong ghost @click="openFileTagModal"> 添加文件 </n-button>
          </div>
          <div class="operationItem">
            <n-input-group>
              <n-button type="primary" @click="handleQuery"> 搜索 </n-button>
              <n-input
                :style="{ width: '200px' }"
                placeholder="文件名/标签/类型"
                v-model:value="query"
              />
              <n-button type="primary" ghost @click="handleQuery"> 搜索 </n-button>
            </n-input-group>
          </div>
          <div class="operationItem">
            <!-- 无内容,调整布局用的 -->
          </div>
        </div>
        <div id="searchFileList">
          <n-data-table
            id="searchFileListTable"
            size="small"
            :columns="fileListColumn"
            :data="tagFileList"
            :pagination="pagination"
            :max-height="450"
            :row-props="rowProps"
          />
          <n-dropdown
            placement="bottom-start"
            trigger="manual"
            :x="xFileRef"
            :y="yFileRef"
            :options="fileRightButtonOption"
            :show="showFileDropdownRef"
            :on-clickoutside="onClickOutside"
            @select="handleFileDropDownSelect"
          />
        </div>
      </div>
    </div>
    <div id="rightSide">
      <div id="upperTagList">
        <n-card title="标签" id="upperTagListCard">
          <div id="operationBar">
            <n-space>
              <n-input v-model:value="pattern" placeholder="搜索" />
              <n-switch v-model:value="showIrrelevantNodes">
                <template #checked> 全部 </template>
                <template #unchecked> 结果 </template>
              </n-switch>
              <div id="addTag">
                <n-button @click="openTagModal">添加根标签</n-button>
              </div>
            </n-space>
          </div>
          <div id="root"><a @click="handleShowAll">显示全部</a></div>
          <n-tree
            :node-props="nodeProps"
            :show-irrelevant-nodes="showIrrelevantNodes"
            :pattern="pattern"
            :data="tagListData"
            block-line
            virtual-scroll
            id="tagTree"
            :show-line="true"
            draggable
            @drop="handleDrop"
          ></n-tree>
          <n-dropdown
            placement="bottom-start"
            trigger="manual"
            :x="xNode"
            :y="yNode"
            :options="TreeRightButtonOption"
            :show="showTreeDropdownRef"
            :on-clickoutside="onClickOutside_Node"
            @select="handleTreeDropDownSelect"
          />
        </n-card>
      </div>
      <div id="tagProps"></div>
    </div>
  </div>
</template>

<style src="./assets/mainView.css"></style>
<style scoped></style>
