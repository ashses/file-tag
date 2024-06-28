declare namespace TagFile {
  interface baseFile {
    file_name: string
    abs_path: string
    extra: string
  }

  interface tagFile extends baseFile {
    id: number
    file_base_type: string
    create_at: string
    file_size: string
    file_size_unit: string
    tags: { id: number; tag_name: string }[]
  }

  interface createFile extends baseFile {
    tags: number[]
  }

  interface baseTag {
    tag_name: string
    extra: string
  }

  interface tags extends baseTag {
    id: number
    create_time: string
    child_tags: tags[]
  }

  interface createTag extends baseTag {
    parent_tag_id: number
  }
}

interface treeOptions {
  label: string
  key: string | number
  children?: treeOptions[]
}
