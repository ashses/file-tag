import { CreateAxiosInstance } from './request'
import { BASE_URL } from '@/config/service'

export const request = CreateAxiosInstance({ baseURL: BASE_URL })
