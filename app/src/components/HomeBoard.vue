<script setup lang="ts">
import { onBeforeUnmount, ref } from 'vue'
import { NCard, NButton, NSpace, NIcon, NCheckbox } from 'naive-ui'
import axios from 'axios'
import 'vue-cropper/dist/index.css'
import { VueCropper } from 'vue-cropper'
import {
  DownloadSharp as DownloadIcon,
  FileUploadSharp as UploadIcon,
  LocalPrintshopSharp as PrintIcon,
} from '@vicons/material'

const apiUrl = import.meta.env.VITE_API_URL || 'https://homework.sohot.app/api/invert/'

const imgSrc = ref('')
const imgReturn = ref('')
const infoText = ref('')
const fileInput = ref<HTMLInputElement | null>(null)
const originalFileName = ref('')
const ai_cutting = ref(true)

const cropper_src = ref<{ getCropBlob: (callback: (data: Blob) => void) => void } | null>(
  null
)

const cropper_target = ref<{
  getCropBlob: (callback: (data: Blob) => void) => void
} | null>(null)

const clearPreviousResults = () => {
  if (imgSrc.value) {
    URL.revokeObjectURL(imgSrc.value)
    imgSrc.value = ''
  }
  if (imgReturn.value) {
    URL.revokeObjectURL(imgReturn.value)
    imgReturn.value = ''
  }
  infoText.value = ''
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

const clickInputFile = () => {
  fileInput?.value?.click()
}

const fetchRequest = async (formData: FormData) => {
  infoText.value = '正在处理文件中...'
  try {
    const { data } = await axios.post(apiUrl, formData, {
      responseType: 'arraybuffer',
      headers: {
        'Content-Type': 'multipart/form-data',
        'Access-Control-Allow-Origin': '*',
      },
    })
    const blob = new Blob([data], { type: 'image/jpeg' })
    imgReturn.value = URL.createObjectURL(blob)
    infoText.value = '文件处理成功'
  } catch (error) {
    infoText.value = '文件处理失败'
  }
}

const fileChanged = (e: Event) => {
  const target = e.target as HTMLInputElement
  const file = target.files ? target.files[0] : null
  if (!file) {
    return
  }

  originalFileName.value = file.name // 保存原始文件名
  clearPreviousResults()
  imgSrc.value = URL.createObjectURL(file)
  const formData = new FormData()
  formData.append('file', file)
  formData.append('ai', ai_cutting.value.toString())
  fetchRequest(formData)
}

const downloadSrcImage = () => {
  const aLink = document.createElement('a')
  const fileNameWithoutExt = originalFileName.value.split('.').slice(0, -1).join('.')
  aLink.download = `${fileNameWithoutExt}_cut.jpeg`
  cropper_src.value?.getCropBlob((data: Blob) => {
    aLink.href = window.URL.createObjectURL(data)
    aLink.click()
    window.URL.revokeObjectURL(aLink.href) // 释放创建的URL
  })
}

const downloadImage = () => {
  const aLink = document.createElement('a')
  const fileNameWithoutExt = originalFileName.value.split('.').slice(0, -1).join('.')
  aLink.download = `${fileNameWithoutExt}_reversed.jpeg`
  // // 获取当前时间并格式化为年月日时分秒
  // const now = new Date();
  // const timestamp = now.getFullYear().toString() +
  //                   (now.getMonth() + 1).toString().padStart(2, '0') +
  //                   now.getDate().toString().padStart(2, '0') + '_' +
  //                   now.getHours().toString().padStart(2, '0') +
  //                   now.getMinutes().toString().padStart(2, '0') +
  //                   now.getSeconds().toString().padStart(2, '0');

  // aLink.download = `${fileNameWithoutExt}_export_${timestamp}.jpeg`;
  cropper_target.value?.getCropBlob((data: Blob) => {
    aLink.href = window.URL.createObjectURL(data)
    aLink.click()
    window.URL.revokeObjectURL(aLink.href) // 释放创建的URL
  })
}

const printImage = (imageType: string) => {
  const target = imageType === 'original' ? cropper_src : cropper_target
  target.value?.getCropBlob(async (data: Blob) => {
    const imgSrc = window.URL.createObjectURL(data)
    const img = new Image()
    img.src = imgSrc
    img.onload = () => {
      const windowPrint = window.open('', '_blank')
      windowPrint?.document.write('<img src="' + img.src + '" style="width: 100%;">')
      windowPrint?.document.close()
      windowPrint?.focus()
      windowPrint?.print()
      window.URL.revokeObjectURL(imgSrc) // 释放创建的URL
    }
  })
}

onBeforeUnmount(() => {
  clearPreviousResults() // 组件卸载时清理资源
})
</script>

<template>
  <div class="container">
    <n-card title="请上传需要反色处理的图片">
      <n-space vertical>
        <n-space>
          <n-button @click="clickInputFile">
            <template #icon>
              <n-icon>
                <upload-icon />
              </n-icon>
            </template>
            上传文件</n-button
          >
          <n-checkbox v-model:checked="ai_cutting"> AI Cutting </n-checkbox>
          <n-button v-if="imgSrc" @click="downloadSrcImage"
            ><template #icon>
              <n-icon>
                <download-icon />
              </n-icon> </template
            >下载裁切图(原图)</n-button
          >
          <n-button v-if="imgSrc" @click="printImage('original')"
            ><template #icon>
              <n-icon>
                <print-icon />
              </n-icon> </template
            >打印裁切图(原图)</n-button
          >
        </n-space>
        <div>
          <input type="file" ref="fileInput" @change="fileChanged" hidden />
          <div class="crop-container">
            <VueCropper
              ref="cropper_src"
              :img="imgSrc"
              autoCrop
              centerBox
              outputType="png"
            ></VueCropper>
          </div>
          <div class="content">
            <p>{{ infoText }}</p>
          </div>
        </div>
      </n-space>
      <div class="finalResult">
        <n-space vertical>
          <n-space>
            <n-button v-if="imgReturn" @click="downloadImage"
              ><template #icon>
                <n-icon>
                  <download-icon />
                </n-icon> </template
              >下载裁切图(反色)</n-button
            >
            <n-button v-if="imgReturn" @click="printImage('target')"
              ><template #icon>
                <n-icon>
                  <print-icon />
                </n-icon> </template
              >打印裁切图(反色)</n-button
            >
          </n-space>
          <div class="crop-container">
            <VueCropper
              ref="cropper_target"
              :img="imgReturn"
              :autoCrop="!ai_cutting"
              centerBox
              outputType="png"
            ></VueCropper>
          </div>
        </n-space>
      </div>
    </n-card>
  </div>
</template>

<style scoped>
.container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  width: 100%;
}

.crop-container {
  width: 100%;
  height: 400px;
}
</style>
