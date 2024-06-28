import axios, { type AxiosResponse } from 'axios'
import { type AxiosInstance, type AxiosRequestConfig } from 'axios'
import { handleRequestData, handleBackendError, handleResponseError } from './helper'

export default class DefaultAxiosInstance {
  axiosInstance: AxiosInstance
  backendConfig: backendConfig

  constructor(
    axiosConfig: AxiosRequestConfig,
    backendConfig: backendConfig = {
      codeKey: 'code',
      dataKey: 'data',
      msgKey: 'msg',
      successCode: 200
    }
  ) {
    this.axiosInstance = axios.create(axiosConfig)
    this.backendConfig = backendConfig
    this.axiosInterceptor()
  }

  axiosInterceptor() {
    this.axiosInstance.interceptors.request.use(async (config) => {
      return config
    })
    this.axiosInstance.interceptors.response.use((async (response: AxiosResponse<any, any>) => {
      const { status } = response
      if (status === 200 || status < 300 || status === 304) {
        const backendData = response.data
        const { successCode, codeKey, dataKey } = this.backendConfig
        if (backendData[codeKey] === successCode) {
          return handleRequestData(null, backendData[dataKey])
        }
        const error = handleBackendError(backendData, this.backendConfig)
        return handleRequestData(error, null)
      }
      const error = handleResponseError(response)
      return handleRequestData(error, null)
    }) as unknown as (response: AxiosResponse<any, any>) => Promise<AxiosResponse<any, any>>)
  }
}
