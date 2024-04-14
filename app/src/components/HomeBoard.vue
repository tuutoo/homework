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

const apiUrl = import.meta.env.VITE_API_URL
console.log(apiUrl)
const errorMessage = ref('')

if (!apiUrl) {
  errorMessage.value = 'API URL 未设置。请在 .env 文件中设置 VITE_API_URL。'
}

const imgSrc = ref('')
const imgReturn = ref('')
const infoText = ref('')
const fileInput = ref<HTMLInputElement | null>(null)
const originalFileName = ref('')
const ai_cutting = ref(true)
const tarImgWidth = ref(0)
const tarImgHeight = ref(0)
const cropWidth = ref(0)

const loadImageSize = () => {
  const img = new Image() // 创建一个Image对象
  img.onload = () => {
    // 图片加载完成时触发
    tarImgWidth.value = img.width // 更新宽度
    tarImgHeight.value = img.height // 更新高度
    console.log(`Image Size: ${img.width} x ${img.height}`) // 打印图片尺寸
    cropWidth.value = Math.floor((img.width / img.height) * 400)
  }
  img.src = imgReturn.value // 设置图片的src为imgReturn的值，开始加载图片
}

const cropper_src = ref<{
  getCropBlob: (callback: (data: Blob) => void) => void
} | null>(null)

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
    const blob = new Blob([data], { type: 'image/png' })
    imgReturn.value = URL.createObjectURL(blob)
    infoText.value = '文件处理成功'
    loadImageSize() // 加载图片并获取尺寸
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
  aLink.download = `${fileNameWithoutExt}_cut.png`
  cropper_src.value?.getCropBlob((data: Blob) => {
    aLink.href = window.URL.createObjectURL(data)
    aLink.click()
  })
}

const downloadBlobImage = () => {
  const aLink = document.createElement('a') // 创建一个a元素
  const fileNameWithoutExt = originalFileName.value.split('.').slice(0, -1).join('.') // 获取文件名，去掉扩展名
  aLink.download = `${fileNameWithoutExt}_reversed.png` // 设置下载的文件名
  aLink.href = imgReturn.value // 将a元素的href属性设置为图片的URL
  aLink.click() // 模拟点击，触发下载
}

const downloadCropImage = () => {
  const aLink = document.createElement('a')
  const fileNameWithoutExt = originalFileName.value.split('.').slice(0, -1).join('.')
  aLink.download = `${fileNameWithoutExt}_reversed.png`
  cropper_target.value?.getCropBlob((data: Blob) => {
    aLink.href = window.URL.createObjectURL(data)
    aLink.click()
  })
}

const printImage = (imageType: string) => {
  if (imageType === 'original') {
    cropper_src.value?.getCropBlob(async (data: Blob) => {
      printFromBlob(data)
    })
  } else if (imageType === 'target') {
    cropper_target.value?.getCropBlob(async (data: Blob) => {
      printFromBlob(data)
    })
  } else if (imageType === 'src') {
    printFromURL(imgSrc.value)
  } else if (imageType === 'return') {
    printFromURL(imgReturn.value)
  }
}

function printFromBlob(blob: Blob) {
  const imgURL = window.URL.createObjectURL(blob)
  printFromURL(imgURL)
}

function printFromURL(imgURL: string) {
  const img = new Image()
  img.src = imgURL

  img.onload = () => {
    const windowPrint = window.open('', '_blank')
    windowPrint?.document.write('<img src="' + img.src + '" style="width: 100%;">')
    windowPrint?.document.close()
    windowPrint?.focus()
    windowPrint?.print()
  }
}

onBeforeUnmount(() => {
  clearPreviousResults() // 组件卸载时清理资源
})
</script>

<template>
  <div class="container">
    <n-card v-if="!errorMessage" :bordered="false" title="请上传需要反色处理的图片">
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
          <n-button v-if="imgSrc" @click="printImage('src')"
            ><template #icon>
              <n-icon>
                <print-icon />
              </n-icon> </template
            >打印全图(原图)</n-button
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
            <n-button v-if="imgReturn" @click="downloadBlobImage"
              ><template #icon>
                <n-icon>
                  <download-icon />
                </n-icon> </template
              >下载全图(反色)</n-button
            >
            <n-button v-if="imgReturn" @click="printImage('return')"
              ><template #icon>
                <n-icon>
                  <print-icon />
                </n-icon> </template
              >打印全图(反色)</n-button
            >
            <n-button v-if="imgReturn" @click="downloadCropImage"
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
              autoCrop
              :autoCropWidth="cropWidth"
              autoCropHeight="400"
              centerBox
              outputType="png"
            ></VueCropper>
          </div>
        </n-space>
      </div>
    </n-card>
    <div v-else class="error-message">
      <p>{{ errorMessage }}</p>
    </div>
  </div>
</template>

<style scoped>
.container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  width: 85%;
}

.crop-container {
  width: 100%;
  height: 400px;
}
</style>
