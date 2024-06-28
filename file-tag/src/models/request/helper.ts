import {
  REQUEST_ERROR_CODE,
  REQUEST_ERROR_MSG,
  NETWORK_ERROR_CODE,
  NETWORK_ERROR_MSG,
  ERROR_STATUS,
  NO_ERROR_SHOW_CODE,
  ERROR_MESSAGE_LIVE
} from '@/config/client'

import { type AxiosResponse } from 'axios'

type ErrorStatus = keyof typeof ERROR_STATUS

export async function handleRequestData<T = any>(error: RequestErrorStruct | null, data: any) {
  // 控制请求信息
  if (error) {
    const fail: FailRequest = {
      error,
      data: null
    }
    return fail
  }
  const success: SuccessRequest<T> = {
    error: null,
    data
  }
  return success
}

export function handleBackendError(backendResponse: Record<string, any>, config: backendConfig) {
  const { codeKey, msgKey } = config
  const error: RequestErrorStruct = {
    type: 'backend',
    code: backendResponse[codeKey],
    msg: backendResponse[msgKey]
  }
  showErrorMsg(error)
  return error
}

export function handleResponseError(Response: AxiosResponse) {
  const error: RequestErrorStruct = {
    type: 'axios',
    code: REQUEST_ERROR_CODE,
    msg: REQUEST_ERROR_MSG
  }
  // 网络错误
  if (!window.navigator.onLine) {
    Object.assign(error, { code: NETWORK_ERROR_CODE, msg: NETWORK_ERROR_MSG })
  } else {
    // 非200
    const errorCode: ErrorStatus = Response.status as ErrorStatus
    const msg = ERROR_STATUS[errorCode] || REQUEST_ERROR_MSG
    Object.assign(error, { type: 'http', code: errorCode, msg: msg })
  }
  showErrorMsg(error)
  return error
}

/** 错误消息队列 */
const errorQueue = new Map<string | number, string>([])

/** 错误消息队列方法 */

/** 添加一个消息 */
function addErrorMsg(error: RequestErrorStruct) {
  errorQueue.set(error.code, error.msg)
}
/** 移出一个 */
function deleteErrorMsg(error: RequestErrorStruct) {
  errorQueue.delete(error.code)
}
/** 查找队列中是否有 */
function hasErrorMsg(error: RequestErrorStruct) {
  return errorQueue.has(error.code)
}

/** 在页面和开发者控制台上显示错误信息 */
export function showErrorMsg(error: RequestErrorStruct) {
  /** 防止重复、无信息异常、设置不显示信息 显示  */
  if (!error.msg || NO_ERROR_SHOW_CODE.includes(error.code) || hasErrorMsg(error)) return
  addErrorMsg(error)
  window.console.warn(error.code, error.msg)
  window.$message.error(error.msg, { duration: ERROR_MESSAGE_LIVE })
  setTimeout(() => {
    deleteErrorMsg(error)
  }, ERROR_MESSAGE_LIVE)
}
