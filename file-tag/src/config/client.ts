export const NO_ERROR_SHOW_CODE: (string | number)[] = [999]

export const ERROR_MESSAGE_LIVE = 3000

export const REQUEST_ERROR_CODE = 'DEFAULT'

export const REQUEST_ERROR_MSG = '请求发生错误'

export const NETWORK_ERROR_CODE = 'NET_ERROR'

export const NETWORK_ERROR_MSG = '网络错误'

export const TIME_OUT_CODE = 'ECONNABORTED'

export const TIME_OUT_MSG = '请求超时'

export const TIME_OUT = 30 * 1000

export const ERROR_STATUS = {
  400: '400: 请求出现语法错误',
  401: '401: 用户未授权',
  403: '403: 服务器拒绝访问',
  404: '404: 请求的资源不存在',
  405: '405: 请求方法未允许',
  408: '408: 网络请求超时',
  500: '500: 服务器内部错误',
  501: '501: 服务器未实现请求功能',
  502: '502: 错误网关',
  503: '503: 服务不可用',
  504: '504: 网关超时',
  505: '505: http版本不支持该请求',
  [REQUEST_ERROR_CODE]: REQUEST_ERROR_MSG
}
