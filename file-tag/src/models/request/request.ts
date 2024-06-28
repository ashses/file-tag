// get、post方法
import { type AxiosInstance, type AxiosRequestConfig } from 'axios'
import DefaultAxiosInstance from './instance'

type requestMethod = 'get' | 'post' | 'put' | 'delete'

/** axios实例参数 */
interface axiosParam {
  url: string
  method?: requestMethod
  data?: any
  axiosConfig?: AxiosRequestConfig
}

export function CreateAxiosInstance(config: AxiosRequestConfig, backendConfig?: backendConfig) {
  const AxiosInstance = new DefaultAxiosInstance(config, backendConfig)

  async function asyncRequest<T>(param: axiosParam): Promise<RequestData<T>> {
    const { url } = param
    const method = param.method || 'get'
    const { axiosInstance } = AxiosInstance

    const res = (await getResponse({
      axiosInstance,
      method,
      url,
      data: param.data,
      axiosConfig: param.axiosConfig
    })) as RequestData<T>
    return res
  }
  /** 实例请求方法：get、post、put、delete
   * url: 后端接口
   * data?: 给后端传递的数据
   * axiosConfig?: 给axios实例配置
   */
  /** get请求 */
  function get<T>(url: string, data?: any, axiosConfig?: AxiosRequestConfig) {
    return asyncRequest<T>({ url, method: 'get', data: data, axiosConfig: axiosConfig })
  }

  /** post请求 */
  function post<T>(url: string, data?: any, axiosConfig?: AxiosRequestConfig) {
    return asyncRequest<T>({ url, method: 'post', data: data, axiosConfig: axiosConfig })
  }

  /** put请求(更新) */
  function put<T>(url: string, data?: any, axiosConfig?: AxiosRequestConfig) {
    return asyncRequest<T>({ url, method: 'put', data: data, axiosConfig: axiosConfig })
  }

  /** 删除数据 */
  function methodDelete<T>(url: string, data?: any, axiosConfig?: AxiosRequestConfig) {
    return asyncRequest<T>({ url, method: 'delete', data: data, axiosConfig: axiosConfig })
  }

  return {
    get,
    post,
    put,
    delete: methodDelete
  }
}

async function getResponse(params: {
  axiosInstance: AxiosInstance
  method: requestMethod
  url: string
  data?: any
  axiosConfig?: AxiosRequestConfig
}) {
  const { axiosInstance, method, url, data, axiosConfig } = params
  let res: any
  if (method.toLowerCase() === 'get') {
    res = await axiosInstance.get(url, { ...axiosConfig, params: data })
  } else if (method.toLowerCase() === 'delete') {
    res = await axiosInstance.delete(url, { ...axiosConfig, params: data })
  } else {
    res = await axiosInstance[method](url, data, axiosConfig)
  }
  return res
}
