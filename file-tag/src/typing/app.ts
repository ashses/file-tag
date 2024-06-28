interface Window {
  $loadingBar: import('naive-ui').LoadingBarProviderInst
  $dialog: import('naive-ui').DialogProviderInst
  $message: import('naive-ui').MessageProviderInst
  $notification: import('naive-ui').NotificationProviderInst
}

/** 错误信息 */
interface RequestErrorStruct {
  type: 'axios' | 'http' | 'backend'
  code: number | string
  msg: string
}

interface SuccessRequest<T = any> {
  error: null
  data: T
}

interface FailRequest {
  error: RequestErrorStruct
  data: null
}

/** Request请求体 */
type RequestData<T = any> = SuccessRequest<T> | FailRequest

interface VerticalTable {
  rowName: string
  rowValue: any
}

type contentType = 'application/json' | 'application/x-www-form-urlencoded' | 'multipart/form-data'
