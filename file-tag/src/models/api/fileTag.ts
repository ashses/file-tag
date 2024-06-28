import { request } from '@/models/request/index'

export async function queryFile(queryTags: number) {
  return request.get<TagFile.tagFile[]>(
    '/tag/search/',
    { tag: queryTags },
    { headers: { 'Content-Type': 'application/json' } }
  )
}

export async function getTags() {
  return request.get<TagFile.tags[]>('/tag/get')
}

export async function addFile(file_name: string, abs_path: string, extra: string, tags: number[]) {
  return request.post('/file/create', {
    file_name: file_name,
    abs_path: abs_path,
    extra: extra,
    tags: tags
  })
}

export async function addFileBatch(files: string[], extra: string, tags: number[]) {
  return request.post('/file/multi/create', {
    files: files,
    extra: extra,
    tags: tags
  })
}

export async function deleteFileTag(file_id: number, tags_id: number[]) {
  return request.put('/file/update', { file_id: file_id, tags_id: tags_id, direction: 2 })
}

export async function updateTag(
  id: number,
  parent_tag_id: number = -1,
  extra: string = '',
  tag_name: string = ''
) {
  return request.put('/tag/update', {
    id: id,
    parent_tag_id: parent_tag_id,
    extra: extra,
    tag_name: tag_name
  })
}

export async function addTag(tag_name: string, parent_tag_id: number, extra: string = '') {
  return request.post('/tag/create', {
    tag_name: tag_name,
    parent_tag_id: parent_tag_id,
    extra: extra
  })
}

export async function deleteFile(file_id: number) {
  return request.delete(`/file/delete/${file_id}`)
}

export async function deleteTag(tag_id: number) {
  return request.delete(`/tag/delete/${tag_id}`)
}

export async function saveFile(file_id: number, file_name: string, extra: string, tags: number[]) {
  return request.put('/file/info/update', {
    id: file_id,
    file_name: file_name,
    extra: extra,
    tags: tags
  })
}

export async function getTagById(tag_id: number) {
  return request.get<{
    tag_name: string
    extra: string
    parent_id: number
    parent_tag_name: string
  }>('/tag/single/get', { tag_id: tag_id })
}

export async function queryFiles(query: string) {
  return request.get<TagFile.tagFile[]>('/file/search', { query: query })
}
