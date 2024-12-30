import axios from '@/libs/api.request'

export const invert = (data) => {
  return axios.request({
    url: 'invert/',
    method: 'post',
    data,
    responseType: 'arraybuffer',
    headers: {
      'Content-Type': 'multipart/form-data',
      'Access-Control-Allow-Origin': '*',
    },
  })
}