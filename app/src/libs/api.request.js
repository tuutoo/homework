import HttpRequest from '@/libs/axios'
import config from '@/config'

console.log(import.meta.env);
const baseUrl = import.meta.env.MODE === 'development' ?
  config.baseUrl.dev
  : config.baseUrl.pro

const defaultPrefix = config.baseUrl.defaultPrefix;
const axios = new HttpRequest(baseUrl, defaultPrefix)
export default axios